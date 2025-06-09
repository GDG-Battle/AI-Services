import os, json
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from ..utils.check_code_correctness import verify_code

import dotenv
dotenv.load_dotenv()

MODEL_NAME = "meta/llama-3.3-70b-instruct"

def coding_exo_pipeline(user_query, difficulty, context):
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))

    sys_msg = SystemMessage(content=(
        f"You are an expert Python coding exercise generator and validator.\n\n"
        f"Context:\n{context}\n\n"
        f"Your task is to:\n"
        f"1. Generate a Python coding exercise at the '{difficulty}' level.\n"
        f"2. The exercise **must include** the function signature with all parameters and their types, and specify the return type.\n"
        f"3. Provide a correct Python solution for the exercise.\n"
        f"4. Create at least 3 test cases as a list of inputs (arguments for the function) and the expected output for each input.\n"
        f"5. Use the tool `verify_code` to check the correctness of your solution by passing your solution, inputs, and expected outputs.\n"
        f"6. If `verify_code` returns incorrect, regenerate the solution and/or test cases and recheck.\n"
        f"7. Repeat until the solution passes all test cases and `verify_code` returns correct.\n"
        f"8. Ensure a strict 1:1 mapping between inputs and outputs (same length, same order).\n"
        f"9. Return only a valid **JSON object** in this format:\n"
        '''{{
        "exercise": "string (clearly state the problem and the exact function signature, including parameter and return types)",
        "solution": "string (Python code)",
        "inputs": [[...], [...], ...],  # list of input arguments
        "outputs": [...]  # expected results (int, str, list, etc.)
        }}'''
        f"\nDO NOT include explanations, markdown, function calls, or code blocks. Only return the raw JSON."
    ))


    human_msg = HumanMessage(content=f"Generate a coding exercise about: {user_query}")
    tools = [verify_code]
    agent = create_react_agent(model=llm, tools=tools, debug=True)
    for _ in range(5):
        result = agent.invoke({"messages": [sys_msg, human_msg]})
        try:
            content = result['messages'][-1].content.strip().strip("```json").strip("```")
            parsed = json.loads(content)
            return parsed
        except Exception:
            raise Exception("failed to generate an appropriate json")