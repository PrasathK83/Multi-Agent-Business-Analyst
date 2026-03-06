"""Agent handling file ingestion and validation."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import pandas as pd

from utils.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB
from utils.session_manager import SessionManager
from utils.validators import DataValidator


class InputAgent:
    """Handle file uploads, validation, and metadata extraction."""

    def __init__(self, session: SessionManager):
        self.validator = DataValidator()
        self.session = session

    def process_upload(
        self,
        file_bytes: bytes,
        filename: str,
        file_size: int
    ) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Validate and load the uploaded file into a DataFrame."""
        try:
            is_valid, msg = self.validator.validate_file_extension(filename, ALLOWED_EXTENSIONS)
            if not is_valid:
                return False, msg, None

            is_valid, msg = self.validator.validate_file_size(file_size, MAX_FILE_SIZE_MB)
            if not is_valid:
                return False, msg, None

            df = self._load_file(file_bytes, filename)
            if df is None:
                return False, "Failed to load file", None

            is_valid, msg = self.validator.validate_dataframe(df)
            if not is_valid:
                return False, msg, None

            self.session.set_file_info({
                'filename': filename,
                'size_mb': file_size / (1024 * 1024),
                'extension': Path(filename).suffix.lower()
            })

            return True, "File loaded successfully", df

        except Exception as exc:  # pragma: no cover - defensive
            return False, f"Error processing file: {exc}", None

    def _load_file(self, file_bytes: bytes, filename: str) -> Optional[pd.DataFrame]:
        file_extension = Path(filename).suffix.lower()
        buffer = io.BytesIO(file_bytes)

        try:
            if file_extension == '.csv':
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                    buffer.seek(0)
                    try:
                        return pd.read_csv(buffer, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                buffer.seek(0)
                return pd.read_csv(buffer, encoding='utf-8', errors='ignore')

            if file_extension in ['.xlsx', '.xls']:
                buffer.seek(0)
                engine = 'openpyxl' if file_extension == '.xlsx' else 'xlrd'
                return pd.read_excel(buffer, engine=engine)

            return None

        except Exception:
            return None
    
    def analyze_dataset(self, df: pd.DataFrame) -> Dict:
        """
        Analyze dataset and extract metadata
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024),  # MB
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'categorical_columns': list(df.select_dtypes(include=['object', 'category']).columns),
            'datetime_columns': list(df.select_dtypes(include=['datetime']).columns),
        }
        
        # Detect data quality issues
        issues = self.validator.detect_data_issues(df)
        metadata['issues'] = issues
        
        for key, value in metadata.items():
            self.session.set_metadata(key, value)

        return metadata

    def build_preview(self, df: pd.DataFrame) -> Dict[str, Any]:
        col_info = []
        for col in df.columns:
            col_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_values': int(df[col].nunique())
            })

        return {
            'columns': col_info,
            'head': df.head(10).to_dict(orient='records')
        }

    def execute(self, file_bytes: bytes, filename: str, file_size: int) -> Dict[str, Any]:
        success, message, df = self.process_upload(file_bytes, filename, file_size)
        if not success or df is None:
            return {'success': False, 'message': message}

        metadata = self.analyze_dataset(df)
        preview = self.build_preview(df)

        self.session.set_dataframe(df, 'raw')
        self.session.set_dataframe(df, 'current')
        self.session.update_agent_status('input_complete', True)

        return {
            'success': True,
            'message': message,
            'metadata': metadata,
            'preview': preview
        }
