from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from utils.session_manager import SessionManager

class CleaningAgent:
    
    
    def __init__(self, session: SessionManager):
        self.session = session
    
    def analyze_cleaning_needs(self, df: pd.DataFrame) -> Dict:
       
        needs = {
            'has_missing': df.isnull().sum().sum() > 0,
            'has_duplicates': df.duplicated().sum() > 0,
            'missing_by_column': {},
            'duplicate_count': int(df.duplicated().sum())
        }
        missing = df.isnull().sum()
        needs['missing_by_column'] = {
            col: int(count) for col, count in missing.items() if count > 0
        }
    
        return needs
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str, columns: List[str] = None) -> pd.DataFrame:
        """
        Handle missing values based on strategy
        
        Args:
            df: pandas DataFrame
            strategy: Strategy to use ('mean', 'median', 'mode', 'ffill', 'bfill', 'drop')
            columns: Specific columns to apply strategy (None = all columns)
            
        Returns:
            Cleaned DataFrame
        """
        df_cleaned = df.copy()
        
        if columns is None:
            columns = df_cleaned.columns[df_cleaned.isnull().any()].tolist()
        
        if strategy == 'drop':
            # Drop rows with any missing values in specified columns
            df_cleaned = df_cleaned.dropna(subset=columns)
            self.session.add_cleaning_log(
                "Missing Values",
                f"Dropped rows with missing values in {len(columns)} columns"
            )
        
        else:
            for col in columns:
                if df_cleaned[col].isnull().sum() == 0:
                    continue
                
                # Only apply numeric strategies to numeric columns
                if strategy in ['mean', 'median'] and not pd.api.types.is_numeric_dtype(df_cleaned[col]):
                    # Use mode for non-numeric
                    fill_value = df_cleaned[col].mode()[0] if len(df_cleaned[col].mode()) > 0 else None
                    strategy_used = 'mode'
                else:
                    if strategy == 'mean':
                        fill_value = df_cleaned[col].mean()
                        strategy_used = 'mean'
                    elif strategy == 'median':
                        fill_value = df_cleaned[col].median()
                        strategy_used = 'median'
                    elif strategy == 'mode':
                        fill_value = df_cleaned[col].mode()[0] if len(df_cleaned[col].mode()) > 0 else None
                        strategy_used = 'mode'
                    elif strategy == 'ffill':
                        df_cleaned[col] = df_cleaned[col].fillna(method='ffill')
                        strategy_used = 'forward fill'
                        continue
                    elif strategy == 'bfill':
                        df_cleaned[col] = df_cleaned[col].fillna(method='bfill')
                        strategy_used = 'backward fill'
                        continue
                    else:
                        continue
                
                if fill_value is not None:
                    df_cleaned[col] = df_cleaned[col].fillna(fill_value)
                
                self.session.add_cleaning_log(
                    "Missing Values",
                    f"Filled {col} using {strategy_used}"
                )
        
        return df_cleaned
    
    def handle_duplicates(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """
        Handle duplicate rows based on strategy
        
        Args:
            df: pandas DataFrame
            strategy: Strategy to use ('drop', 'first', 'last', 'keep')
            
        Returns:
            Cleaned DataFrame
        """
        df_cleaned = df.copy()
        
        if strategy == 'keep':
            # Do nothing
            self.session.add_cleaning_log(
                "Duplicates",
                "Kept all duplicate rows"
            )
        elif strategy == 'drop':
            # Remove all duplicates
            initial_rows = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates(keep=False)
            removed = initial_rows - len(df_cleaned)
            self.session.add_cleaning_log(
                "Duplicates",
                f"Removed all {removed} duplicate rows"
            )
        else:
            # Keep first or last occurrence
            initial_rows = len(df_cleaned)
            df_cleaned = df_cleaned.drop_duplicates(keep=strategy)
            removed = initial_rows - len(df_cleaned)
            self.session.add_cleaning_log(
                "Duplicates",
                f"Removed {removed} duplicate rows (kept {strategy})"
            )
        
        return df_cleaned
    
    def apply_cleaning(self, df: pd.DataFrame, choices: Dict) -> pd.DataFrame:
        """
        Apply cleaning operations based on user choices
        
        Args:
            df: pandas DataFrame
            choices: Dictionary of user choices
            
        Returns:
            Cleaned DataFrame
        """
        df_cleaned = df.copy()
        
        # Handle missing values
        if choices['clean_missing'] and choices['missing_strategy']:
            df_cleaned = self.handle_missing_values(
                df_cleaned,
                choices['missing_strategy'],
                choices['missing_columns']
            )
        
        # Handle duplicates
        if choices['clean_duplicates'] and choices['duplicate_strategy']:
            df_cleaned = self.handle_duplicates(
                df_cleaned,
                choices['duplicate_strategy']
            )
        
        return df_cleaned
    
    def calculate_summary(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> Dict[str, float]:
        rows_removed = len(df_before) - len(df_after)
        missing_before = float(df_before.isnull().sum().sum())
        missing_after = float(df_after.isnull().sum().sum())

        return {
            'rows_removed': rows_removed,
            'missing_before': missing_before,
            'missing_after': missing_after,
            'final_rows': len(df_after)
        }

    def execute(self, choices: Dict) -> Dict[str, any]:
        df = self.session.get_dataframe('current')
        if df is None:
            return {'success': False, 'message': 'No data available. Please upload data first.'}

        needs = self.analyze_cleaning_needs(df)
        if not needs['has_missing'] and not needs['has_duplicates']:
            self.session.set_dataframe(df, 'cleaned')
            self.session.update_agent_status('cleaning_complete', True)
            return {
                'success': True,
                'message': 'Data already clean. No operations performed.',
                'summary': self.calculate_summary(df, df)
            }

        df_cleaned = self.apply_cleaning(df, choices)
        self.session.set_dataframe(df_cleaned, 'cleaned')
        self.session.set_dataframe(df_cleaned, 'current')
        self.session.update_agent_status('cleaning_complete', True)

        summary = self.calculate_summary(df, df_cleaned)
        return {
            'success': True,
            'message': 'Data cleaning completed successfully.',
            'summary': summary,
            'needs': needs,
            'cleaning_log': self.session.state.cleaning_log
        }

    def get_cleaning_needs(self) -> Dict:
        df = self.session.get_dataframe('current')
        if df is None:
            return {'has_data': False}
        needs = self.analyze_cleaning_needs(df)
        needs['has_data'] = True
        return needs
