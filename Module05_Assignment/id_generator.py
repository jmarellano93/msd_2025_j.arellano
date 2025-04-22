# You could use your browser to interact with a rest API or use Postman. Downloaded chrome extension.
# We need an ID generator so that whenever a datapoint is retrieved from the backend, we want to
# give that datapoint a unique identifier.

from abc import ABC, abstractmethod
import uuid
import random

class IDGenerator(ABC):

  @abstractmethod
  def get_id(self):
    pass

class AlphaNumericIDGenerator(IDGenerator):
  def get_id(self):
    return uuid.uuid1()

class NumericIDGenerator(IDGenerator):
  def get_id(self):
    return random.randint(10000, 100000000000)