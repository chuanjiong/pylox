
from enum import Enum, auto
from my_token import Token

class FuncType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()

class ClsType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

class Resolver:
    def __init__(self):
        self.scopes = []
        self.locals = {}
        self.current_function = FuncType.NONE
        self.current_class = ClsType.NONE

    def resolve_error(self, token, msg):
        print(f'[Line {token.line}] resolve error at {token.lexme}, {msg}')
        raise

    def check(self, name, value):
        if len(self.scopes) == 0:
            return False
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if k not in self.scopes[-1]:
            return False
        return self.scopes[-1][k] == value

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if len(self.scopes) == 0:
            return
        if name.lexme in self.scopes[-1]:
            self.resolve_error(name, 'Already a variable with this name in this scope.')
        self.scopes[-1][name.lexme] = False

    def define(self, name):
        if isinstance(name, Token):
            k = name.lexme
        else:
            k = name
        if len(self.scopes) == 0:
            return
        self.scopes[-1][k] = True

    def resolve_local(self, expr, name):
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexme in self.scopes[i]:
                self.locals[expr] = len(self.scopes) - 1 - i
                return

