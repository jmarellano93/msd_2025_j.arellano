"""
Example script for demonstrating memory profiling with memory_profiler.
This script defines a function that allocates memory and is decorated with @profile.
To run: python -m memory_profiler memory.py
"""
import logging
from memory_profiler import profile

# Configure logging for this script if run directly
# This won't affect Flask app's logging unless this script modifies root logger settings widely.
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
script_logger = logging.getLogger(__name__)

@profile
def allocate_memory_example():
    """
    Example function that allocates memory by creating lists.
    Decorated with @profile for line-by-line memory analysis when
    run with 'python -m memory_profiler memory.py'.

    Returns:
        tuple: A tuple containing two lists (a, b).
    """
    script_logger.info("Starting memory allocation example...")
    # Allocate a list with a range of numbers
    list_a = [i for i in range(100000)] # Increased size slightly for more visible allocation
    script_logger.debug(f"List 'a' created with {len(list_a)} elements.")

    # Allocate another list with squares of numbers
    list_b = [i ** 2 for i in range(100000)]
    script_logger.debug(f"List 'b' created with {len(list_b)} elements.")

    script_logger.info("Memory allocation example finished.")
    return list_a, list_b

if __name__ == "__main__":
    script_logger.info("Running memory.py script directly...")
    # Call the function to trigger memory profiling if script is run with memory_profiler module
    results_a, results_b = allocate_memory_example()
    script_logger.info(
        f"allocate_memory_example executed. List A items: {len(results_a)}, "
        f"List B items: {len(results_b)}"
    )
    script_logger.info(
        "Check console output for memory_profiler report if run via "
        "'python -m memory_profiler memory.py'"
    )
