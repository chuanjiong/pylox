
import time
from my_type import Func

class NativeFunc(Func):
    def __init__(self, name, arity):
        self.name = name
        self.arity_ = arity

    def __repr__(self):
        return f'native function {self.name}()'

    def arity(self):
        return self.arity_

class ClockFunc(NativeFunc):
    def __init__(self, name, arity):
        super().__init__(name, arity)

    def call(self, arguments):
        return time.time()


