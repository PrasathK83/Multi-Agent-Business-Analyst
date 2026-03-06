
import pandas as pd
from typing import Tuple
from pathlib import Path


class DataValidator:
    """Validates uploaded data and user inputs"""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: list) -> Tuple[bool, str]:
        """Validate file extension"""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        return True, "Valid file extension"
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int) -> Tuple[bool, str]:
        """Validate file size in MB"""
        size_mb = file_size / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return False, f"File too large ({size_mb:.2f} MB). Maximum: {max_size_mb} MB"
        
        return True, f"File size OK ({size_mb:.2f} MB)"
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate DataFrame structure"""
        if df is None:
            return False, "DataFrame is None"
        
        if df.empty:
            return False, "DataFrame is empty"
        
        if len(df.columns) == 0:
            return False, "No columns found"
        
        if len(df) == 0:
            return False, "No rows found"
        
        return True, "DataFrame is valid"
    
    @staticmethod
    def detect_data_issues(df: pd.DataFrame) -> dict:
        """Detect common data quality issues"""
        issues = {
            'missing_values': {},
            'duplicates': 0,
            'data_types': {},
            'warnings': []
        }
        
        # Missing values
        missing = df.isnull().sum()
        issues['missing_values'] = {
            col: int(count) for col, count in missing.items() if count > 0
        }
        
        # Duplicates
        issues['duplicates'] = int(df.duplicated().sum())
        
        # Data types
        issues['data_types'] = {
            col: str(dtype) for col, dtype in df.dtypes.items()
        }
        
        # Warnings
        if len(issues['missing_values']) > 0:
            total_missing = sum(issues['missing_values'].values())
            issues['warnings'].append(
                f"Found {total_missing} missing values across {len(issues['missing_values'])} columns"
            )
        
        if issues['duplicates'] > 0:
            issues['warnings'].append(
                f"Found {issues['duplicates']} duplicate rows"
            )
        
        # Check for very high cardinality (potential ID columns)
        for col in df.columns:
            if df[col].nunique() == len(df) and len(df) > 100:
                issues['warnings'].append(
                    f"Column '{col}' has unique values (possible ID field)"
                )
        
        return issues
    
    @staticmethod
    def validate_column_exists(df: pd.DataFrame, column: str) -> Tuple[bool, str]:
        """Check if column exists in DataFrame"""
        if column not in df.columns:
            return False, f"Column '{column}' not found. Available: {list(df.columns)}"
        
        return True, "Column exists"
    
    @staticmethod
    def validate_numeric_column(df: pd.DataFrame, column: str) -> Tuple[bool, str]:
        """Check if column is numeric"""
        if column not in df.columns:
            return False, f"Column '{column}' not found"
        
        if not pd.api.types.is_numeric_dtype(df[column]):
            return False, f"Column '{column}' is not numeric (type: {df[column].dtype})"
        
        return True, "Column is numeric"
    
    @staticmethod
    def validate_categorical_column(df: pd.DataFrame, column: str, max_unique: int = 50) -> Tuple[bool, str]:
        """Check if column is suitable for categorical analysis"""
        if column not in df.columns:
            return False, f"Column '{column}' not found"
        
        unique_count = df[column].nunique()
        
        if unique_count > max_unique:
            return False, f"Too many unique values ({unique_count}) for categorical analysis"
        
        return True, f"Valid categorical column ({unique_count} unique values)"


class QueryValidator:
    """Validates natural language queries"""
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, str]:
        """Basic query validation"""
        if not query or query.strip() == "":
            return False, "Query cannot be empty"
        
        if len(query) < 3:
            return False, "Query too short (minimum 3 characters)"
        
        if len(query) > 500:
            return False, "Query too long (maximum 500 characters)"
        
        return True, "Valid query"
    
    @staticmethod
    def is_safe_query(query: str) -> Tuple[bool, str]:
        """Check for potentially harmful operations"""
        dangerous_keywords = [
            'drop table', 'delete from', 'truncate', 
            'insert into', 'update set', 'exec',
            'system', 'os.', 'eval(', 'exec('
        ]
        
        query_lower = query.lower()
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                return False, f"Query contains potentially dangerous operation: '{keyword}'"
        
        return True, "Query is safe"
