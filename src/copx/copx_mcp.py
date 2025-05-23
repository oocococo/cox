from mcp.server.fastmcp import FastMCP
import os # Added import for os module
from pocketflow import Flow
from pydantic import BaseModel
from copx.project_declaration_map import update_project_declaration_map
from copx.flow import run_agent
from copx.utils import LLMClient  # Add LLMClient import

_git_path = os.environ.get("COX_DATA_PATH")
_model = os.environ.get("COX_MODEL")
_api_key = os.environ.get("COX_API_KEY")
_base_url = os.environ.get("COX_BASE_URL")

mcp = FastMCP("CodeExpert", dependencies=["pocketflow","pydantic","tree_sitter","aiofiles","tree_sitter_go","pathspec"])

@mcp.tool(name="Query",description="Get expert answer about project's codebase")
async def mcp_query(query: str,project_path: str):
    assert _git_path is not None
    assert _model is not None
    assert _api_key is not None
    assert _base_url is not None
    # Ensure query.git_path exists, if not, create it
    if not os.path.exists(_git_path):
        os.makedirs(_git_path)
        print(f"Created directory: {_git_path}")

    decl_map, changed = await update_project_declaration_map(project_path, _git_path)
    print("此次变更涉及:", changed)
    llm_client = LLMClient(
        model_id=_model, base_url=_base_url, api_key=_api_key
    )
    shared = await run_agent(project_path, query, decl_map, llm_client)
    return shared["answer"]

def main():
    mcp.run()
