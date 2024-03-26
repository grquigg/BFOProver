class Node:
    def __init__(self, index: int, type: str, values: list, args: list):
        self.index = 0
        self.type = type
        self.neighbors = {}
        self.args = args

class FactNode(Node):
    def __init__(self, index: int, value: str, args: list):
        super().__init__(index, "Fact", [value], args)
        self.value = value
        self.rules_from = []
        self.is_true = True

    