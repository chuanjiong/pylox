
import time
from my_type import Func

class ClockNativeFunc(Func):
    def __init__(self, arity):
        self.arity_ = arity

    def __repr__(self):
        return f'(native clock)'

    def arity(self):
        return self.arity_

    def call(self, arguments):
        return time.time()

class OpenNativeFunc(Func):
    def __init__(self, arity):
        self.arity_ = arity

    def __repr__(self):
        return f'(native open)'

    def arity(self):
        return self.arity_

    def call(self, arguments):
        return open(arguments[0])

class ReadNativeFunc(Func):
    def __init__(self, arity):
        self.arity_ = arity

    def __repr__(self):
        return f'(native read)'

    def arity(self):
        return self.arity_

    def call(self, arguments):
        return arguments[0].read()

class CloseNativeFunc(Func):
    def __init__(self, arity):
        self.arity_ = arity

    def __repr__(self):
        return f'(native close)'

    def arity(self):
        return self.arity_

    def call(self, arguments):
        return arguments[0].close()


native_table = {
    'clock': ClockNativeFunc(0),
    'open': OpenNativeFunc(1),
    'read': ReadNativeFunc(1),
    'close': CloseNativeFunc(1),
}

