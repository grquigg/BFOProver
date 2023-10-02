class Rule(): # a rule has a list of terms
    def __init__(self, index, if_terms, then_terms, has_skolem, skolems):
        self.if_terms = if_terms
        self.then_terms = then_terms
        self.index = int(index)
        self.arity = len(self.if_terms)
        self.is_then_or()
        self.antecedents = 0
        self.has_skolem = has_skolem
        self.skolems = skolems
        if(self.is_then_or):
            self.antecedents = len(self.then_terms)
        else:
            self.antecedents = 1

    def is_then_or(self):
        #if each term in the list of then_terms of a rule is itself a list, then it's a then-or
        lists = [i for i in range(len(self.then_terms)) if isinstance(self.then_terms[i], list)]
        if(len(lists) == len(self.then_terms)):
            self.is_then_or = True
        else:
            self.is_then_or = False

    def __str__(self):
        return "if({}), then({})".format(self.if_terms, self.then_terms)