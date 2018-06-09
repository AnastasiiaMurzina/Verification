import sys
from keyword import kwlist
import re
operators = '+', '-', '*', '/', '%'
bifs = '=', '!', '<', '>'
binaries = '&', '^', '~', '|'
extra = '(', ',', '.', ')', ' ', ':', '[', ']'
builds = dir (__builtins__)

def reader(file_name):
    acc = []
    with open(file_name, 'r') as f:
        for line in f:
            acc.append(line.replace('\n', ''))
    return acc


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
            if line.count(i):
                if ix + 1 < len(lines) and space_counter(line) == space_counter(lines[ix+1]):
                    print('WARNING: Unreachable line', ix + 1, ':', lines[ix+1])
                break


def find_assign(lines):
    assigns = []
    for line in lines:
        if line.count('=') == 1:
            line = line.replace(' ', '').split('=')
            flag = False
            for i in operators+bifs+binaries:
                if i in line[0]:
                    flag = True
                    assigns.append(False)
                    break
            if not flag: assigns.append(True)
        else:
            assigns.append(False)
    assigns = [i for i, j in enumerate(assigns) if j]
    return assigns


def assign_for(lines):
    fors = []
    ix = 0
    for line in lines:
        if line.count('for'):
            line = line.replace('for', '').replace(' ', '').replace(':', '').split('in')
            line.insert(0, ix)
            fors.append(line)
        ix += 1
    return fors


def namespaces_search(lines):
    '''
    :return: {'global': {'parent':None, 'vars': []}, }
    '''
    namespace = {'global': {'parent': None, 'vars': [], 'spaces': 0}}
    cur_space = 'global'
    explicit_assigns = find_assign(lines)
    for_assigns = assign_for(lines)
    fors_count = 0
    if_count = 0
    assigns = explicit_assigns+for_assigns

    def checker_usage(right):
        xs = right
        flags = [False for _ in xs]
        sp = cur_space

        while not (namespace[sp].get('parent') is None) and not all(flags):
            for i in range(len(flags)):
                if not flags[i]:
                    if xs[i] in namespace[sp]['vars']:
                        flags[i] = True
            if not (namespace[sp]['parent'] is None):
                sp = namespace[sp]['parent']
        for i in range(len(flags)):
            if not flags[i]:
                if xs[i] in namespace[sp]['vars']:
                    flags[i] = True
        if not (namespace[sp]['parent'] is None):
            sp = namespace[sp]['parent']
        if not all(flags):
            unfind = list(filter(lambda x: xs[x] != '', [i for i, j in enumerate(flags) if not j]))
            print('ERROR: line', ix, ':', [xs[i] for i in unfind], ' vars are not expected to use')
            return False
        return True

    for ix in range(len(lines)):
        if lines[ix] != '' and lines[ix].replace(" ", '')[0] != '#':
            c = space_counter(lines[ix])
            if lines[ix] != '' and c < namespace[cur_space]['spaces'] and namespace[cur_space]['parent']:
                cur_space = namespace[cur_space]['parent']
            if ix in assigns:
                left, right = lines[ix].replace(" ", '').split('=')
                right = re.split('|'.join(map(re.escape, binaries+bifs+operators+extra+tuple(kwlist)+tuple(reversed(sorted(namespace.keys()))))), right)
                r_check = list(filter(lambda x: not x.isdigit(), right))
                if left.count(","):
                    new_vars = left.replace(" ", '').split(',')
                    if checker_usage(r_check):
                        for j in new_vars:
                            namespace[cur_space]['vars'].append(j)
                else:
                    if checker_usage(r_check):
                        namespace[cur_space]['vars'].append(left)
            elif lines[ix].count('def '):
                c1 = space_counter(lines[ix+1])
                line = lines[ix].replace(" ", '').replace('def', '').replace(':', '').split('(')
                parent = cur_space
                cur_space = line[0]
                if line[1] != ')':
                    line = line[1].replace(')', '')
                    if line.count(','):
                        args = line.split(',')
                        namespace.update({cur_space: {'parent': parent, 'vars': args, 'spaces': c1}})
                    else:
                        arg = line
                        namespace.update({cur_space: {'parent': parent, 'vars': [arg], 'spaces': c1}})
                else:
                    namespace.update({cur_space: {'parent': parent, 'vars': [], 'spaces': c1}})
            elif lines[ix].count('if '):
                if ix+1 < len(lines) and space_counter(lines[ix+1]) > space_counter(lines[ix]):
                    namespace.update({'if'+str(if_count): {'parent': cur_space, 'vars': [], 'spaces': space_counter(lines[ix+1])}})
                    cur_space = 'if' + str(if_count)
                    if_count += 1
            elif lines[ix].count('for '):
                if ix+1 < len(lines) and space_counter(lines[ix+1]) > space_counter(lines[ix]):
                    line = lines[ix][lines[ix].find('for')+4:lines[ix].find('in')]
                    if line.count(","):
                        args = line.replace(" ", '').split(',')
                    else:
                        args = [line.replace(" ", '')]
                    namespace.update({'for'+str(fors_count): {'parent': cur_space, 'vars': args, 'spaces': space_counter(lines[ix+1])}})
                    cur_space = 'for' + str(fors_count)
                    fors_count += 1
            else:
                line = re.split('|'.join(map(re.escape, binaries+bifs+operators+extra)), lines[ix])
                def fil_fun(x):
                    return x != "" and not((x[0] == "'" and x[-1] == "'") or x in kwlist or x in builds or x in namespace.keys() or x.isdigit())
                line = list(filter(lambda x: fil_fun(x), line))
                checker_usage(line)
        # print(namespace)

if __name__ == '__main__':
    name = sys.argv[1]
    lines = reader(name)
    check_unreach(lines)
    namespaces_search(lines)
