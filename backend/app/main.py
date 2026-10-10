from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import chat_with_agent
from app.sandbox import create_project, list_files, read_file, write_file, run_command

app = FastAPI(title="CodePilot Advanced")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateProjectReq(BaseModel):
    name: str


class WriteFileReq(BaseModel):
    path: str
    content: str


class CommandReq(BaseModel):
    command: str


class ChatReq(BaseModel):
    project_name: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/projects")
def create(req: CreateProjectReq):
    return create_project(req.name)


@app.get("/projects")
def list_projects():
    from pathlib import Path
    root = Path("/tmp/codepilot_projects")
    if not root.exists():
        return []
    return [{"name": p.name, "path": str(p)} for p in root.iterdir() if p.is_dir()]


@app.get("/projects/{project_name}/files")
def files(project_name: str):
    result = list_files(project_name)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.get("/projects/{project_name}/file")
def read(project_name: str, path: str):
    result = read_file(project_name, path)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.post("/projects/{project_name}/file")
def write(project_name: str, req: WriteFileReq):
    result = write_file(project_name, req.path, req.content)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.post("/projects/{project_name}/run")
def run(project_name: str, req: CommandReq):
    result = run_command(project_name, req.command)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.post("/agent/chat")
def agent_chat(req: ChatReq):
    result = chat_with_agent(req.project_name, req.message)
    return result
