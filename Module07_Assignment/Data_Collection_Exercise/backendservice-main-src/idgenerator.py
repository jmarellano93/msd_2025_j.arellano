"""
This module provides ID generation capabilities.
It defines an abstract base class for ID generators and concrete implementations.
"""
from abc import ABC, abstractmethod
import uuid
import random
import logging

module_logger = logging.getLogger(__name__)

class IDGenerator(ABC):
    """Abstract base class for ID generators."""

    @abstractmethod
    def get_id(self) -> str:
        """
        Generates and returns a unique ID.

        Returns:
            str: The generated unique ID.
        """
        pass # pylint: disable=unnecessary-pass (Pylint sometimes flags pass in abstract methods)

class AlphaNumericIDGenerator(IDGenerator):
    """Generates a UUID1-based alphanumeric ID."""
    def get_id(self) -> str:
        """
        Generates a unique ID based on UUID version 1.

        Returns:
            str: A UUID string.
        """
        generated_id = str(uuid.uuid1())
        module_logger.debug(f"AlphaNumericIDGenerator created ID: {generated_id}")
        return generated_id

class NumericIDGenerator(IDGenerator):
    """Generates a random numeric ID."""
    def get_id(self) -> str: # Changed to return string to match AlphaNumeric for consistency if used interchangeably
        """
        Generates a random integer ID as a string.

        The range is between 10,000 and 100,000,000,000 (inclusive).
        Returns:
            str: A string representation of the random numeric ID.
        """
        # Original returned int, but common practice is string IDs.
        # If int is strictly needed, type hint and return type should be int.
        # For this exercise, making it string for consistency.
        random_int_id = random.randint(10000, 100000000000)
        generated_id = str(random_int_id)
        module_logger.debug(f"NumericIDGenerator created ID: {generated_id}")
        return generated_id

# Example usage (can be removed or kept for simple testing)
if __name__ == '__main__':
    # Configure basic logging for direct script execution test
    logging.basicConfig(level=logging.DEBUG)

    alpha_gen = AlphaNumericIDGenerator()
    num_gen = NumericIDGenerator()

    module_logger.info("Testing ID Generators:")
    module_logger.info(f"AlphaNumeric ID 1: {alpha_gen.get_id()}")
    module_logger.info(f"AlphaNumeric ID 2: {alpha_gen.get_id()}")
    module_logger.info(f"Numeric ID 1: {num_gen.get_id()}")
    module_logger.info(f"Numeric ID 2: {num_gen.get_id()}")