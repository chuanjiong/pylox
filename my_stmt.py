
import my_env
import my_type
import my_scope

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def exec(self):
        return self.expr.eval()

    def resolve(self):
        self.expr.resolve()

class Print(Stmt):
    def __init__(self, value):
        self.value = value

    def exec(self):
        value = self.value.eval()
        print(f'{value}')

    def resolve(self):
        self.value.resolve()

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def exec(self):
        if self.initializer is None:
            my_env.current_env.define(self.name, None)
        else:
            my_env.current_env.define(self.name, self.initializer.eval())

    def resolve(self):
        my_scope.declare(self.name)
        if self.initializer is not None:
            self.initializer.resolve()
        my_scope.define(self.name)

class Block(Stmt):
    def __init__(self, statements):
        self.statements = statements

    def exec(self, env=None):
        prev_env = my_env.current_env
        if env is None:
            my_env.current_env = my_env.Env(prev_env)
        else:
            my_env.current_env = env
        try:
            for statement in self.statements:
                statement.exec()
        finally:
            my_env.current_env = prev_env

    def resolve(self):
        my_scope.begin_scope()
        for statement in self.statements:
            statement.resolve()
        my_scope.end_scope()

class If(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def exec(self):
        if my_env.isTruthy(self.condition.eval()):
            self.then_branch.exec()
        elif self.else_branch is not None:
            self.else_branch.exec()

    def resolve(self):
        self.condition.resolve()
        self.then_branch.resolve()
        if self.else_branch is not None:
            self.else_branch.resolve()

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def exec(self):
        while my_env.isTruthy(self.condition.eval()):
            self.body.exec()

    def resolve(self):
        self.condition.resolve()
        self.body.resolve()

class Function(Stmt):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def exec(self):
        my_env.current_env.define(self.name, my_type.Func(self.name, self.parameters, self.body, my_env.current_env, False))

    def resolve(self):
        my_scope.declare(self.name)
        my_scope.define(self.name)
        prev_func = my_scope.current_function
        my_scope.current_function = my_scope.FuncType.FUNCTION
        my_scope.begin_scope()
        for parameter in self.parameters:
            my_scope.declare(parameter)
            my_scope.define(parameter)
        self.body.resolve()
        my_scope.end_scope()
        my_scope.current_function = prev_func

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def exec(self):
        value = None
        if self.value is not None:
            value = self.value.eval()
        raise my_type.ReturnValue(value)

    def resolve(self):
        if my_scope.current_function == my_scope.FuncType.NONE:
            my_scope.report_error(self.keyword, 'Can not return from top-level code.')
        if self.value is not None:
            if my_scope.current_function == my_scope.FuncType.INITIALIZER:
                my_scope.report_error(self.keyword, 'Can not return a value from an initializer.')
            self.value.resolve()

class Class(Stmt):
    def __init__(self, name, sp, methods):
        self.name = name
        self.sp = sp
        self.methods = methods

    def exec(self):
        sp = None
        if self.sp is not None:
            sp = self.sp.eval()
            if not isinstance(sp, my_type.Cls):
                my_scope.report_error(self.sp.name, 'Superclass must be a class.')
        my_env.current_env.define(self.name, None)
        env = my_env.current_env
        if self.sp is not None:
            env = my_env.Env(my_env.current_env)
            env.define('super', sp)
        methods = {}
        for method in self.methods:
            methods[method.name.lexme] = my_type.Func(method.name, method.parameters, method.body, env, method.name.lexme=='init')
        if self.sp is not None:
            my_env.current_env = env.enclosing
        my_env.current_env.assign(self.name, my_type.Cls(self.name, sp, methods))

    def resolve(self):
        prev_cls = my_scope.current_class
        my_scope.current_class = my_scope.ClsType.CLASS
        my_scope.declare(self.name)
        my_scope.define(self.name)
        if self.sp is not None:
            my_scope.current_class = my_scope.ClsType.SUBCLASS
            if self.name.lexme == self.sp.name.lexme:
                my_scope.report_error(self.sp.name, 'A class can not inherit from itself.')
            self.sp.resolve()
        if self.sp is not None:
            my_scope.begin_scope()
            my_scope.scopes[-1]['super'] = True
        my_scope.begin_scope()
        # my_scope.scopes[-1]['this'] = True
        for method in self.methods:
            prev_func = my_scope.current_function
            my_scope.current_function = my_scope.FuncType.METHOD
            if method.name.lexme == 'init':
                my_scope.current_function = my_scope.FuncType.INITIALIZER
            my_scope.begin_scope()
            my_scope.scopes[-1]['this'] = True #...
            for parameter in method.parameters:
                my_scope.declare(parameter)
                my_scope.define(parameter)
            method.body.resolve()
            my_scope.end_scope()
            my_scope.current_function = prev_func
        my_scope.end_scope()
        if self.sp is not None:
            my_scope.end_scope()
        my_scope.current_class = prev_cls

