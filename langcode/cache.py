class Cache:

    def __init__(self, size):
        self.size = size
        self.array = [None] * size
        self.pointer = 0

    @property
    def next_pointer(self):
        return 0 if (self.pointer + 1) >= self.size else self.pointer + 1

    def put(self, T):
        self.array[self.next_pointer] = T
        self.pointer = self.next_pointer

    """
    between 1 and size, inclusize
    """
    def nth_prev(self, n):
        if not 1 <= n <= self.size:
            raise Exception("argument n is " + n + " but is expected 1<=n<=size" )
        index = self.pointer - n
        while index < 0:
            index += self.size
        return self.array[index]

