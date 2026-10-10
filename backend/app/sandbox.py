import subprocess
from pathlib import Path

PROJECTS_ROOT = Path("/tmp/codepilot_projects")
PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)


def ensure_project(project_name: str):
    project_dir = PROJECTS_ROOT / project_name
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def create_project(project_name: str):
    project_dir = ensure_project(project_name)
    return {
        "project": project_name,
        "path": str(project_dir),
        "files": []
    }


def list_files(project_name: str):
    project_dir = PROJECTS_ROOT / project_name
    if not project_dir.exists():
        return {"error": "Project not found"}

    files = []
    for p in project_dir.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(project_dir)))
    return {"files": files}


def read_file(project_name: str, path: str):
    file_path = PROJECTS_ROOT / project_name / path
    if not file_path.exists():
        return {"error": "File not found"}
    return {"path": path, "content": file_path.read_text()}


def write_file(project_name: str, path: str, content: str):
    file_path = PROJECTS_ROOT / project_name / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return {"ok": True, "path": path}


def run_command(project_name: str, command: str):
    project_dir = PROJECTS_ROOT / project_name
    if not project_dir.exists():
        return {"error": "Project not found"}

    try:
        result = subprocess.run(
            ["docker", "run", "--rm",
             "-v", f"{str(project_dir)}:/workspace",
             "-w", "/workspace",
             "codepilot-sandbox",
             "bash", "-lc", command],
            capture_output=True,
            text=True,
            timeout=180
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": 124,
            "stdout": "",
            "stderr": "Command timed out"
        }
