import unittest
import sys
sys.path.append('../')
from parse_input import read_fact, parse_rule
from prover import linkStep
#all of the test cases for making sure that the linking logic actually works
class LinkingMethods(unittest.TestCase):

    def query_rules(self):
        pass

    def test_simple_link(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(61,1,[],kow(if([[instance-of,A,B,C]]),then([universal,B])))."]
        fact = read_fact(0, fact_input[0], False)
        rule = parse_rule(rule_input[0])
        self.assertEqual(len(rule.values), 1)
        self.assertEqual(fact.value, rule.values[0])
        rule_dict = {"instance-of": [0]}
        valid_facts = []
        valid_facts = linkStep([fact], [rule], rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): rule})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "process", "C": "t"})])

    def test_complex_link(self):
        pass

    def test_tollens_link(self):
        pass

    def test_then_or_link(self):
        pass

    def test_rules_cannot_link_together(self):
        pass

    def test_facts_cannot_link_together(self):
        pass


if __name__ == '__main__':
    unittest.main()