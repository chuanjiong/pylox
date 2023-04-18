
from my_token import Token
from my_env import Env

class ReturnValue(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value

class Func:
    def __init__(self, name, parameters, body, env, is_init=False):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.env = env
        self.is_init = is_init

    def __repr__(self):
        return f'(function {self.name})'

    def arity(self):
        return len(self.parameters)

    def call(self, arguments):
        env = Env(self.env)
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
        return None

    def bind(self, instance):
        env = Env(self.env)
        env.define('this', instance)
        return Func(self.name, self.parameters, self.body, env, self.is_init)

class Cls:
    def __init__(self, name, sp, methods):
        self.name = name
        self.sp = sp
        self.methods = methods

    def __repr__(self):
        return f'(class {self.name} < {self.sp})'

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
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k in self.methods:
            return self.methods[k]
        elif self.sp is not None:
            return self.sp.get_method(k)
        else:
            return None

class Instance:
    def __init__(self, cls):
        self.cls = cls
        self.fields = {}

    def __repr__(self):
        return f'(instance {self.cls})'

    def get(self, name, env):
        if name.lexme in self.fields:
            return self.fields[name.lexme]
        method = self.cls.get_method(name.lexme)
        if method is not None:
            return method.bind(self)
        env.runtime_error(name, f'Undefined property {name.lexme}.')

    def set(self, name, value):
        self.fields[name.lexme] = value

