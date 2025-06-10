from langchain_nvidia import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
import os
import dotenv
from ..utils.vector_store import VectorStore

dotenv.load_dotenv()

MODEL_NAME = "meta/llama-3.1-70b-instruct"

def hint_pipeline(problem_description: str, context: str = "") -> str:
    vector_store = VectorStore()
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))
    
    # Get relevant context from vector store
    search_results = vector_store.similarity_search(problem_description, k=3)
    retrieved_context = "\n".join([doc['page_content'] for doc in search_results])
    
    # Combine provided context with retrieved context
    full_context = f"{context}\n{retrieved_context}" if context else retrieved_context

    sys_msg = SystemMessage(content=(
        "You are a helpful programming assistant. Using the context below, provide a hint "
        "for solving the problem without giving away the complete solution:\n"
        f"Context:\n{full_context}\n\n"
        "Give a clear but subtle hint that guides the user towards the solution."
    ))
    
    human_msg = HumanMessage(content=f"I need a hint for this problem: {problem_description}")

    response = llm.invoke([sys_msg, human_msg])
    if isinstance(response, dict):
        return response['messages'][-1].content
    return response.content