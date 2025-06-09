from typing import List
from ..agents.qcm_gen_agent import qcm_pipeline
from ..agents.exo_gen_agent import coding_exo_pipeline

def generate_lab(context: str, number_of_question: int, user_query: str=None, task: str="qcm", difficulty: str="easy"):
    if(task not in ["qcm", "code"]):
        raise ValueError("Invalid task type. Choose 'qcm' or 'code'.")

    # use the appropriate agent based on the task
    if task == "qcm":
        # results is in a dict
        results = qcm_pipeline(user_query, difficulty, context, number_of_question)
    else:
        results = coding_exo_pipeline(user_query, difficulty, context)
    return results