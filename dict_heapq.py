import heapq
from typing import Dict, List, Tuple


# Define a dictionary to hold the priority queue for each category
priority_queues: Dict[str, List[Tuple[int, str]]] = {}

# Function to add a task to a priority queue
def add_task(category: str, task: str, priority: int = 0):
    if category not in priority_queues:
        priority_queues[category] = []
    heapq.heappush(priority_queues[category], (priority, task))


# Function to get  the highest priority task fro a priority queue
def get_task(category: str) -> str:
    if category in priority_queues and priority_queues[category]:
        return heapq.heappop(priority_queues[category])[1]
    return "No tasks available" 

# Add tasks to different categories 
add_task("work", "task_1", priority=2)    
add_task("work", "task_2", priority=1)    
add_task("personal", "task_3", priority=3)    
add_task("personal", "task_4", priority=1)    

