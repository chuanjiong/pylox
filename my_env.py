
from my_error import *
from my_scanner import *
import my_type

def isTruthy(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return True

class Env:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name.lexme] = value

    def get(self, name):
        if name.lexme in self.values:
            return self.values[name.lexme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        error(name.line, f'Undefined variable {name.lexme}.')
        raise

    def assign(self, name, value):
        if name.lexme in self.values:
            self.values[name.lexme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            error(name.line, f'Undefined variable {name.lexme}.')
            raise

global_env = Env()

# global_env.define(Token(TokenType.IDENTIFIER, 'clock', None, 0), my_type.ClockFunc('clock', 0))

current_env = global_env

