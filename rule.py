import utils
from utils import display
from node import Node

class RuleNode(Node): # a rule has a list of terms
    def __init__(self, index, if_terms, then_terms, has_skolem, skolems):
        super().__init__(index, "Rule", None, None)
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
        self.values = [term[0] for term in self.if_terms]
        self.args = [term[1:] for term in self.if_terms]

    def is_then_or(self):
        #if each term in the list of then_terms of a rule is itself a list, then it's a then-or
        lists = [i for i in range(len(self.then_terms)) if isinstance(self.then_terms[i], list)]
        if(len(lists) == len(self.then_terms)):
            self.is_then_or = True
        else:
            self.is_then_or = False

    def __str__(self):
        return "if({}), then({})".format(self.if_terms, self.then_terms)
    
    #here's where a bit more can be leveraged in terms of the way that formatting strings work
    def match(self, fact_terms, clause_num):
        clause = self.if_terms[clause_num]
        # Check if lengths are equal
        display(f"Length of fact terms: {len(fact_terms)}", "debug", utils.DEBUG)
        display(f"Length of clause: {len(clause)}", "debug", utils.DEBUG)
        if len(fact_terms) != len(clause):
            return False, {}
        display("Length of terms equal", "debug", utils.DEBUG)
        var_mapping = {}
        for p, i in zip(clause, fact_terms):
            # Check if it's a variable in the pattern
            if p.isupper() and len(p) == 1:
                var_mapping[p] = i
            elif p != i:
                return False, {}
    
        return True, var_mapping


