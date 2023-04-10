
hadError = False

def report(line, where, msg):
    print(f'[line {line}] Error {where}: {msg}')
    hadError = True

def error(line, msg):
    report(line, '', msg)

