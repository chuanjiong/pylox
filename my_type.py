
import time
import my_env
from my_error import *

def report_error(operator, msg):
    report(operator.line, f'at {operator.lexme}', msg)
    raise

class Func:
    def __init__(self, name, parameters, body, env, is_init):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.env = env
        self.is_init = is_init

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
            if self.is_init:
                return env.get_at(0, 'this')
            return value.value
        if self.is_init:
            return env.get_at(0, 'this')

    def bind(self, instance):
        env = my_env.Env(self.env)
        env.define('this', instance)
        return Func(self.name, self.parameters, self.body, env, self.is_init)

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

class Instance:
    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def __repr__(self):
        return f'{self.cls} instance'

    def get(self, name):
        if name.lexme in self.fields:
            return self.fields[name.lexme]
        method = self.cls.get_method(name.lexme)
        if method is not None:
            return method.bind(self)
        report_error(name, f'Undefined property {name.lexme}.')

    def set(self, name, value):
        self.fields[name.lexme] = value

class Cls:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __repr__(self):
        return f'class {self.name}'

    def arity(self):
        init = self.get_method('init')
        if init is not None:
            return init.arity()
        return 0

    def call(self, arguments):
        instance = Instance(self)
        init = self.get_method('init')
        if init is not None:
            return init.bind(instance).call(arguments)
        return instance

    def get_method(self, name):
        if name in self.methods:
            return self.methods[name]
        return None

