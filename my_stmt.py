
import my_env
import my_type

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def exec(self):
        return self.expr.eval()

class Print(Stmt):
    def __init__(self, value):
        self.value = value

    def exec(self):
        value = self.value.eval()
        print(f'{value}')

class Var(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def exec(self):
        if self.initializer is None:
            my_env.current_env.define(self.name, None)
        else:
            my_env.current_env.define(self.name, self.initializer.eval())

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

class While(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def exec(self):
        while my_env.isTruthy(self.condition.eval()):
            self.body.exec()

class Function(Stmt):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def exec(self):
        my_env.current_env.define(self.name, my_type.Func(self.name, self.parameters, self.body, my_env.current_env))

class Return(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def exec(self):
        value = None
        if self.value is not None:
            value = self.value.eval()
        raise my_type.ReturnValue(value)

