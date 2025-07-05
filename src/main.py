# src/main.py
import time
from collections import deque
from typing import Dict, List
from src.agents import (
    get_mistral_embedding,
    task_creation_agent,
    prioritization_agent,
    execution_agent,
    context_agent,
)
from src.database import setup_supabase_table, supabase
from src.config import OBJECTIVE, YOUR_TABLE_NAME, YOUR_FIRST_TASK

# Print OBJECTIVE
print("\033[96m\033[1m" + "\n*****OBJECTIVE*****\n" + "\033[0m\033[0m")
print(OBJECTIVE)

# Set up Supabase table
setup_supabase_table()

# Task list
task_list = deque([])

def add_task(task: Dict):
    task_list.append(task)

# Add the first task
first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
add_task(first_task)

# Main loop
task_id_counter = 1
max_iterations = 10  # Prevent runaway costs
iteration = 0

while task_list and iteration < max_iterations:
    # Print task list
    print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
    for t in task_list:
        print(f"{t['task_id']}: {t['task_name']}")

    # Step 1: Pull the first task
    task = task_list.popleft()
    print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
    print(f"{task['task_id']}: {task['task_name']}")

    # Step 2: Execute task
    result = execution_agent(OBJECTIVE, task["task_name"])
    this_task_id = int(task["task_id"])
    print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
    print(result)

    # Step 3: Store result in Supabase
    enriched_result = {"data": result}
    result_id = f"result_{task['task_id']}"
    try:
        supabase.table(YOUR_TABLE_NAME).insert({
            "content": result,
            "metadata": {"task": task["task_name"], "result": result},
            "embedding": get_mistral_embedding(result)
        }).execute()
    except Exception as e:
        print(f"Error storing result in Supabase: {e}")

    # Step 4: Create and prioritize new tasks
    new_tasks = task_creation_agent(
        OBJECTIVE,
        enriched_result,
        task["task_name"],
        [t["task_name"] for t in task_list]
    )
    for new_task in new_tasks:
        task_id_counter += 1
        new_task.update({"task_id": task_id_counter})
        add_task(new_task)
    prioritization_agent(this_task_id)

    iteration += 1
    time.sleep(1)

# Optional cleanup
def cleanup_supabase_table():
    try:
        supabase.sql(f"DROP TABLE IF EXISTS {YOUR_TABLE_NAME};")
        print(f"Supabase table {YOUR_TABLE_NAME} deleted.")
    except Exception as e:
        print(f"Error deleting Supabase table: {e}")

# Uncomment to cleanup after use
# cleanup_supabase_table()
