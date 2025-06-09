from langchain_nvidia import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from ..utils.check_code_correctness import check_code
import os
import dotenv
dotenv.load_dotenv()

MODEL_NAME = "meta/llama-3.3-70b-instruct"

def evaluate_and_feedback(exercise, solution, inputs, outputs):
    # 1. Run check_code
    check_result = check_code(inputs, outputs, solution)
    correct = check_result["correct"]
    comment = check_result["comment"]

    # 2. Prepare feedback prompt for the agent
    llm = ChatNVIDIA(model=MODEL_NAME, nvidia_api_key=os.getenv("NVIDIA_API_KEY"))
    sys_msg = SystemMessage(content=(
        "You are a Python tutor. Given the following exercise, user solution, test results, and feedback, provide constructive feedback to the user.\n\n"
        "Respond in Markdown. If the code is correct, praise the user and suggest improvements. If incorrect, explain the mistake and how to fix it."
    ))
    human_msg = HumanMessage(content=(
        f"Exercise:\n{exercise}\n\n"
        f"User solution:\n{solution}\n\n"
        f"Inputs: {inputs}\n"
        f"Expected Outputs: {outputs}\n"
        f"Test Results: {comment}\n"
    ))

    # 3. Use LangGraph ReAct agent for feedback
    agent = create_react_agent(model=llm, tools=[], debug=False)
    result = agent.invoke({"messages": [sys_msg, human_msg]})
    feedback = result['messages'][-1].content

    # 4. Return JSON
    return {
        "correct": correct,
        "feedback": feedback
    }