"""Flask backend for the AI-powered multi-agent analytics system."""

from __future__ import annotations

import os
import mimetypes
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from flask import (
    Flask,
    abort,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    render_template,
    request,
    session as flask_session,
    send_from_directory,
    url_for,
)
from flask_cors import CORS
from plotly.utils import PlotlyJSONEncoder
from werkzeug.exceptions import HTTPException

from agents import (
    CleaningAgent,
    InputAgent,
    NLQAgent,
    ReportAgent,
    VisualizationAgent,
)
from utils.config import REPORTS_DIR
from utils.session_manager import SessionManager

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STAGE_TABS = [
    {"key": "upload", "label": "Upload"},
    {"key": "clean", "label": "Clean"},
    {"key": "query", "label": "Ask"},
    {"key": "visualize", "label": "Visualize"},
    {"key": "report", "label": "Report"},
]

app = Flask(
    __name__,
    static_folder=None,
    template_folder=str(TEMPLATES_DIR),
)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

SESSION_COOKIE_KEY = "analytics_session_id"


def ensure_web_session() -> SessionManager:
    session_id = flask_session.get(SESSION_COOKIE_KEY)
    if not session_id or not SessionManager.has_session(session_id):
        session_id = SessionManager.create_session()
        flask_session[SESSION_COOKIE_KEY] = session_id
    return SessionManager(session_id)


def resolve_session_from_request() -> SessionManager:
    header_session = request.headers.get("X-Session-Id")
    if header_session and SessionManager.has_session(header_session):
        return SessionManager(header_session)
    cookie_session = flask_session.get(SESSION_COOKIE_KEY)
    if cookie_session and SessionManager.has_session(cookie_session):
        return SessionManager(cookie_session)
    abort(400, description="Missing or invalid session id")


def get_session_or_abort() -> SessionManager:
    session_id = request.headers.get("X-Session-Id")
    if not session_id or not SessionManager.has_session(session_id):
        abort(400, description="Missing or invalid session id")
    return SessionManager(session_id)


def serialize_history(session: SessionManager) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    for item in session.state.query_history:
        result = item["result"]
        if isinstance(result, pd.DataFrame):
            summary: Dict[str, Any] = {
                "type": "dataframe",
                "rows": len(result),
                "columns": list(result.columns),
            }
        elif isinstance(result, pd.Series):
            summary = {
                "type": "series",
                "length": len(result),
                "name": result.name,
            }
        elif isinstance(result, (int, float)):
            summary = {"type": "scalar", "value": result}
        else:
            summary = {"type": "text", "value": str(result)}
        history.append(
            {
                "timestamp": item["timestamp"],
                "query": item["query"],
                "explanation": item["explanation"],
                "result_summary": summary,
            }
        )
    return history


def build_cleaning_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "clean_missing": bool(payload.get("clean_missing", False)),
        "missing_strategy": payload.get("missing_strategy"),
        "missing_columns": payload.get("missing_columns") or [],
        "clean_duplicates": bool(payload.get("clean_duplicates", True)),
        "duplicate_strategy": payload.get("duplicate_strategy") or "drop",
    }


def build_chart_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "chart_type": payload.get("chart_type"),
        "x_col": payload.get("x_col"),
        "y_col": payload.get("y_col"),
    }


