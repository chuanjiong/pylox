
from enum import Enum, auto
from my_error import scan_error

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

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

        self.token_map = {
            '(': lambda: self.add_token(TokenType.LEFT_PAREN),
            ')': lambda: self.add_token(TokenType.RIGHT_PAREN),
            '{': lambda: self.add_token(TokenType.LEFT_BRACE),
            '}': lambda: self.add_token(TokenType.RIGHT_BRACE),
            '.': lambda: self.add_token(TokenType.DOT),
            ',': lambda: self.add_token(TokenType.COMMA),
            ';': lambda: self.add_token(TokenType.SEMICOLON),
            '+': lambda: self.add_token(TokenType.PLUS),
            '-': lambda: self.add_token(TokenType.MINUS),
            '*': lambda: self.add_token(TokenType.STAR),
            '/': lambda: self.advance_slash(),
            '!': lambda: self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG),
            '=': lambda: self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL),
            '>': lambda: self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER),
            '<': lambda: self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS),
            '"': lambda: self.advance_string(),
            '\n': lambda: self.advance_line(),
            ' ': lambda: None,
            '\t': lambda: None,
            '\r': lambda: None,
        }

        self.key_map = {
            'and': lambda: self.add_token(TokenType.AND),
            'class': lambda: self.add_token(TokenType.CLASS),
            'else': lambda: self.add_token(TokenType.ELSE),
            'false': lambda: self.add_token(TokenType.FALSE),
            'for': lambda: self.add_token(TokenType.FOR),
            'fun': lambda: self.add_token(TokenType.FUN),
            'if': lambda: self.add_token(TokenType.IF),
            'nil': lambda: self.add_token(TokenType.NIL),
            'or': lambda: self.add_token(TokenType.OR),
            'print': lambda: self.add_token(TokenType.PRINT),
            'return': lambda: self.add_token(TokenType.RETURN),
            'super': lambda: self.add_token(TokenType.SUPER),
            'this': lambda: self.add_token(TokenType.THIS),
            'true': lambda: self.add_token(TokenType.TRUE),
            'var': lambda: self.add_token(TokenType.VAR),
            'while': lambda: self.add_token(TokenType.WHILE),
        }

    def is_digit(self, c):
        return c in "0123456789"

    def is_alpha_(self, c):
        return c in "_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    def is_end(self):
        return self.current >= len(self.source)

    def advance(self):
        if self.is_end():
            return '\0'
        c = self.source[self.current]
        self.current += 1
        return c

    def match(self, c):
        if self.is_end():
            return False
        if self.source[self.current] != c:
            return False
        self.current += 1
        return True

    def peek(self):
        if self.is_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current+1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]

    def add_token(self, type_, literal=None):
        self.tokens.append(Token(type_, self.source[self.start:self.current], literal, self.line))

    def advance_line(self):
        self.line += 1

    def advance_slash(self):
        if self.match('/'):
            while not self.is_end() and self.peek() != '\n':
                self.advance()
        else:
            self.add_token(TokenType.SLASH)

    def advance_number(self):
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def advance_string(self):
        while not self.is_end() and self.peek() != '"':
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_end():
            scan_error(self.line, f'Unterminated string.')
            return
        self.advance()
        self.add_token(TokenType.STRING, self.source[self.start+1:self.current-1])

    def advance_identifier(self):
        while self.is_digit(self.peek()) or self.is_alpha_(self.peek()):
            self.advance()
        k = self.source[self.start:self.current]
        if k in self.key_map:
            self.key_map[k]()
        else:
            self.add_token(TokenType.IDENTIFIER)

    def scan_token(self):
        c = self.advance()
        if c in self.token_map:
            self.token_map[c]()
        elif self.is_digit(c):
            self.advance_number()
        elif self.is_alpha_(c):
            self.advance_identifier()
        else:
            scan_error(self.line, f'Unexpected character {c}.')

    def scan_tokens(self):
        while not self.is_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens


if __name__ == '__main__':
    s = Scanner('var x = 4 * (3 + 4) + 8; if (x > 3) { y = x*4;}else{y=4;} return a;\n / "abc" 3.5 09.1 @ this super_ super abc //aabc')
    t = s.scan_tokens()
    for i in t:
        print(f'{i}')

