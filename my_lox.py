
import sys

from my_scanner import Scanner
from my_parser import Parser
from my_resolver import Resolver
from my_env import Env

def run(src, resolver, env):
    value = None
    statements = Parser(Scanner(src, env).scan_tokens(), env).parse()
    print('+'*16 + ' ast ' + '+'*16)
    for statement in statements:
        print(f'{statement}')
    print('-'*16 + ' ast ' + '-'*16)
    print('+'*16 + ' exec ' + '+'*16)
    for statement in statements:
        statement.resolve(resolver)
    for statement in statements:
        value = statement.exec(env)
    print('-'*16 + ' exec ' + '-'*16)
    return value

def run_file(path):
    print('='*16 + f' run: {path} ' + '='*16)
    with open(path, 'r') as f:
        run(f.read(), Resolver(), Env())

def run_prompt():
    resolver = Resolver()
    env = Env()
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

