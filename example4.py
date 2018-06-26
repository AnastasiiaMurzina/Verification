def function1(b):
    print('1')
    return 0
    print('0')

def function2():
    for i in range(10):
        print(i, 'b')
        function1(i)
        if i == 5:
            continue
            print('after')

def function3(a=0, b):
    print(b)

def function4(a, **b={}):
    print(b.keys())

def main1():
    f = 2 * a
    function1(f)
    function2()

