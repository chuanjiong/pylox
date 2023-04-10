
import time
import my_env

class Func:
    def __init__(self, name, parameters, body, env):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.env = env

    def __repr__(self):
        return f'function {self.name}()'

    def arity(self):
        return len(self.parameters)

    def call(self, arguments):
        env = my_env.Env(self.env)
        for i, arg in enumerate(arguments):
            env.define(self.parameters[i], arg)
        try:
            self.body.exec(env)
        except ReturnValue as value:
            return value.value

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

class ReturnValue(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

