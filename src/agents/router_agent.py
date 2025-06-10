from langchain_nvidia import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
import os
from .mentor_agent import mentor_pipeline
from .hint_agent import hint_pipeline

MODEL_NAME = "meta/llama-3.1-70b-instruct"

def extract_context(query: str) -> tuple:
    """Extract context and core query from user input"""
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))
    
    sys_msg = SystemMessage(content="""
    Analyze the user query and extract:
    1. The main question/request
    2. Any context provided in the query
    
    Return in format: QUERY: <main question> ||| CONTEXT: <extracted context>
    If no context is provided, return empty string for context.
    """)
    
    human_msg = HumanMessage(content=f"Extract query and context: {query}")
    
    response = llm.invoke([sys_msg, human_msg])
    parts = response.content.split("|||")
    
    if len(parts) == 2:
        main_query = parts[0].replace("QUERY:", "").strip()
        context = parts[1].replace("CONTEXT:", "").strip()
        return main_query, context
    return query, ""

def route_query(query: str, additional_context: str = "") -> dict:
    """Routes the query to the appropriate agent based on query type"""
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))
    
    # Extract context from query
    main_query, extracted_context = extract_context(query)
    
    # Combine extracted context with any additional context provided
    full_context = f"{extracted_context}\n{additional_context}".strip()
    
    sys_msg = SystemMessage(content="""
    Analyze the user query and determine if it's:
    1. A request for explanation/learning about a concept (MENTOR)
    2. A request for help with a specific problem/challenge (HINT)
    
    Respond only with "MENTOR" or "HINT".
    """)
    
    human_msg = HumanMessage(content=f"Classify this query: {main_query}")
    
    response = llm.invoke([sys_msg, human_msg])
    agent_type = response.content.strip().upper()
    
    if agent_type == "MENTOR":
        result = mentor_pipeline(main_query)
        return {"type": "mentor", "response": result}
    else:
        result = hint_pipeline(main_query, full_context)
        return {"type": "hint", "response": result}