
from my_type import Func, ReturnValue, Cls
from my_resolver import FuncType, ClsType
from my_env import Env

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'[{self.expr}]'

    def resolve(self, resolver):
        self.expr.resolve(resolver)

    def exec(self, env):
        return self.expr.eval(env)

class Print(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'[print {self.expr}]'

    def resolve(self, resolver):
        self.expr.resolve(resolver)

    def exec(self, env):
        print(f'{self.expr.eval(env)}')

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def __repr__(self):
        return f'[var {self.name} {self.initializer}]'

    def resolve(self, resolver):
        resolver.declare(self.name)
        if self.initializer is not None:
            self.initializer.resolve(resolver)
        resolver.define(self.name)

    def exec(self, env):
        if self.initializer is None:
            env.define(self.name, None)
        else:
            env.define(self.name, self.initializer.eval(env))

class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f'[block {[statement for statement in self.statements]}]'

    def resolve(self, resolver):
        resolver.begin_scope()
        for statement in self.statements:
            statement.resolve(resolver)
        resolver.end_scope()

    def exec(self, env):
        env = Env(env)
        for statement in self.statements:
            statement.exec(env)

class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def __repr__(self):
        return f'[if {self.condition} {self.then_branch} {self.else_branch}]'

    def resolve(self, resolver):
        self.condition.resolve(resolver)
        self.then_branch.resolve(resolver)
        if self.else_branch is not None:
            self.else_branch.resolve(resolver)

    def exec(self, env):
        if env.is_truthy(self.condition.eval(env)):
            self.then_branch.exec(env)
        elif self.else_branch is not None:
            self.else_branch.exec(env)

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f'[While {self.condition} {self.body}]'

    def resolve(self, resolver):
        self.condition.resolve(resolver)
        self.body.resolve(resolver)

    def exec(self, env):
        while env.is_truthy(self.condition.eval(env)):
            self.body.exec(env)

class Function(Stmt):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return f'[fun {self.name} {self.parameters} {self.body}]'

    def resolve(self, resolver):
        resolver.declare(self.name)
        resolver.define(self.name)
        prev_func = resolver.current_function
        resolver.current_function = FuncType.FUNCTION
        resolver.begin_scope()
        for parameter in self.parameters:
            resolver.declare(parameter)
            resolver.define(parameter)
        self.body.resolve(resolver)
        resolver.end_scope()
        resolver.current_function = prev_func

    def exec(self, env):
        env.define(self.name, Func(self.name, self.parameters, self.body, env))

class Return(Stmt):
    def __init__(self, ret, expr):
        self.ret = ret
        self.expr = expr

    def __repr__(self):
        return f'[return {self.expr}]'

    def resolve(self, resolver):
        if resolver.current_function == FuncType.NONE:
            resolver.resolve_error(self.ret, 'Can not return from top-level code.')
        if self.expr is not None:
            if resolver.current_function == FuncType.INITIALIZER:
                resolver.resolve_error(self.ret, 'Can not return a value from an initializer.')
            self.expr.resolve(resolver)

    def exec(self, env):
        value = None
        if self.expr is not None:
            value = self.expr.eval(env)
        raise ReturnValue(value)

class Class(Stmt):
    def __init__(self, name, sp, methods):
        self.name = name
        self.sp = sp
        self.methods = methods

    def __repr__(self):
        return f'[class {self.name} < {self.sp} {self.methods}]'

    def resolve(self, resolver):
        prev_cls = resolver.current_class
        resolver.current_class = ClsType.CLASS
        resolver.declare(self.name)
        resolver.define(self.name)
        if self.sp is not None:
            resolver.current_class = ClsType.SUBCLASS
            if self.name.lexme == self.sp.name.lexme:
                resolver.resolve_error(self.sp.name, 'A class can not inherit from itself.')
            self.sp.resolve(resolver)
        if self.sp is not None:
            resolver.begin_scope()
            resolver.define('super')
        resolver.begin_scope()
        resolver.define('this')
        for method in self.methods:
            prev_func = resolver.current_function
            resolver.current_function = FuncType.METHOD
            if method.name.lexme == 'init':
                resolver.current_function = FuncType.INITIALIZER
            resolver.begin_scope()
            for parameter in method.parameters:
                resolver.declare(parameter)
                resolver.define(parameter)
            method.body.resolve(resolver)
            resolver.end_scope()
            resolver.current_function = prev_func
        resolver.end_scope()
        if self.sp is not None:
            resolver.end_scope()
        resolver.current_class = prev_cls

    def exec(self, env):
        sp = None
        if self.sp is not None:
            sp = self.sp.eval(env)
            if not isinstance(sp, Cls):
                env.runtime_error(self.sp.name, 'Superclass must be a class.')
        env.define(self.name, None)
        if self.sp is not None:
            sp_env = Env(env)
            sp_env.define('super', sp)
        else:
            sp_env = env
        methods = {}
        for method in self.methods:
            methods[method.name.lexme] = Func(method.name, method.parameters, method.body, sp_env, method.name.lexme=='init')
        env.assign(self.name, Cls(self.name, sp, methods))

