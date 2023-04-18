
import sys

from my_scanner import Scanner
from my_parser import Parser
from my_resolver import Resolver
from my_env import Env

#my_env.global_env.define(Token(TokenType.IDENTIFIER, 'clock', None, 0), my_type.ClockFunc('clock', 0))

def run(src, resolver, env):
    try:
        value = None
        statements = Parser(Scanner(src, env).scan_tokens(), env).parse()
        for statement in statements:
            print(f'{statement}')
        for statement in statements:
            value = statement.resolve(resolver)
        for statement in statements:
            value = statement.exec(env)
        return value
    except KeyboardInterrupt:
        sys.exit()

def runFile(path):
    resolver = Resolver()
    env = Env()
    with open(path, 'r') as f:
        run(f.read(), resolver, env)

def runPrompt():
    resolver = Resolver()
    env = Env()
    while True:
        print('> ', end = '')
        value = run(input(), resolver, env)
        if value is not None:
            print(f'{value}')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print(f'Usage: {sys.argv[0]} [script]')
    elif len(sys.argv) == 2:
        runFile(sys.argv[1])
    else:
        runPrompt()

