
from my_error import parse_error
from my_scanner import TokenType
import my_expr
import my_stmt

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        return self.tokens[self.current]

    def check(self, type_):
        return self.peek().type_ == type_

    def match(self, *types):
        if self.peek().type_ in types:
            self.current += 1
            return True
        return False

    def consume(self, type_, msg):
        if self.check(type_):
            self.current += 1
            return self.tokens[self.current-1]
        else:
            parse_error(self.tokens[self.current], msg)

    def previous(self):
        return self.tokens[self.current-1]

    '''
    expression      ->      assignment

    assignment      ->      (call'.')? IDENTIFIER '=' assignment
                        |   logic_or

    logic_or        ->      logic_and ('or' logic_and)*

    logic_and       ->      equality ('and' equality)*

    equality        ->      comparison (('!=' | '==') comparison)*

    comparison      ->      term (('>' | '>=' | '<' | '<=') term)*

    term            ->      factor (('+' | '-') factor)*

    factor          ->      unary (('*' | '/') unary)*

    unary           ->      ('!' | '-') unary
                        |   call

    call            ->      primary (('(' arguments? ')') | ('.' IDENTIFIER))*

    primary         ->      'true' | 'false' | 'nil' | NUMBER | STRING | IDENTIFIER
                        |   'this' | 'super' '.' IDENTIFIER | '(' expression ')'

    arguments       ->      expression (',' expression)*
    '''

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.match(TokenType.EQUAL):
            value = self.assignment()
            if isinstance(expr, my_expr.Variable):
                return my_expr.Assign(expr.name, value)
            elif isinstance(expr, my_expr.Get):
                return my_expr.Set(expr.expr, expr.name, value)
            parse_error(self.tokens[self.current], f'Invalid assignment target.')
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = my_expr.Logical(expr, operator, right)
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = my_expr.Logical(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return my_expr.Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, f'Expect property name after ".".')
                expr = my_expr.Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, expr):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    parse_error(self.tokens[self.current], f'Can not have more than 255 arguments.')
                arguments.append(self.expression())
        paren = self.consume(TokenType.RIGHT_PAREN, f'Expect ) after arguments.')
        return my_expr.Call(expr, arguments, paren)

    def primary(self):
        if self.match(TokenType.TRUE):
            return my_expr.Literal(True)
        elif self.match(TokenType.FALSE):
            return my_expr.Literal(False)
        elif self.match(TokenType.NIL):
            return my_expr.Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return my_expr.Literal(self.previous().literal)
        elif self.match(TokenType.IDENTIFIER):
            return my_expr.Variable(self.previous())
        elif self.match(TokenType.THIS):
            return my_expr.This(self.previous())
        elif self.match(TokenType.SUPER):
            sp = self.previous()
            self.consume(TokenType.DOT, f'Expect . after super.')
            method = self.consume(TokenType.IDENTIFIER, f'Expect superclass method name.')
            return my_expr.Super(sp, method)
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, f'Expect ) after expression.')
            return my_expr.Grouping(expr)
        parse_error(self.tokens[self.current], f'Expect expression.')

    '''
    statement               ->      print_statement
                                |   block_statement
                                |   if_statement
                                |   while_statement
                                |   for_statement
                                |   return_statement
                                |   expression_statement

    print_statement         ->      'print' expression ';'

    block_statement         ->      '{' declaration* '}'

    if_statement            ->      'if' '(' expression ')' statement ('else' statement)?

    while_statement         ->      'while' '(' expression ')' statement

    for_statement           ->      'for' '(' (var_declaration | expression_statement | ';')
                                              expression? ';'
                                              expression? ')' statement

    return_statement        ->      'return' expression? ';'

    expression_statement    ->      expression ';'
    '''

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return self.block_statement()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        return self.expression_statement()

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after expression.')
        return my_stmt.Expression(expr)

    def print_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after print expression.')
        return my_stmt.Print(expr)

    def block_statement(self):
        statements = []
        while not self.check(TokenType.EOF) and not self.check(TokenType.RIGHT_BRACE):
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, f'Expect }} after block.')
        return my_stmt.Block(statements)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, f'Expect ( after if.')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, f'Expect ) after if condition.')
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return my_stmt.If(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, f'Expect ( after while.')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, f'Expect ) after while condition.')
        body = self.statement()
        return my_stmt.While(condition, body)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, f'Expect ( after for.')
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after loop condition.')
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, f'Expect ) after for clauses.')
        body = self.statement()
        if increment is not None:
            body = my_stmt.Block([body, my_stmt.Expression(increment)])
        if condition is None:
            condition = my_expr.Literal(True)
        body = my_stmt.While(condition, body)
        if initializer is not None:
            body = my_stmt.Block([initializer, body])
        return body

    def return_statement(self):
        ret = self.previous()
        expr = None
        if not self.check(TokenType.SEMICOLON):
            expr = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after return expression.')
        return my_stmt.Return(ret, expr)

    '''
    declaration             ->      var_declaration
                                |   fun_declaration
                                |   class_declaration
                                |   statement

    var_declaration         ->      'var' IDENTIFIER ('=' expression)? ';'

    fun_declaration         ->      'fun' function

    class_declaration       ->      'class' IDENTIFIER ('<' IDENTIFIER)? '{' function* '}'

    function                ->      IDENTIFIER '(' parameters? ')' block_statement

    parameters              ->      IDENTIFIER (',' IDENTIFIER)*
    '''

    def declaration(self):
        if self.match(TokenType.VAR):
            return self.var_declaration()
        elif self.match(TokenType.FUN):
            return self.fun_declaration('function')
        elif self.match(TokenType.CLASS):
            return self.class_declaration()
        return self.statement()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, f'Expect variable name.')
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after variable declaration.')
        return my_stmt.Var(name, initializer)

    def fun_declaration(self, type_):
        name = self.consume(TokenType.IDENTIFIER, f'Expect {type_} name.')
        self.consume(TokenType.LEFT_PAREN, f'Expect ( after {type_} name.')
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, f'Expect parameter name.'))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    parse_error(self.tokens[self.current], f'Can not have more than 255 parameters.')
                parameters.append(self.consume(TokenType.IDENTIFIER, f'Expect parameter name.'))
        self.consume(TokenType.RIGHT_PAREN, f'Expect ) after parameters.')
        self.consume(TokenType.LEFT_BRACE, f'Expect {{ before {type_} body.')
        body = self.block_statement()
        return my_stmt.Function(name, parameters, body)

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, f'Expect class name.')
        sp = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, f'Expect superclass name.')
            sp = my_expr.Variable(self.previous())
        self.consume(TokenType.LEFT_BRACE, f'Expect {{ before class body.')
        methods = []
        while not self.check(TokenType.EOF) and not self.check(TokenType.RIGHT_BRACE):
            methods.append(self.fun_declaration('method'))
        self.consume(TokenType.RIGHT_BRACE, f'Expect }} after class body.')
        return my_stmt.Class(name, sp, methods)

    def parse(self):
        statements = []
        while not self.check(TokenType.EOF):
            statements.append(self.declaration())
        return statements


if __name__ == '__main__':
    from my_scanner import Scanner
    s = Parser(Scanner('3*(4+5)-4 ; print 1;').scan_tokens()).parse()
    print(s)

