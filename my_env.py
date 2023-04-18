
from my_token import Token

class BaseEnv:
    def scan_error(self, line, msg):
        print(f'[Line {line}] scan error: {msg}')
        raise

    def parse_error(self, token, msg):
        print(f'[Line {token.line}] parse error at {token.lexme}, {msg}')
        raise

    def runtime_error(self, token, msg):
        print(f'[Line {token.line}] runtime error at {token.lexme}, {msg}')
        raise

    def is_truthy(self, value):
        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        else:
            return True

    def check_operands(self, operator, operands, type_, msg):
        for o in operands:
            if not isinstance(o, type_):
                self.runtime_error(operator, msg)

class Env(BaseEnv):
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
        if enclosing is None:
            self.global_env = self
        else:
            self.global_env = enclosing.global_env

    def define(self, name, value):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        self.values[k] = value

    def get(self, name):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k in self.values:
            return self.values[k]
        elif self.enclosing is not None:
            return self.enclosing.get(name)
        else:
            super().runtime_error(name, f'Undefined variable {k}.')

    def assign(self, name, value):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k in self.values:
            self.values[k] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            super().runtime_error(name, f'Undefined variable {k}.')

    def get_at(self, distance, name):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env.get(name)

    def assign_at(self, distance, name, value):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env.assign(name, value)

    def get_global(self, name):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k in self.global_env.values:
            return self.global_env.values[k]
        else:
            super().runtime_error(name, f'Undefined variable {k}.')

    def assign_global(self, name, value):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k in self.global_env.values:
            self.global_env.values[k] = value
        else:
            super().runtime_error(name, f'Undefined variable {k}.')

