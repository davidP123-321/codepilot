import json
import os

from openai import OpenAI

from app.sandbox import list_files, read_file, write_file, run_command

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def build_project_context(project_name: str):
    files = list_files(project_name).get("files", [])
    context = []
    for path in files[:10]:
        file_data = read_file(project_name, path)
        if "error" not in file_data:
            context.append({
                "path": path,
                "content": file_data["content"][:4000]
            })
    return {
        "files": files,
        "sample_files": context
    }


def chat_with_agent(project_name: str, user_message: str):
    context = build_project_context(project_name)
    project_files = context["files"]
    sample_files = context["sample_files"]

    system_prompt = f"""
Tu es un agent de développement qui travaille dans un projet de code.

Contexte du projet :
- Fichiers: {project_files[:50]}
- Échantillon de fichiers:
{json.dumps(sample_files, indent=2)[:6000]}

Règles:
1. Lis le code avant de modifier.
2. Ne modifie pas sans besoin.
3. Vérifie le build/test après chaque correction.
4. Si une commande échoue, analyse immédiatement l’erreur.
5. Fournis un résumé clair de ce que tu as changé.
"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List project files",
                "parameters": {
                    "type": "object",
                    "properties": {"project_name": {"type": "string"}},
                    "required": ["project_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "path": {"type": "string"}
                    },
                    "required": ["project_name", "path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["project_name", "path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_command",
                "description": "Run shell command inside project container",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string"},
                        "command": {"type": "string"}
                    },
                    "required": ["project_name", "command"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    for _ in range(8):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            temperature=0.2
        )

        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        if not tool_calls:
            return {
                "assistant_message": msg.content,
                "final": True
            }

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        })

        for tc in tool_calls:
            function_name = tc.function.name
            arguments = json.loads(tc.function.arguments)

            if function_name == "list_files":
                result = list_files(arguments["project_name"])
            elif function_name == "read_file":
                result = read_file(arguments["project_name"], arguments["path"])
            elif function_name == "write_file":
                result = write_file(arguments["project_name"], arguments["path"], arguments["content"])
            elif function_name == "run_command":
                result = run_command(arguments["project_name"], arguments["command"])
            else:
                result = {"error": f"Tool unknown: {function_name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": function_name,
                "content": json.dumps(result)
            })

    return {
        "assistant_message": "L'agent a terminé avec plusieurs itérations.",
        "final": True
    }
