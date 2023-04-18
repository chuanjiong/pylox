
import sys

from my_scanner import Scanner
from my_parser import Parser
from my_resolver import Resolver
from my_env import Env
from my_native import native_table

def run(src, resolver, env):
    value = None
    statements = Parser(Scanner(src, env).scan_tokens(), env).parse()
    for statement in statements:
        statement.resolve(resolver)
    for statement in statements:
        value = statement.exec(env)
    return value

def run_file(path):
    print('='*16 + f' run: {path} ' + '='*16)
    with open(path, 'r') as f:
        resolver = Resolver()
        env = Env()
        env.values.update(native_table)
        run(f.read(), resolver, env)

def run_prompt():
    resolver = Resolver()
    env = Env()
    env.values.update(native_table)
    while True:
        print('> ', end='')
        try:
            value = run(input(), resolver, env)
            if value is not None:
                print(f'{value}')
        except KeyboardInterrupt:
            sys.exit()
        except:
            pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        run_prompt()
    else:
        for i in range(1, len(sys.argv)):
            run_file(sys.argv[i])

