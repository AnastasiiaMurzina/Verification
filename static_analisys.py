import sys
from keyword import kwlist
import re
operators = '+', '-', '*', '/', '%'
bifs = '=', '!', '<', '>'
binaries = '&', '^', '~', '|'
extra = '(', ',', '.', ')', ' ', ':', '[', ']'
builds = dir (__builtins__)

global funcs
funcs = {}

bads = set([])

def reader(file_name):
    acc = []
    with open(file_name, 'r') as f:
        for line in f:
            acc.append(line.replace('\n', ''))
    return acc


def eraser_comment():
    global lines
    flag = True
    for ix, line in enumerate(lines):
        sharp = line.find('#')
        if sharp != -1 and flag: lines[ix] = line[:sharp]
        if line.find("'''") != -1 and line.find("\"'''\"") == -1: flag ^= True
        if not flag: lines[ix] = ''


def find_defs(lines):
    for ix, i in enumerate(lines):
        if len(i) > 4 and i.replace(' ', '')[0:3] == 'def':
            opened = i.find('(')
            closed = i[::-1].find(')')
            fname = i[4:opened].replace(" ", '')
            params = i[opened+1:-closed-1].replace(' ', '')
            params = params.split(',')
            sparams = set([])
            eq_flag = False
            ssparams, ssparamss = None, None
            for ip in params:
                stars = ip.count('*')
                eq = ip.find('=')
                if eq != -1: eq_flag = True
                if len(ip) > 0 and not ssparams and not ssparamss and (ip[0] != '*' or stars == 0):
                    if ip in set.union(sparams, funcs):
                        print("SyntaxError: duplicate argument '", ip, "' in function definition, line", ix+1)
                        bads.add(fname)
                    if eq == -1 and eq_flag:
                        print('SyntaxError: non-default argument follows defaul argument, line', ix+1)
                        bads.add(fname)
                    else:
                        sparams.add(ip[:eq if eq != -1 else None])
                elif stars >= 1 and ip[0] == '*' and not ssparams and not ssparamss:
                    if ip[1::] in set.union(sparams, funcs):
                        print("SyntaxError: duplicate argument '", ip, "' in function definition, line", ix+1)
                        bads.add(fname)
                    else:
                        sparams.add(ip[1:])
                        ssparams = ip[1:]
                elif stars > 2 and ip[0] == '**' and not ssparamss:
                    if ip[2::] in set.union(sparams, funcs):
                        print("SyntaxError: duplicate argument '", ip, "' in function definition, line", ix + 1)
                        bads.add(fname)
                    else:
                        sparams.add(ip[2:])
                        ssparamss = ip[2:]
            if fname not in bads:
                funcs.update({fname: [[sparams, ssparams, ssparamss], [i.count('=') == 1 for i in params]]})#fix = equation here!
    return funcs


def find_fissues(lines):
    issues = []
    for ix, line in enumerate(lines):
        ex_line = line.replace(' ', '')
        if not (len(ex_line) > 4 and ex_line[0:3] == 'def'):
            for i in (re.split('|'.join(map(re.escape, binaries+bifs+operators+extra+tuple(builds))), line)):
                if i.replace(' ', '') != '' and i in funcs.keys():
                    issues.append([ix, i])
    return issues


def functions_used(fissues):
    used = set([i for _, i in fissues])
    if used != set(funcs.keys()):
        print('There some unused:', set(funcs.keys()).difference(used))


def check_issues(issues, lines): #for example function
    for num, f_isname in issues:
        pos = lines[num].find(f_isname+'(')
        actual_args = lines[num][pos+len(f_isname)+1:lines[num].find(')')].replace(' ', '').split(',')
        print(actual_args)
        if len(funcs[f_isname][0][0]) == len(actual_args):
            pass #it's ok
        else:
            pass # check else


def space_counter(line):
    spaces = 0
    for ix in range(len(line)):
        if line[ix] != ' ':
            break
        spaces += 1
    return spaces


def check_unreach(lines):
    stop_words = ('return', 'break', 'continue', 'yield')
    for ix, line in enumerate(lines):
        for i in stop_words:
            if line.startswith(i+' '):
                if ix + 1 < len(lines) and space_counter(line) == space_counter(lines[ix+1]):
                    print('WARNING: Unreachable line', ix + 1, ':', lines[ix+1])
                break

if __name__ == '__main__':
    name = sys.argv[1]
    lines = reader(name)
    eraser_comment()
    check_unreach(lines)
    funcs = find_defs(lines)
    issues = find_fissues(lines)
    functions_used(issues)