def serialize_chart_payloads(charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for chart in charts or []:
        figure = chart.get("figure") or {}
        try:
            figure_json = json.dumps(figure, cls=PlotlyJSONEncoder)
        except TypeError:
            figure_json = json.dumps({"data": [], "layout": {}}, cls=PlotlyJSONEncoder)
        serialized.append({**chart, "figure_json": figure_json})
    return serialized


def build_dashboard_context(session: SessionManager, current_step: str) -> Dict[str, Any]:
    valid_steps = {tab["key"] for tab in STAGE_TABS}
    if current_step not in valid_steps:
        current_step = STAGE_TABS[0]["key"]

    summary = session.get_summary()
    cleaning_agent = CleaningAgent(session)
    cleaning_needs = cleaning_agent.get_cleaning_needs()

    return {
        "stage_tabs": STAGE_TABS,
        "current_step": current_step,
        "summary": summary,
        "file_info": session.get_file_info(),
        "dataset_preview": session.state.dataset_preview,
        "cleaning_needs": cleaning_needs,
        "cleaning_summary": session.state.cleaning_summary,
        "query_result": session.state.last_query_result,
        "history": serialize_history(session),
        "chart_payloads": serialize_chart_payloads(session.state.chart_payloads),
        "report_status": session.state.report_status,
        "flash_messages": get_flashed_messages(with_categories=True),
    }


def json_error(message: str, status_code: int):
    response = jsonify({"detail": message})
    response.status_code = status_code
    return response


@app.errorhandler(HTTPException)
def handle_http_exception(exc: HTTPException):
    if request.path.startswith("/api/"):
        description = exc.description or exc.name or "Request error"
        return json_error(description, exc.code or 500)
    return exc


@app.errorhandler(Exception)
def handle_unexpected_exception(exc: Exception):
    if request.path.startswith("/api/"):
        app.logger.exception(exc)
        return json_error("Internal server error", 500)
    raise exc


@app.route("/")
def serve_index():
    session = ensure_web_session()
    current_step = request.args.get("step", STAGE_TABS[0]["key"])
    context = build_dashboard_context(session, current_step)
    return render_template("index.html", **context)


@app.route("/assets/<path:filename>")
def serve_asset(filename: str):
    assets_root = STATIC_DIR.resolve()
    file_path = (assets_root / filename).resolve()
    if not str(file_path).startswith(str(assets_root)):
        abort(404, description="Asset not found")
    if not file_path.exists():
        abort(404, description="Asset not found")
    content_type, _ = mimetypes.guess_type(str(file_path))
    return send_from_directory(
        str(assets_root),
        str(file_path.relative_to(assets_root)),
        mimetype=content_type or "application/octet-stream",
    )


@app.route("/session/reset", methods=["POST"])
def reset_web_session():
    flask_session.pop(SESSION_COOKIE_KEY, None)
    ensure_web_session()
    flash("Session reinitialized", "success")
    return redirect(url_for("serve_index"))


@app.route("/upload", methods=["POST"])
def upload_step():
    session = ensure_web_session()
    file_storage = request.files.get("file")
    if file_storage is None or file_storage.filename == "":
        flash("Please select a file to upload.", "error")
        return redirect(url_for("serve_index", step="upload"))

    file_bytes = file_storage.read()
    agent = InputAgent(session)
    result = agent.execute(file_bytes, file_storage.filename, len(file_bytes))
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.dataset_preview = result.get("preview", {})
        session.state.cleaning_summary = {}
        session.state.last_query_result = {}
        session.state.chart_payloads = []
        session.state.report_status = {}
        flash(result["message"], "success")
    return redirect(url_for("serve_index", step="upload"))


@app.route("/clean", methods=["POST"])
def clean_step():
    session = ensure_web_session()
    payload = {
        "clean_missing": True,
        "missing_strategy": request.form.get("missing_strategy"),
        "missing_columns": [col.strip() for col in (request.form.get("missing_columns") or "").split(",") if col.strip()],
        "clean_duplicates": bool(request.form.get("handle_duplicates")),
        "duplicate_strategy": "drop" if request.form.get("handle_duplicates") else "keep",
    }
    agent = CleaningAgent(session)
    result = agent.execute(payload)
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.cleaning_summary = result.get("summary", {})
        flash(result["message"], "success")
    return redirect(url_for("serve_index", step="clean"))


@app.route("/query", methods=["POST"])
def query_step():
    session = ensure_web_session()
    query_text = (request.form.get("query") or "").strip()
    if not query_text:
        flash("Enter a natural language question first.", "error")
        return redirect(url_for("serve_index", step="query"))
    agent = NLQAgent(session)
    result = agent.execute(query_text)
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.last_query_result = result
        flash("Query executed successfully.", "success")
    return redirect(url_for("serve_index", step="query"))


@app.route("/visualize/auto", methods=["POST"])
def auto_visualize_step():
    session = ensure_web_session()
    agent = VisualizationAgent(session)
    result = agent.execute(auto=True)
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.chart_payloads = result.get("charts", []) + session.state.chart_payloads
        flash(result["message"], "success")
    return redirect(url_for("serve_index", step="visualize"))


@app.route("/visualize/custom", methods=["POST"])
def custom_visualize_step():
    session = ensure_web_session()
    payload = {
        "chart_type": request.form.get("chart_type"),
        "x_col": (request.form.get("x_col") or "").strip(),
        "y_col": (request.form.get("y_col") or "").strip() or None,
    }
    agent = VisualizationAgent(session)
    result = agent.execute(
        chart_type=payload["chart_type"],
        x_col=payload["x_col"],
        y_col=payload["y_col"],
        auto=False,
    )
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.chart_payloads = result.get("charts", []) + session.state.chart_payloads
        flash(result["message"], "success")
    return redirect(url_for("serve_index", step="visualize"))


@app.route("/report", methods=["POST"])
def report_step():
    session = ensure_web_session()
    agent = ReportAgent(session)
    result = agent.execute()
    if not result["success"]:
        flash(result["message"], "error")
    else:
        session.state.report_status = {
            "filename": Path(result["report_path"]).name,
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }
        flash("Report generated successfully.", "success")
    return redirect(url_for("serve_index", step="report"))


@app.route("/reset", methods=["POST"])
def reset_data_step():
    session = ensure_web_session()
    session.reset_session()
    flash("Session data cleared.", "success")
    return redirect(url_for("serve_index", step="upload"))


@app.route("/api/session", methods=["POST"])
def create_session():
    session_id = SessionManager.create_session()
    return jsonify({"session_id": session_id})


@app.route("/api/reset", methods=["POST"])
def reset_session():
    session = get_session_or_abort()
    session.reset_session()
    return jsonify({"success": True})


@app.route("/api/summary")
def get_summary():
    session = get_session_or_abort()
    return jsonify(session.get_summary())


@app.route("/api/upload", methods=["POST"])
def upload_file():
    session = get_session_or_abort()
    file_storage = request.files.get("file")
    if file_storage is None or file_storage.filename == "":
        abort(400, description="File is required")
    file_bytes = file_storage.read()
    agent = InputAgent(session)
    result = agent.execute(file_bytes, file_storage.filename, len(file_bytes))
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/api/cleaning/needs")
def cleaning_needs():
    session = get_session_or_abort()
    agent = CleaningAgent(session)
    return jsonify(agent.get_cleaning_needs())


@app.route("/api/clean", methods=["POST"])
def clean_data():
    session = get_session_or_abort()
    payload = request.get_json(silent=True) or {}
    agent = CleaningAgent(session)
    result = agent.execute(build_cleaning_payload(payload))
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/api/query", methods=["POST"])
def run_query():
    session = get_session_or_abort()
    payload = request.get_json(silent=True) or {}
    query_text = (payload.get("query") or "").strip()
    if not query_text:
        abort(400, description="Query text is required")
    agent = NLQAgent(session)
    result = agent.execute(query_text)
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/api/history")
def query_history():
    session = get_session_or_abort()
    return jsonify(serialize_history(session))


@app.route("/api/visualize/auto", methods=["POST"])
def auto_visualize():
    session = get_session_or_abort()
    agent = VisualizationAgent(session)
    result = agent.execute(auto=True)
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/api/visualize/custom", methods=["POST"])
def custom_visualize():
    session = get_session_or_abort()
    payload = request.get_json(silent=True) or {}
    chart_payload = build_chart_payload(payload)
    if not chart_payload["chart_type"] or not chart_payload["x_col"]:
        abort(400, description="Chart type and X column are required")
    agent = VisualizationAgent(session)
    result = agent.execute(
        chart_type=chart_payload["chart_type"],
        x_col=chart_payload["x_col"],
        y_col=chart_payload["y_col"],
        auto=False,
    )
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/api/charts")
def list_charts():
    session = get_session_or_abort()
    charts = [
        {
            "title": chart["title"],
            "type": chart["type"],
            "timestamp": chart["timestamp"],
        }
        for chart in session.state.generated_charts
    ]
    return jsonify(charts)


@app.route("/api/report", methods=["POST"])
def generate_report():
    session = get_session_or_abort()
    agent = ReportAgent(session)
    result = agent.execute()
    if not result["success"]:
        abort(400, description=result["message"])
    return jsonify(result)


@app.route("/reports/<path:filename>")
@app.route("/api/reports/<path:filename>")
def download_report(filename: str):
    resolve_session_from_request()
    reports_root = REPORTS_DIR.resolve()
    report_path = (reports_root / filename).resolve()
    if not str(report_path).startswith(str(reports_root)):
        abort(404, description="Report not found")
    if not report_path.exists():
        abort(404, description="Report not found")
    return send_from_directory(
        str(reports_root),
        report_path.name,
        mimetype="application/pdf",
        as_attachment=True,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug_env = os.environ.get("FLASK_DEBUG")
    debug = True if debug_env is None else debug_env == "1"
    use_reloader = os.environ.get("FLASK_USE_RELOADER", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=use_reloader)
