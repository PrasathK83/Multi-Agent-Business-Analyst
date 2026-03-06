"""Session management without Streamlit dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
import threading
import uuid


@dataclass
class SessionState:
    """Container for per-session data objects."""

    raw_dataframe: Optional[pd.DataFrame] = None
    cleaned_dataframe: Optional[pd.DataFrame] = None
    current_dataframe: Optional[pd.DataFrame] = None
    dataset_metadata: Dict[str, Any] = field(default_factory=dict)
    cleaning_log: List[Dict[str, Any]] = field(default_factory=list)
    query_history: List[Dict[str, Any]] = field(default_factory=list)
    generated_charts: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[Dict[str, Any]] = field(default_factory=list)
    agent_status: Dict[str, bool] = field(default_factory=lambda: {
        'input_complete': False,
        'cleaning_complete': False,
        'nlq_ready': False
    })
    uploaded_file_info: Dict[str, Any] = field(default_factory=dict)
    dataset_preview: Dict[str, Any] = field(default_factory=dict)
    cleaning_summary: Dict[str, Any] = field(default_factory=dict)
    last_query_result: Dict[str, Any] = field(default_factory=dict)
    chart_payloads: List[Dict[str, Any]] = field(default_factory=list)
    report_status: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Thread-safe session store for API consumers."""

    _sessions: Dict[str, SessionState] = {}
    _lock = threading.Lock()

    def __init__(self, session_id: str):
        self.session_id = session_id
        with SessionManager._lock:
            if session_id not in SessionManager._sessions:
                SessionManager._sessions[session_id] = SessionState()
        self.state = SessionManager._sessions[session_id]

    # ------------------------------------------------------------------
    # Session lifecycle helpers
    # ------------------------------------------------------------------
    @classmethod
    def create_session(cls) -> str:
        """Create and register a new session identifier."""
        session_id = uuid.uuid4().hex
        with cls._lock:
            cls._sessions[session_id] = SessionState()
        return session_id

    @classmethod
    def delete_session(cls, session_id: str):
        """Remove session from store if present."""
        with cls._lock:
            cls._sessions.pop(session_id, None)

    @classmethod
    def has_session(cls, session_id: str) -> bool:
        return session_id in cls._sessions

    # ------------------------------------------------------------------
    # Dataframe helpers
    # ------------------------------------------------------------------
    def set_dataframe(self, df: pd.DataFrame, df_type: str = 'current'):
        if df_type == 'raw':
            self.state.raw_dataframe = df.copy()
        elif df_type == 'cleaned':
            self.state.cleaned_dataframe = df.copy()
        self.state.current_dataframe = df.copy()

    def get_dataframe(self, df_type: str = 'current') -> Optional[pd.DataFrame]:
        if df_type == 'raw':
            return self.state.raw_dataframe
        if df_type == 'cleaned':
            return self.state.cleaned_dataframe
        return self.state.current_dataframe

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def add_cleaning_log(self, action: str, details: str):
        self.state.cleaning_log.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'details': details
        })

    def add_query(self, query: str, result: Any, explanation: str):
        self.state.query_history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'query': query,
            'result': result,
            'explanation': explanation
        })

    def add_chart(self, chart_obj: Any, chart_type: str, title: str):
        self.state.generated_charts.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'chart': chart_obj,
            'type': chart_type,
            'title': title
        })

    def add_insight(self, insight: str, category: str = 'general'):
        self.state.insights.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'text': insight,
            'category': category
        })

    # ------------------------------------------------------------------
    # Metadata helpers
    # ------------------------------------------------------------------
    def set_metadata(self, key: str, value: Any):
        self.state.dataset_metadata[key] = value

    def get_metadata(self, key: str) -> Any:
        return self.state.dataset_metadata.get(key)

    def update_agent_status(self, agent: str, status: bool):
        self.state.agent_status[agent] = status

    def set_file_info(self, info: Dict[str, Any]):
        self.state.uploaded_file_info = info

    def get_file_info(self) -> Dict[str, Any]:
        return self.state.uploaded_file_info

    def reset_session(self):
        SessionManager._sessions[self.session_id] = SessionState()
        self.state = SessionManager._sessions[self.session_id]

    def get_summary(self) -> Dict[str, Any]:
        df = self.state.current_dataframe
        return {
            'has_data': df is not None,
            'rows': len(df) if df is not None else 0,
            'columns': len(df.columns) if df is not None else 0,
            'cleaning_operations': len(self.state.cleaning_log),
            'queries_executed': len(self.state.query_history),
            'charts_generated': len(self.state.generated_charts),
            'insights_count': len(self.state.insights)
        }

