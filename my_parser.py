
import my_expr
import my_stmt
from my_scanner import *
from my_error import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        return self.tokens[self.current]

    def check(self, type_):
        if self.peek().type_ == type_:
            return True
        return False

    def match(self, types):
        if self.peek().type_ in types:
            self.current += 1
            return True
        return False

    def consume(self, type_, msg):
        if self.peek().type_ == type_:
            self.current += 1
            return self.tokens[self.current-1]
        else:
            self.report_error(msg)

    def previous(self):
        return self.tokens[self.current-1]

    def report_error(self, msg):
        if self.peek().type_ == TokenType.EOF:
            report(self.peek().line, f'at end', msg)
        else:
            report(self.peek().line, f'at {self.peek().lexme}', msg)
        raise

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.or_expr()
        if self.match([TokenType.EQUAL]):
            value = self.assignment()
            if isinstance(expr, my_expr.Variable):
                return my_expr.Assign(expr.name, value)
            elif isinstance(expr, my_expr.Get):
                return my_expr.Set(expr.expr, expr.name, value)
            self.report_error('Invalid assignment target.')
        return expr

    def or_expr(self):
        expr = self.and_expr()
        while self.match([TokenType.OR]):
            operator = self.previous()
            right = self.and_expr()
            expr = my_expr.Logical(expr, operator, right)
        return expr

    def and_expr(self):
        expr = self.equality()
        while self.match([TokenType.AND]):
            operator = self.previous()
            right = self.equality()
            expr = my_expr.Logical(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL]):
            operator = self.previous()
            right = self.comparison()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]):
            operator = self.previous()
            right = self.term()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match([TokenType.MINUS, TokenType.PLUS]):
            operator = self.previous()
            right = self.factor()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match([TokenType.SLASH, TokenType.STAR]):
            operator = self.previous()
            right = self.unary()
            expr = my_expr.Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match([TokenType.BANG, TokenType.MINUS]):
            operator = self.previous()
            right = self.unary()
            return my_expr.Unary(operator, right)
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match([TokenType.LEFT_PAREN]):
                expr = self.finish_call(expr)
            elif self.match([TokenType.DOT]):
                name = self.consume(TokenType.IDENTIFIER, 'Expect property name after ".".')
                expr = my_expr.Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, expr):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match([TokenType.COMMA]):
                if len(arguments) >= 255:
                    self.report_error('Can not have more than 255 arguments.')
                arguments.append(self.expression())
        paren = self.consume(TokenType.RIGHT_PAREN, 'Expect ) after arguments.')
        return my_expr.Call(expr, arguments, paren)

    def primary(self):
        if self.match([TokenType.FALSE]):
            return my_expr.Literal(False)
        if self.match([TokenType.TRUE]):
            return my_expr.Literal(True)
        if self.match([TokenType.NIL]):
            return my_expr.Literal(None)
        if self.match([TokenType.NUMBER, TokenType.STRING]):
            return my_expr.Literal(self.previous().literal)
        if self.match([TokenType.LEFT_PAREN]):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, f'Expect ) after expression.')
            return my_expr.Grouping(expr)
        if self.match([TokenType.THIS]):
            return my_expr.This(self.previous())
        if self.match([TokenType.IDENTIFIER]):
            return my_expr.Variable(self.previous())
        self.report_error('Expect expression.')

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after expression.')
        return my_stmt.Expression(expr)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after value.')
        return my_stmt.Print(value)

    def block_statement(self):
        statements = []
        # while self.peek().type_ != TokenType.EOF and self.peek().type_ != TokenType.RIGHT_BRACE:
        while not self.check(TokenType.EOF) and not self.check(TokenType.RIGHT_BRACE):
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, 'Expect } after block.')
        return my_stmt.Block(statements)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect ( after if.')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ) after if condition.')
        then_branch = self.statement()
        else_branch = None
        if self.match([TokenType.ELSE]):
            else_branch = self.statement()
        return my_stmt.If(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect ( after while.')
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ) after while condition.')
        body = self.statement()
        return my_stmt.While(condition, body)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect ( after for.')
        if self.match([TokenType.SEMICOLON]):
            initializer = None
        elif self.match([TokenType.VAR]):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        # if self.peek().type_ != TokenType.SEMICOLON:
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ; after loop condition.')
        increment = None
        # if self.peek().type_ != TokenType.RIGHT_PAREN:
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ) after for clauses.')
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
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ; after return value.')
        return my_stmt.Return(keyword, value)

    def statement(self):
        if self.match([TokenType.PRINT]):
            return self.print_statement()
        if self.match([TokenType.LEFT_BRACE]):
            return self.block_statement()
        if self.match([TokenType.IF]):
            return self.if_statement()
        if self.match([TokenType.WHILE]):
            return self.while_statement()
        if self.match([TokenType.FOR]):
            return self.for_statement()
        if self.match([TokenType.RETURN]):
            return self.return_statement()
        return self.expression_statement()

    def var_declaration(self):
        self.consume(TokenType.IDENTIFIER, f'Expect variable name.')
        name = self.previous()
        initializer = None
        if self.match([TokenType.EQUAL]):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, f'Expect ; after variable declaration.')
        return my_stmt.Var(name, initializer)

    def fun_declaration(self, type_):
        name = self.consume(TokenType.IDENTIFIER, f'Expect {type_} name.')
        self.consume(TokenType.LEFT_PAREN, f'Expect ( after {type_} name.')
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, 'Expect parameter name.'))
            while self.match([TokenType.COMMA]):
                if len(parameters) >= 255:
                    self.report_error('Can not have more than 255 parameters.')
                parameters.append(self.consume(TokenType.IDENTIFIER, 'Expect parameter name.'))
        self.consume(TokenType.RIGHT_PAREN, 'Expect ) after parameters.')
        self.consume(TokenType.LEFT_BRACE, f'Expect {{ before {type_} body.')
        body = self.block_statement()
        return my_stmt.Function(name, parameters, body)

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, f'Expect class name.')
        self.consume(TokenType.LEFT_BRACE, f'Expect {{ before class body.')
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.check(TokenType.EOF):
            methods.append(self.fun_declaration('method'))
        self.consume(TokenType.RIGHT_BRACE, f'Expect }} after class body.')
        return my_stmt.Class(name, methods)

    def declaration(self):
        if self.match([TokenType.VAR]):
            return self.var_declaration()
        if self.match([TokenType.FUN]):
            return self.fun_declaration('function')
        if self.match([TokenType.CLASS]):
            return self.class_declaration()
        return self.statement()

    def parse(self):
        statements = []
        # while self.peek().type_ != TokenType.EOF:
        while not self.check(TokenType.EOF):
            statements.append(self.declaration())
        return statements


if __name__ == '__main__':
    p = Parser(Scanner('3*(4+5)-4 ; print 1;').scan_tokens())
    e = p.parse()
    print(e)

