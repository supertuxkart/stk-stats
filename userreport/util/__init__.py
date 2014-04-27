class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))
