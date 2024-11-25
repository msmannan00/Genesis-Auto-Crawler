from abc import ABC, abstractmethod

class request_handler(ABC):

  @abstractmethod
  def invoke_trigger(self, p_command, p_data=None):
    pass
