from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.supervisor_agent import SupervisorAgent
from langchain_core.messages import HumanMessage, SystemMessage
import os

from utils.memory import (
    load_memory_bundle,
    format_memory_context,
    summarize_and_store_conversation,
)

FRONTEND_ORIGIN = os.getenv(
    "FRONTEND_ORIGIN",
    "http://localhost:8000",
)

os.environ.pop("SSL_CERT_FILE", None)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    id_number: int
    messages: str

supervisor_agent = SupervisorAgent()

@app.post("/execute")
def execute_agent(user_input: UserQuery):
    app_graph = supervisor_agent.workflow()

    memory_bundle = load_memory_bundle(user_input.id_number)
    memory_context = format_memory_context(memory_bundle)

    message_stack = []
    if memory_context:
        message_stack.append(SystemMessage(content=f"Persistent memory:\n{memory_context}"))
    message_stack.append(HumanMessage(content=user_input.messages))

    query_data = {
        "messages": message_stack,
        "id_number": user_input.id_number,
        "next": "",
        "query": "",
        "current_reasoning": "",
        "current_instructions": "",
        "missing_information": [],
        "steps_taken": 0,
        "memory_context": memory_context,
    }

    response = app_graph.invoke(query_data, config={"recursion_limit": 20})
    summarize_and_store_conversation(user_input.id_number, response["messages"])
    # return JSONResponse(content = response["messages"], status_code = 200)
    return {"messages": response["messages"]}
    
