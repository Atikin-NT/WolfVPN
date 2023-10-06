class A:
    pass

class B(A):
    pass

class C(A):
    def print_p(self):
        print(A.p)

def main():
    b = B()
    A.p = 5
    c = C()
    print(b.p, c.p)
    print(id(b.p), id(c.p))
    print(id(b), id(c))
    c.print_p()


if __name__ == '__main__':
    main()
