import fastapi
import os # Added import for os module
from pocketflow import Flow
from pydantic import BaseModel
from project_declaration_map import update_project_declaration_map
from flow import run_agent
from utils import LLMClient  # Add LLMClient import


class CodeQuery(BaseModel):
    project_path: str
    question: str
    model: str = "openai/gemini-2.5-pro"
    api_base: str = "http://100.68.29.74:8000/v1"
    api_key: str = "123"
    git_path: str = "~/Documents/CodeQA/git_mirror"


app = fastapi.FastAPI()


@app.post("/query")
async def query(query: CodeQuery):
    proj_path = query.project_path
    git_path = os.path.expanduser(query.git_path) # Expand user for git_path

    # Ensure query.git_path exists, if not, create it
    if not os.path.exists(git_path):
        os.makedirs(git_path)
        print(f"Created directory: {git_path}")

    decl_map, changed = await update_project_declaration_map(proj_path, git_path)
    print("此次变更涉及:", changed)
    llm_client = LLMClient(
        model_id=query.model, base_url=query.api_base, api_key=query.api_key
    )
    shared = await run_agent(proj_path, query.question, decl_map, llm_client)
    return shared["answer"]


