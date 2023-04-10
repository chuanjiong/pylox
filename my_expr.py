
import my_type
from my_scanner import *
import my_env
import my_scope

def report_error(operator, msg):
    report(operator.line, f'at {operator.lexme}', msg)
    raise

def check_operands(operator, operands, type_, msg):
    for i in operands:
        if not isinstance(i, type_):
            report_error(operator, msg)
    return True

class Expr:
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def eval(self):
        return self.value

    def resolve(self):
        pass

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.right})'

    def eval(self):
        right = self.right.eval()
        if self.operator.type_ == TokenType.MINUS:
            check_operands(self.operator, [right], float, 'Operand must be a number.')
            return -right
        else: # TokenType.BANG
            return not my_env.isTruthy(right)

    def resolve(self):
        self.right.resolve()

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.left} {self.right})'

    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        if self.operator.type_ == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float) or isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                report_error(self.operator, 'Operands must be two numbers or two strings.')
        elif self.operator.type_ == TokenType.MINUS:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left - right
        elif self.operator.type_ == TokenType.STAR:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left * right
        elif self.operator.type_ == TokenType.SLASH:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left / right
        elif self.operator.type_ == TokenType.GREATER:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left > right
        elif self.operator.type_ == TokenType.GREATER_EQUAL:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left >= right
        elif self.operator.type_ == TokenType.LESS:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left < right
        elif self.operator.type_ == TokenType.LESS_EQUAL:
            check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left <= right
        elif self.operator.type_ == TokenType.BANG_EQUAL:
            return left != right
        else: # TokenType.EQUAL_EQUAL
            return left == right

    def resolve(self):
        self.left.resolve()
        self.right.resolve()

class Grouping(Expr):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'(group {self.expr})'

    def eval(self):
        return self.expr.eval()

    def resolve(self):
        self.expr.resolve()

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'(id {self.name})'

    def eval(self):
        # return my_env.current_env.get(self.name)
        if self in my_scope.my_locals:
            return my_env.current_env.get_at(my_scope.my_locals[self], self.name)
        else:
            return my_env.global_env.get(self.name)

    def resolve(self):
        if not my_scope.is_empty() and not my_scope.check(self.name):
            report_error(self.name, 'Can not read local variable in its own initializer.')
        my_scope.resolve_local(self, self.name)

class Assign(Expr):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f'(= {self.name} {self.value})'

    def eval(self):
        value = self.value.eval()
        # my_env.current_env.assign(self.name, value)
        if self in my_scope.my_locals:
            return my_env.current_env.assign_at(my_scope.my_locals[self], self.name, value)
        else:
            return my_env.global_env.assign(self.name, value)
        return value

    def resolve(self):
        self.value.resolve()
        my_scope.resolve_local(self, self.name)

class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.left} {self.right})'

    def eval(self):
        left = self.left.eval()
        if self.operator.type_ == TokenType.OR:
            if my_env.isTruthy(left):
                return left
        else: # TokenType.AND
            if not my_env.isTruthy(left):
                return left
        return self.right.eval()

    def resolve(self):
        self.left.resolve()
        self.right.resolve()

class Call(Expr):
    def __init__(self, callee, arguments, paren):
        self.callee = callee
        self.arguments = arguments
        self.paren = paren

    def __repr__(self):
        return f'({self.callee} {self.arguments})'

    def eval(self):
        callee = self.callee.eval()
        if not isinstance(callee, my_type.Func):
            report_error(self.paren, 'Can only call functions and classes.')
        arguments = []
        for argument in self.arguments:
            arguments.append(argument.eval())
        if len(arguments) != callee.arity():
            report_error(self.paren, f'Expected {callee.arity()} arguments but got {len(arguments)}.')
        return callee.call(arguments)

    def resolve(self):
        self.callee.resolve()
        for argument in self.arguments:
            argument.resolve()


if __name__ == '__main__':
    e = Binary(Unary(Token(TokenType.MINUS, '-', None, 1), Literal(float(123))), Token(TokenType.STAR, '*', None, 1), Grouping(Literal(float(45.67))))
    print(e)
    print(e.eval())
    e = Variable(Token(TokenType.IDENTIFIER, 'x', None, 1))
    print(e)
    e = Logical(Literal(False), Token(TokenType.AND, 'and', None, 1), Literal(float(0)))
    print(e)
    print(e.eval())

