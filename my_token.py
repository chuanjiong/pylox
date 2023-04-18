
from enum import Enum, auto

class TokenType(Enum):
    LEFT_PAREN = auto()     # (
    RIGHT_PAREN = auto()    # )
    LEFT_BRACE = auto()     # {
    RIGHT_BRACE = auto()    # }
    DOT = auto()            # .
    COMMA = auto()          # ,
    SEMICOLON = auto()      # ;
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    BANG = auto()           # !
    BANG_EQUAL = auto()     # !=
    EQUAL = auto()          # =
    EQUAL_EQUAL = auto()    # ==
    GREATER = auto()        # >
    GREATER_EQUAL = auto()  # >=
    LESS = auto()           # <
    LESS_EQUAL = auto()     # <=
    NUMBER = auto()         # 数字
    STRING = auto()         # 字符串
    IDENTIFIER = auto()     # 标识符
    # 关键字
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FOR = auto()
    FUN = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    # 结束标志
    EOF = auto()

class Token:
    def __init__(self, type_, lexme, literal, line):
        self.type_ = type_
        self.lexme = lexme
        self.literal = literal # 字面值：数字float、字符串str
        self.line = line

    def __repr__(self):
        return f'{self.type_} {self.lexme} {self.literal}'

    def __str__(self):
        return f'{self.lexme}'

