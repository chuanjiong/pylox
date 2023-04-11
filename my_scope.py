
from enum import Enum, auto
from my_error import *

class FuncType(Enum):
    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()

class ClsType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

scopes = []
my_locals = {}

current_function = FuncType.NONE
current_class = ClsType.NONE

def report_error(name, msg):
    report(name.line, f'at {name.lexme}', msg)
    raise

def is_empty():
    return len(scopes) == 0

def begin_scope():
    scopes.append({})

def end_scope():
    scopes.pop()

def declare(name):
    if len(scopes) == 0:
        return
    if name.lexme in scopes[-1]:
        report_error(name, 'Already a variable with this name in this scope.')
    scopes[-1][name.lexme] = False

def define(name):
    if len(scopes) == 0:
        return
    scopes[-1][name.lexme] = True

def check(name):
    return scopes[-1][name.lexme]

def resolve_local(expr, name):
    for i in range(len(scopes)-1, -1, -1):
        if name.lexme in scopes[i]:
            my_locals[expr] = len(scopes) - 1 - i
            return

