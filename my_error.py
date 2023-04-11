
hadError = False

def report(line, where, msg):
    print(f'[line {line}] Error {where}: {msg}')
    hadError = True

def error(line, msg):
    report(line, '', msg)

def scan_error(line, msg):
    print(f'[Line {line}] scan error: {msg}')

