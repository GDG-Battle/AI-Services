from langchain_sandbox import PyodideSandboxTool
from langchain_core.tools import tool
import re

def check_code(inputs: list, outputs: list, user_code: str) -> dict:
    tool = PyodideSandboxTool(allow_net=True)

    match = re.search(r'def (\w+)\s*\(', user_code)
    if not match:
        return {
            "correct": False,
            "comment": "### ❌ Problem Identified\nNo function definition found in user code."
        }
    func_name = match.group(1)

    for i, input_args in enumerate(inputs):
        try:
            args = input_args if isinstance(input_args, (list, tuple)) else [input_args]
            call_str = f"{user_code}\nprint({func_name}(*{repr(args)}))"

            user_output = tool.invoke(call_str)
            try:
                user_output = eval(user_output.strip())
            except:
                pass

            if user_output != outputs[i]:
                return {
                    "correct": False,
                    "comment": f"### ❌ Problem Identified\nTest case {i} failed: expected {outputs[i]}, got {user_output}"
                }
        except Exception as e:
            return {
                "correct": False,
                "comment": f"### ❌ Problem Identified\nError running test case {i}.\n\n### 🧠 Error:\n{repr(e)}"
            }

    return {
        "correct": True,
        "comment": "### ✅ Solution Analysis\nAll test cases passed."
    }


@tool
def verify_code(data: dict) -> dict:
    """
    Validate user code by running test cases.
    Args:
        data: A dict with keys 'inputs', 'outputs', 'solution'
    Returns:
        A dict with keys 'correct' (bool) and 'comment' (str)
    """
    return check_code(data["inputs"], data["outputs"], data["solution"])

