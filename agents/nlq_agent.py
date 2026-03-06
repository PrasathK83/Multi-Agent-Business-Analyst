"""Natural Language Query agent decoupled from Streamlit UI."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

import pandas as pd

try:
    from langchain_core.caches import BaseCache as _LangChainBaseCache  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover - fallback for very old LangChain versions
    _LangChainBaseCache = None

    class BaseCache:  # type: ignore
        """Fallback placeholder to satisfy ChatGroq forward references."""

        pass
else:
    from langchain_core.callbacks import Callbacks as _LangChainCallbacks
    from langchain_core.language_models import base as _lc_base_module
    from langchain_core.outputs import LLMResult as _LangChainLLMResult

    setattr(_lc_base_module, "BaseCache", _LangChainBaseCache)
    setattr(_lc_base_module, "Callbacks", _LangChainCallbacks)
    setattr(_lc_base_module, "LLMResult", _LangChainLLMResult)

    try:  # Ensure ChatGroq module sees the resolved forward references
        import langchain_groq.chat_models as _groq_chat_module

        setattr(_groq_chat_module, "BaseCache", _LangChainBaseCache)
        setattr(_groq_chat_module, "Callbacks", _LangChainCallbacks)
        setattr(_groq_chat_module, "LLMResult", _LangChainLLMResult)
    except ImportError:
        pass

    BaseCache = _LangChainBaseCache  # re-export for type checking tools
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from pandasai import SmartDataframe
from pandasai.llm import LangchainLLM

from utils.config import GROQ_API_KEY, GROQ_MODEL, LANGCHAIN_TEMPERATURE
from utils.validators import QueryValidator
from utils.session_manager import SessionManager


class NLQAgent:
    """
    Natural Language Query Agent - Third agent in the pipeline
    Converts natural language questions to executable Pandas operations
    """
    
    def __init__(self, session: SessionManager):
        self.session = session
        self.validator = QueryValidator()
        self.llm = None
        self.smart_df = None
        self.llm_error: Optional[str] = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for query processing"""
        if not GROQ_API_KEY:
            self.llm_error = "GROQ_API_KEY not configured"
            return
        
        try:
            # Work around Pydantic forward-ref issue in ChatGroq
            ChatGroq.model_rebuild()

            # Initialize Groq LLM via LangChain
            self.llm = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name=GROQ_MODEL,
                temperature=LANGCHAIN_TEMPERATURE
            )
        except Exception as exc:  # pragma: no cover - defensive
            self.llm_error = f"Error initializing LLM: {exc}"
    
    def _initialize_smart_dataframe(self, df: pd.DataFrame):
        """
        Initialize PandasAI SmartDataframe
        
        Args:
            df: pandas DataFrame
        """
        try:
            # Wrap LangChain LLM for PandasAI
            langchain_llm = LangchainLLM(self.llm)
            
            # Create SmartDataframe
            self.smart_df = SmartDataframe(
                df,
                config={
                    "llm": langchain_llm,
                    "verbose": False,
                    "enforce_privacy": True,
                    "enable_cache": False
                }
            )
        except Exception:
            self.smart_df = None
    
    def parse_query_with_llm(self, query: str, df: pd.DataFrame) -> Tuple[bool, str, Any]:
        """
        Parse natural language query using LLM
        
        Args:
            query: Natural language question
            df: pandas DataFrame
            
        Returns:
            Tuple of (success, explanation, result)
        """
        try:
            # Create context about the dataset
            context = self._create_dataset_context(df)
            
            # Create prompt for query interpretation
            prompt = PromptTemplate(
                input_variables=["query", "context"],
                template="""You are a data analyst. Given the following dataset information and a user query, 
provide a clear explanation of what analysis should be performed and what the expected result means.

Dataset Context:
{context}

User Query: {query}

Provide:
1. What the query is asking for
2. What columns/operations are relevant
3. A brief explanation of the expected result

Format your response as JSON with keys: "interpretation", "relevant_columns", "explanation"
"""
            )
            
            # Get LLM interpretation
            chain = prompt | self.llm
            response = chain.invoke({"query": query, "context": context})
            
            # Parse response
            try:
                interpretation = json.loads(response.content)
            except:
                interpretation = {
                    "interpretation": response.content,
                    "relevant_columns": [],
                    "explanation": "Processing query..."
                }
            
            return True, interpretation.get("explanation", ""), interpretation
            
        except Exception as exc:
            return False, f"Error parsing query: {exc}", None
    
    def _create_dataset_context(self, df: pd.DataFrame) -> str:
        """
        Create context string about dataset for LLM
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Context string
        """
        context = f"""
Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns

Columns and Types:
{df.dtypes.to_string()}

Numeric Columns: {list(df.select_dtypes(include=['number']).columns)}
Categorical Columns: {list(df.select_dtypes(include=['object']).columns)}

Sample Data:
{df.head(3).to_string()}
"""
        return context
    
    def execute_query_with_pandasai(self, query: str, df: pd.DataFrame) -> Tuple[bool, Any, str]:
        """
        Execute query using PandasAI
        
        Args:
            query: Natural language question
            df: pandas DataFrame
            
        Returns:
            Tuple of (success, result, explanation)
        """
        try:
            # Initialize SmartDataframe if not already done
            if self.smart_df is None:
                self._initialize_smart_dataframe(df)
            
            # Execute query
            result = self.smart_df.chat(query)
            
            # Generate explanation
            explanation = f"Executed query: '{query}'"
            
            return True, result, explanation
            
        except Exception as exc:
            return False, None, f"Error executing query: {exc}"
    
    def execute_query_fallback(self, query: str, df: pd.DataFrame) -> Tuple[bool, Any, str]:
        """
        Fallback query execution using direct Pandas operations
        Handles common query patterns
        
        Args:
            query: Natural language question
            df: pandas DataFrame
            
        Returns:
            Tuple of (success, result, explanation)
        """
        query_lower = query.lower()
        
        try:
            # Pattern 1: Count/Sum operations
            if any(word in query_lower for word in ['how many', 'count', 'total number']):
                # Try to find column name in query
                for col in df.columns:
                    if col.lower() in query_lower:
                        if 'unique' in query_lower or 'distinct' in query_lower:
                            result = df[col].nunique()
                            explanation = f"Counted unique values in '{col}': {result}"
                        else:
                            result = df[col].count()
                            explanation = f"Counted non-null values in '{col}': {result}"
                        return True, result, explanation
                
                # Default: total rows
                result = len(df)
                explanation = f"Total number of rows: {result}"
                return True, result, explanation
            
            # Pattern 2: Average/Mean
            elif any(word in query_lower for word in ['average', 'mean']):
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in query_lower:
                        result = df[col].mean()
                        explanation = f"Average of '{col}': {result:.2f}"
                        return True, result, explanation
            
            # Pattern 3: Maximum
            elif 'max' in query_lower or 'highest' in query_lower or 'largest' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in query_lower:
                        result = df[col].max()
                        explanation = f"Maximum value in '{col}': {result}"
                        return True, result, explanation
            
            # Pattern 4: Minimum
            elif 'min' in query_lower or 'lowest' in query_lower or 'smallest' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in query_lower:
                        result = df[col].min()
                        explanation = f"Minimum value in '{col}': {result}"
                        return True, result, explanation
            
            # Pattern 5: Sum
            elif 'sum' in query_lower or 'total' in query_lower:
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in query_lower:
                        result = df[col].sum()
                        explanation = f"Sum of '{col}': {result:,.2f}"
                        return True, result, explanation
            
            # Pattern 6: Group by / by category
            elif 'by' in query_lower or 'per' in query_lower:
                # Find categorical column
                cat_col = None
                num_col = None
                
                for col in df.select_dtypes(include=['object']).columns:
                    if col.lower() in query_lower:
                        cat_col = col
                        break
                
                for col in df.select_dtypes(include=['number']).columns:
                    if col.lower() in query_lower:
                        num_col = col
                        break
                
                if cat_col:
                    if num_col:
                        if 'sum' in query_lower:
                            result = df.groupby(cat_col)[num_col].sum()
                        elif 'average' in query_lower or 'mean' in query_lower:
                            result = df.groupby(cat_col)[num_col].mean()
                        else:
                            result = df.groupby(cat_col)[num_col].count()
                    else:
                        result = df[cat_col].value_counts()
                    
                    explanation = f"Grouped analysis by '{cat_col}'"
                    return True, result, explanation
            
            # If no pattern matched
            return False, None, "Could not parse query. Please try rephrasing or be more specific."
            
        except Exception as exc:
            return False, None, f"Error executing query: {exc}"
    
    def process_query(self, query: str, df: pd.DataFrame) -> Tuple[bool, Any, str]:
        """
        Main query processing method - tries multiple approaches
        
        Args:
            query: Natural language question
            df: pandas DataFrame
            
        Returns:
            Tuple of (success, result, explanation)
        """
        # Validate query
        is_valid, msg = self.validator.validate_query(query)
        if not is_valid:
            return False, None, msg
        
        is_safe, msg = self.validator.is_safe_query(query)
        if not is_safe:
            return False, None, msg
        
        # Try PandasAI first
        if self.llm:
            success, result, explanation = self.execute_query_with_pandasai(query, df)
            if success:
                return True, result, explanation
        
        # Fallback to pattern matching
        success, result, explanation = self.execute_query_fallback(query, df)
        
        return success, result, explanation
    
    def serialize_result(self, result: Any) -> Dict[str, Any]:
        if isinstance(result, pd.DataFrame):
            return {
                'type': 'dataframe',
                'data': result.to_dict(orient='records'),
                'columns': list(result.columns)
            }
        if isinstance(result, pd.Series):
            return {
                'type': 'series',
                'data': result.to_dict(),
                'name': result.name
            }
        if isinstance(result, (int, float)):
            return {'type': 'scalar', 'data': result}
        return {'type': 'text', 'data': str(result)}

    def execute(self, query: str) -> Dict[str, Any]:
        if self.llm_error:
            return {'success': False, 'message': self.llm_error}

        df = self.session.get_dataframe('current')
        if df is None:
            return {'success': False, 'message': 'No data available. Please upload data first.'}

        success, result, explanation = self.process_query(query, df)
        if not success:
            return {'success': False, 'message': explanation}

        self.session.add_query(query, result, explanation)

        if isinstance(result, (int, float)):
            insight = f"Query '{query}' returned: {result}"
        elif isinstance(result, (pd.DataFrame, pd.Series)):
            insight = f"Query '{query}' returned {len(result)} results"
        else:
            insight = f"Query '{query}' completed successfully"

        self.session.add_insight(insight, 'query')
        self.session.update_agent_status('nlq_ready', True)

        return {
            'success': True,
            'explanation': explanation,
            'result': self.serialize_result(result)
        }
