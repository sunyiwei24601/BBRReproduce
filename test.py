import _thread

def fair(x1, x2):
    s = x1 + x2
    top = (s/x1 + s/x2) ** 2
    down = 2 * ((s/x1)**2 + (s/x2)**2)
    return top/down
if __name__ == '__main__':
    print(fair(21,73))
    