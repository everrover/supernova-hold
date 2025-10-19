from abc import ABC, abstractmethod

class EncBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def input_options(self, data, options={}):
        return

    @abstractmethod
    def encode(self, data, options={}):
        pass