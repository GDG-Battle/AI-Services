import os, json
from typing import Dict
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
import dotenv
dotenv.load_dotenv()

MODEL_NAME = "meta/llama-3.3-70b-instruct"

# --- QCM generator using ReAct agent ---
def qcm_pipeline(user_query: str, difficulty: str, context: str, number_of_questions: int) -> Dict:
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))

    # Prepare prompt with explicit context
    sys_msg = SystemMessage(content=(
        f"You are an educational assistant. Using the context below, generate exactly {number_of_questions} multiple-choice questions at the '{difficulty}' level. "
        f"Each question must have exactly 3 plausible options and ONLY ONE correct answer.\n\n"
        f"Context:\n{context}\n\n"
        "Return only a valid JSON in this exact format (use double quotes for all keys and string values):\n"
        '''{
    "quiz": [
        {
        "question": "string",
        "options": ["option1", "option2", "option3"],
        "answer": 1
        }
        // Repeat this format for each question
    ]
    }'''
        f"\nYou MUST return exactly {number_of_questions} questions inside the 'quiz' array. No more, no less. Do NOT explain. Only output the JSON."
    ))

    human_msg = HumanMessage(content=f"Generate a question about: {user_query}")

    # No retrieval tool needed here, just pass the LLM
    agent = create_react_agent(model=llm, tools=[], debug=False)

    result = agent.invoke({"messages": [sys_msg, human_msg]})

    try:
        parsed = json.loads(result['messages'][-1].content.strip().strip("```json").strip("```"))
    except json.JSONDecodeError:
        raise ValueError(f"Output is not valid JSON:\n{result['messages'][-1].content}")

    return parsed

