
from my_token import TokenType
from my_type import Func, Cls, Instance
from my_resolver import ClsType

class Expr:
    pass

class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def resolve(self, resolver):
        pass

    def eval(self, env):
        return self.value

class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.right})'

    def resolve(self, resolver):
        self.right.resolve(resolver)

    def eval(self, env):
        right = self.right.eval(env)
        if self.operator.type_ == TokenType.MINUS:
            env.check_operands(self.operator, [right], float, 'Operand must be a number.')
            return -right
        else: # TokenType.BANG
            return not env.is_truthy(right)

class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.left} {self.right})'

    def resolve(self, resolver):
        self.left.resolve(resolver)
        self.right.resolve(resolver)

    def eval(self, env):
        left = self.left.eval(env)
        right = self.right.eval(env)
        if self.operator.type_ == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float) or isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                env.runtime_error(self.operator, 'Operands must be two numbers or two strings.')
        elif self.operator.type_ == TokenType.MINUS:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left - right
        elif self.operator.type_ == TokenType.STAR:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left * right
        elif self.operator.type_ == TokenType.SLASH:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left / right
        elif self.operator.type_ == TokenType.GREATER:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left > right
        elif self.operator.type_ == TokenType.GREATER_EQUAL:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left >= right
        elif self.operator.type_ == TokenType.LESS:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left < right
        elif self.operator.type_ == TokenType.LESS_EQUAL:
            env.check_operands(self.operator, [left, right], float, 'Operand must be a number.')
            return left <= right
        elif self.operator.type_ == TokenType.BANG_EQUAL:
            return left != right
        else: # TokenType.EQUAL_EQUAL
            return left == right

class Logical(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f'({self.operator} {self.left} {self.right})'

    def resolve(self, resolver):
        self.left.resolve(resolver)
        self.right.resolve(resolver)

    def eval(self, env):
        left = self.left.eval(env)
        if self.operator.type_ == TokenType.OR:
            if env.is_truthy(left):
                return left
        else: # TokenType.AND
            if not env.is_truthy(left):
                return left
        return self.right.eval(env)

class Grouping(Expr):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'(group {self.expr})'

    def resolve(self, resolver):
        self.expr.resolve(resolver)

    def eval(self, env):
        return self.expr.eval(env)

class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'(id {self.name})'

    def resolve(self, resolver):
        self.resolver = resolver
        if resolver.check(self.name, False):
            resolver.resolve_error(self.name, f'Can not read local variable in its own initializer.')
        else:
            resolver.resolve_local(self, self.name)

    def eval(self, env):
        if self in self.resolver.locals:
            return env.get_at(self.resolver.locals[self], self.name)
        else:
            return env.get_global(self.name)

class Assign(Expr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f'(= {self.name} {self.expr})'

    def resolve(self, resolver):
        self.resolver = resolver
        self.expr.resolve(resolver)
        resolver.resolve_local(self, self.name)

    def eval(self, env):
        value = self.expr.eval(env)
        if self in self.resolver.locals:
            env.assign_at(self.resolver.locals[self], self.name, value)
        else:
            env.assign_global(self.name, value)
        return value

class This(Expr):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'this'

    def resolve(self, resolver):
        self.resolver = resolver
        if resolver.current_class == ClsType.NONE:
            resolver.resolve_error(self.name, f'Can not use this outside of a class.')
        else:
            resolver.resolve_local(self, self.name)

    def eval(self, env):
        if self in self.resolver.locals:
            return env.get_at(self.resolver.locals[self], self.name)
        else:
            return env.get_global(self.name)

class Super(Expr):
    def __init__(self, sp, method):
        self.sp = sp
        self.method = method

    def __repr__(self):
        return f'(super {self.method})'

    def resolve(self, resolver):
        self.resolver = resolver
        if resolver.current_class == ClsType.NONE:
            resolver.resolve_error(self.sp, f'Can not use super outside of a class.')
        elif resolver.current_class != ClsType.SUBCLASS:
            resolver.resolve_error(self.sp, f'Can not use super in a class with no superclass.')
        else:
            resolver.resolve_local(self, self.sp)

    def eval(self, env):
        distance = self.resolver.locals[self]
        sp = env.get_at(distance, self.sp)
        this = env.get_at(distance-1, 'this')
        method = sp.get_method(self.method)
        if method is None:
            env.runtime_error(self.method, f'Undefined property {self.method}.')
        return method.bind(this)

class Call(Expr):
    def __init__(self, callee, arguments, paren):
        self.callee = callee
        self.arguments = arguments
        self.paren = paren

    def __repr__(self):
        return f'({self.callee} {self.arguments})'

    def resolve(self, resolver):
        self.callee.resolve(resolver)
        for argument in self.arguments:
            argument.resolve(resolver)

    def eval(self, env):
        callee = self.callee.eval(env)
        if not isinstance(callee, (Func, Cls)):
            env.runtime_error(self.paren, f'Can only call functions and classes.')
        arguments = []
        for argument in self.arguments:
            arguments.append(argument.eval(env))
        if len(arguments) != callee.arity():
            env.runtime_error(self.paren, f'Expected {callee.arity()} arguments but got {len(arguments)}.')
        return callee.call(arguments)

class Get(Expr):
    def __init__(self, expr, name):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return f'(get {self.expr} {self.name})'

    def resolve(self, resolver):
        self.expr.resolve(resolver)

    def eval(self, env):
        expr = self.expr.eval(env)
        if not isinstance(expr, Instance):
            env.runtime_error(self.name, 'Only instances have properties.')
        return expr.get(self.name, env)

class Set(Expr):
    def __init__(self, expr, name, value):
        self.expr = expr
        self.name = name
        self.value = value

    def __repr__(self):
        return f'(set {self.expr} {self.name} {self.value})'

    def resolve(self, resolver):
        self.expr.resolve(resolver)
        self.value.resolve(resolver)

    def eval(self, env):
        expr = self.expr.eval(env)
        if not isinstance(expr, Instance):
            env.runtime_error(self.name, 'Only instances have fields.')
        value = self.value.eval(env)
        expr.set(self.name, value)
        return value

