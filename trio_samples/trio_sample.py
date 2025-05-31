import trio
import math
from functools import partial
from typing import Callable, Any


def is_prime(n: int) -> bool:
    """
    Check if a number is prime.
    This function can be CPU intensive for large numbers.

    Args:
        n (int): The number to check for primality.

    Returns:
        bool: True if n is prime, False otherwise.
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

async def generic_async_runner_for_sync_task(
        sync_callable: Callable[..., Any],
        *args: list[Any],   # This should be an Object
        result_container: list | None=None,
):
    """
    A generic async wrapper that executes a given synchronous callable
    in a separate thread using trio.to_thread.run_sync.

    Args:
        sync_callable (Callable[..., Any]): The synchronous function to run.
        *args (list[Any]): Arguments to pass to the synchronous function.
    """
    # For logging or identification purposes
    task_name = getattr(sync_callable, '__name__', 'unknown_task')
    print(f"Starting task: {task_name} with args: {args}")

    try:
        # The core of the wrapper: run the provided sync_callable in a thread
        result = await trio.to_thread.run_sync(
            sync_callable, *args, cancellable=True
        )
        print(f"Task {task_name} with args: {args} completed with result: {result}")
        result_container.append({"id": task_name, "result": result})
        
    except trio.Cancelled:
        print(f"Task {task_name} was cancelled.")
        

async def main(result_container: list):
    async with trio.open_nursery() as nursery:
        # Example usage of the generic async runner for a sync task
        task1 = partial(generic_async_runner_for_sync_task, is_prime, 1532021237514419, result_container=result_container)
        nursery.start_soon(task1)
        
        # Wait for all tasks to complete
        task2 = partial(generic_async_runner_for_sync_task, is_prime, 31, result_container=result_container)
        nursery.start_soon(task2)

if __name__ == "__main__":
    result_container = []
    trio.run(main, result_container)
    print("Results:", result_container)