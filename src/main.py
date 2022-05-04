def tribonnaci(n):
    if n == 1:
        return 1
    elif n == 2:
        return 1
    elif n == 3:
        return 2
    else:
        return tribonnaci(n-1) + tribonnaci(n-2) + tribonnaci(n-3)

def main():
    for i in range(1, 22):
        print(tribonnaci(i))

if __name__ == '__main__':
    main()
