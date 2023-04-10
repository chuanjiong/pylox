
import sys
from my_scanner import *
from my_parser import *
from my_error import *
import my_type
import my_env

my_env.global_env.define(Token(TokenType.IDENTIFIER, 'clock', None, 0), my_type.ClockFunc('clock', 0))

def run(src):
    try:
        value = None
        statements = Parser(Scanner(src).scan_tokens()).parse()
        for statement in statements:
            value = statement.resolve()
        for statement in statements:
            value = statement.exec()
        return value
    except KeyboardInterrupt:
        sys.exit()
    except my_type.ReturnValue as e:
        print(f'return value: {e.value}')
    except:
        print(f'runtime error')

def runFile(path):
    with open(path, 'r') as f:
        run(f.read())

def runPrompt():
    while True:
        print('> ', end = '')
        value = run(input())
        if value is not None:
            print(f'{value}')


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print(f'Usage: {sys.argv[0]} [script]')
    elif len(sys.argv) == 2:
        runFile(sys.argv[1])
    else:
        runPrompt()

