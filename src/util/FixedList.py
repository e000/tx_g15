class FixedList(list):
    """
        A list of N size, it will automatically truncate itself when the list grows too big.
    """

    def __init__(self, size):
        self.size = size
        list.__init__(self)

    def append(self, item):
        while len(self) >= self.size:
            self.pop(0)
        list.append(self, item)

    def extend(self, iterable):
        for i in iterable:
            self.append(i)

    def prepend(self, item):
        while len(self) >= self.size:
            self.pop()
        list.insert(item, 0)

    def update(self, list):
        self[:] = list[:5]

    def clear(self):
        self[:] = []