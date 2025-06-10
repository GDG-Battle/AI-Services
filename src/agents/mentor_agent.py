from langchain_nvidia import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
import os
import dotenv
from ..utils.vector_store import VectorStore

dotenv.load_dotenv()

MODEL_NAME = "meta/llama-3.1-70b-instruct"

def mentor_pipeline(user_query: str) -> str:
    vector_store = VectorStore()
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))

    # Get relevant context from vector store
    search_results = vector_store.similarity_search(user_query, k=3)
    context = "\n".join([doc['page_content'] for doc in search_results])

    sys_msg = SystemMessage(content=(
        "You are an IT mentor. Using the context below, provide guidance on the following topic:\n"
        f"Context:\n{context}\n\n"
        "Respond in a clear and concise manner, offering insights and resources."
    ))
    
    human_msg = HumanMessage(content=f"Please explain the concept of: {user_query}")

    response = llm.invoke([sys_msg, human_msg])
    if isinstance(response, dict):
        return response['messages'][-1].content
    return response.content