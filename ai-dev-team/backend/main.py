import asyncio
import io
import json
import os
import uuid
import zipfile
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.database import init_db, AsyncSessionLocal, Project, AgentLog, TestResult
from config.settings import settings
from workflows.sprint_manager import SprintManager
from workflows.approval_workflow import send_approval_email

# In-memory project store (use DB for persistence)
active_runs: Dict[str, dict] = {}
ws_connections: Dict[str, list] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    yield

app = FastAPI(title="AI Dev Team API", lifespan=lifespan)

_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket for live progress ─────────────────────────────────────────────
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()
    if project_id not in ws_connections:
        ws_connections[project_id] = []
    ws_connections[project_id].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[project_id].remove(websocket)

async def broadcast(project_id: str, message: dict):
    if project_id in ws_connections:
        dead = []
        for ws in ws_connections[project_id]:
            try:
                await ws.send_json(message)
            except:
                dead.append(ws)
        for ws in dead:
            ws_connections[project_id].remove(ws)

# ── Project endpoints ────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    name: str
    requirements: str

@app.post("/api/projects")
async def create_project_from_text(body: ProjectCreate):
    project_id = str(uuid.uuid4())[:8]
    active_runs[project_id] = {
        "id": project_id,
        "name": body.name,
        "status": "created",
        "created_at": datetime.utcnow().isoformat(),
        "logs": [],
        "phases": [],
    }
    asyncio.create_task(_run_project(project_id, body.name, body.requirements))
    return {"project_id": project_id, "status": "started", "message": "AI Dev Team is working..."}

@app.post("/api/projects/upload")
async def create_project_from_file(
    name: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    project_id = str(uuid.uuid4())[:8]

    if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
        import io
        df = pd.read_excel(io.BytesIO(content))
        requirements = df.to_string(index=False)
    elif file.filename.endswith(".csv"):
        import io
        df = pd.read_csv(io.BytesIO(content))
        requirements = df.to_string(index=False)
    else:
        requirements = content.decode("utf-8", errors="replace")

    active_runs[project_id] = {
        "id": project_id,
        "name": name,
        "status": "created",
        "created_at": datetime.utcnow().isoformat(),
        "logs": [],
        "phases": [],
    }
    asyncio.create_task(_run_project(project_id, name, requirements))
    return {"project_id": project_id, "status": "started"}

@app.get("/api/projects")
async def list_projects():
    return {"projects": list(active_runs.values())}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    return active_runs[project_id]

@app.get("/api/projects/{project_id}/files")
async def list_files(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    project = active_runs[project_id]
    output_dir = project.get("output_dir")
    if not output_dir or not os.path.exists(output_dir):
        return {"files": []}

    file_list = []
    for root, dirs, files in os.walk(output_dir):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules"}]
        for fname in files:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, output_dir)
            size = os.path.getsize(full)
            file_list.append({"path": rel, "size": size,
                               "ext": os.path.splitext(fname)[1].lstrip(".")})
    return {"files": sorted(file_list, key=lambda x: x["path"]), "output_dir": output_dir}

@app.get("/api/projects/{project_id}/files/view")
async def view_file(project_id: str, path: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    output_dir = active_runs[project_id].get("output_dir", "")
    full_path = os.path.normpath(os.path.join(output_dir, path))
    if not full_path.startswith(os.path.normpath(output_dir)):
        raise HTTPException(403, "Path traversal not allowed")
    if not os.path.isfile(full_path):
        raise HTTPException(404, "File not found")
    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    return {"path": path, "content": content}

@app.get("/api/projects/{project_id}/download")
async def download_project(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    output_dir = active_runs[project_id].get("output_dir")
    if not output_dir or not os.path.exists(output_dir):
        raise HTTPException(404, "No generated files yet")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules"}]
            for fname in files:
                full = os.path.join(root, fname)
                arc = os.path.relpath(full, os.path.dirname(output_dir))
                zf.write(full, arc)
    buf.seek(0)
    project_name = active_runs[project_id].get("name", project_id).replace(" ", "_")
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": f'attachment; filename="{project_name}_generated.zip"'})

@app.get("/api/projects/{project_id}/report")
async def get_report(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    project = active_runs[project_id]
    report_path = project.get("report_path")
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(404, "Report not yet generated")
    return FileResponse(report_path, media_type="text/html")

@app.post("/api/projects/{project_id}/approve")
async def approve_project(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    active_runs[project_id]["status"] = "approved"
    active_runs[project_id]["approved_at"] = datetime.utcnow().isoformat()
    await broadcast(project_id, {"event": "approved", "message": "Project approved for production!"})
    return {"status": "approved", "message": "Project approved. Ready for production deployment."}

@app.post("/api/projects/{project_id}/reject")
async def reject_project(project_id: str, reason: str = ""):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    active_runs[project_id]["status"] = "rejected"
    active_runs[project_id]["rejection_reason"] = reason
    await broadcast(project_id, {"event": "rejected", "message": f"Project rejected: {reason}"})
    return {"status": "rejected"}

@app.get("/api/projects/{project_id}/logs")
async def get_logs(project_id: str):
    if project_id not in active_runs:
        raise HTTPException(404, "Project not found")
    return {"logs": active_runs[project_id].get("logs", [])}

# ── Background task ─────────────────────────────────────────────────────────
async def _run_project(project_id: str, name: str, requirements: str):
    active_runs[project_id]["status"] = "in_progress"
    loop = asyncio.get_running_loop()

    def progress_callback(data: dict):
        event_type = data.get("event", "log")
        active_runs[project_id]["logs"].append(data)

        if event_type == "phase":
            active_runs[project_id]["phases"].append(data)
            active_runs[project_id]["current_phase"] = data.get("name", "")

        # Safe to call from background thread
        asyncio.run_coroutine_threadsafe(broadcast(project_id, data), loop)

    manager = SprintManager(project_id=project_id, project_name=name)
    manager.set_progress_callback(progress_callback)

    try:
        result = await asyncio.to_thread(manager.run, requirements)

        active_runs[project_id].update({
            "status": result["status"],
            "output_dir": result["output_dir"],
            "report_path": result["report_path"],
            "security": result["security"],
            "performance": result["performance"],
            "sprints_completed": result["sprints_completed"],
            "total_stories": result["total_stories"],
            "total_files": result["total_files"],
            "approval_required": result["approval_required"],
            "completed_at": datetime.utcnow().isoformat(),
        })

        # Send approval email if all tests pass
        if result["approval_required"] and settings.APPROVAL_EMAIL:
            email_sent = send_approval_email(
                project_name=name,
                project_id=project_id,
                report_path=result["report_path"],
                security_score=result["security"]["score"] or 0,
                perf_score=result["performance"]["score"] or 0,
                total_stories=result["total_stories"],
            )
            active_runs[project_id]["approval_email_sent"] = email_sent

        await broadcast(project_id, {
            "event": "completed",
            "status": result["status"],
            "report_path": f"/api/projects/{project_id}/report",
            "security": result["security"],
            "performance": result["performance"],
        })

    except Exception as e:
        active_runs[project_id]["status"] = "error"
        active_runs[project_id]["error"] = str(e)
        await broadcast(project_id, {"event": "error", "message": str(e)})
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
