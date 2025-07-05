# src/agents.py
from typing import Dict, List
from mistralai import Mistral
from src.config import MISTRAL_API_KEY, supabase
import numpy as np

mistral_client = Mistral(api_key=MISTRAL_API_KEY)

def get_mistral_embedding(text: str) -> List[float]:
    try:
        text = text.replace("\n", " ")
        response = mistral_client.embeddings.create(
            model="mistral-embed",
            inputs=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return [0.0] * 1024  # Fallback to zero vector

def task_creation_agent(objective: str, result: Dict, task_description: str, task_list: List[str]):
    prompt = f"""You are a task creation AI. Objective: {objective}. Based on the last task result: {result}, from task: {task_description}, and incomplete tasks: {', '.join(task_list)}, generate 3-5 specific, actionable tasks that advance the objective without overlapping existing tasks. Return as a numbered list."""
    try:
        response = mistral_client.chat.complete(
            model="Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        new_tasks = response.choices[0].message.content.strip().split('\n')
        return [{"task_name": task_name.strip()} for task_name in new_tasks if task_name.strip()]
    except Exception as e:
        print(f"Error in task_creation_agent: {e}")
        return []

def prioritization_agent(this_task_id: int, task_list: deque, objective: str):
    task_names = [t["task_name"] for t in task_list]
    next_task_id = int(this_task_id) + 1
    prompt = f"""You are a task prioritization AI. Objective: {objective}. Clean and reprioritize these tasks: {task_names}. Do not remove any tasks. Return as a numbered list starting with {next_task_id}."""
    try:
        response = mistral_client.chat.complete(
            model="Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1000
        )
        new_tasks = response.choices[0].message.content.strip().split('\n')
        task_list.clear()
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = task_parts[0].strip()
                task_name = task_parts[1].strip()
                task_list.append({"task_id": task_id, "task_name": task_name})
    except Exception as e:
        print(f"Error in prioritization_agent: {e}")

def execution_agent(objective: str, task: str) -> str:
    context = context_agent(query=objective, n=5)
    prompt = f"""You are an AI performing one task. Objective: {objective}. Task: {task}\nContext: {context}\nResponse:"""
    try:
        response = mistral_client.chat.complete(
            model="Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in execution_agent: {e}")
        return "Task failed due to an error."

def context_agent(query: str, n: int) -> List[str]:
    try:
        query_embedding = get_mistral_embedding(query)
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": n,
                "filter": {}
            }
        ).execute()
        sorted_results = sorted(response.data, key=lambda x: x["similarity"], reverse=True)
        return [item["metadata"].get("task", "") for item in sorted_results if item["metadata"]]
    except Exception as e:
        print(f"Error in context_agent: {e}")
        return []
