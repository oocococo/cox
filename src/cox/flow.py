import os
from typing import Dict, List
from pocketflow import AsyncFlow
import asyncio

import prompts.prompt as pm
from project_tree import get_directory_tree_for_llm
from nodes import CodeRetriver, AnswerFormulator
from utils import LLMClient

sys_prompt = pm.ROLE_2 + pm.Workflow + pm.Tools2


async def create_agent_flow():
    # Create instances of each node
    retriever = CodeRetriver()
    answer = AnswerFormulator()

    # Connect the nodes
    retriever - "continue" >> retriever

    retriever - "answer" >> answer

    # Create and return the flow, starting with the DecideAction node
    return AsyncFlow(start=retriever)


async def run_agent(
    project_path: str,
    query: str,
    declaration_map: Dict[str, List[dict]],
    llm_client: LLMClient,
):
    flow = await create_agent_flow()
    init_messages = [
        {"role": "system", "content": sys_prompt},
        {
            "role": "user",
            "content": f"User is asking question about {os.path.basename(project_path)}, here's the file structure tree of this project: {get_directory_tree_for_llm(project_path)}. User's question: {query}",
        },
    ]
    shared = {
        "project_path": project_path,
        "query": query,
        "messages": init_messages,
        "llm_client": llm_client,  # Add llm_client to shared dictionary
        "declaration_map": declaration_map,  # Add declaration_map to shared dictionary
    }
    await flow.run_async(
        shared
    )  # Changed to run_async and removed asyncio.run as run_agent is now async
    return shared
