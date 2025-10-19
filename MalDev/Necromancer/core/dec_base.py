from abc import ABC, abstractmethod

class DecBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def input_options(self, data, options={}):
        return

    @abstractmethod
    def decode(self):
        pass