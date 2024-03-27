import unittest
import sys
sys.path.append('../')
from parse_input import read_fact, read_rules
from prover import linkStep, modusPonens

class ModusPonens(unittest.TestCase):
    """
    need to ensure that the correct fact is generated and everything is fine with it
    """
    def test_simple_mp(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(61,1,[],kow(if([[instance-of,A,B,C]]),then([universal,B])))."]
        fact = read_fact(0, fact_input[0], False)
        rules, rule_dict = read_rules(rule_input)
        valid_facts = []
        valid_facts = linkStep([fact], rules, rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): [rules[61]]})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "process", "C": "t"}, 61)])
        facts = modusPonens(valid_facts, [fact], rules)
        self.assertEqual(len(facts), 2)
        self.assertEqual(facts[1].value, "universal")
        self.assertEqual(facts[1].args, ['process'])
        self.assertEqual(facts[1].index, 1)

    def test_simple_mp_with_multiple_facts(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(61,1,[],kow(if([[instance-of,A,B,C]]),then([universal,B]))).",
                      "r(62,1,[],kow(if([[instance-of,A,B,C]]),then([particular,A])))."]
        fact = read_fact(0, fact_input[0], False)
        rules, rule_dict = read_rules(rule_input)
        valid_facts = []
        valid_facts = linkStep([fact], rules, rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): [rules[61], rules[62]]})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "process", "C": "t"}, 61), (fact, {"A": "my-thinking", "B": "process", "C": "t"}, 62)])
        facts = modusPonens(valid_facts, [fact], rules)
        self.assertEqual(len(facts), 3)
        self.assertEqual(facts[1].value, "universal")
        self.assertEqual(facts[1].args, ['process'])
        self.assertEqual(facts[1].index, 1)
        self.assertEqual(facts[2].value, "particular")
        self.assertEqual(facts[2].args, ['my-thinking'])
        self.assertEqual(facts[2].index, 2)

    def test_dont_derive_existing_facts(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(61,1,[],kow(if([[instance-of,A,B,C]]),then([universal,B]))).",
                      "r(62,1,[],kow(if([[instance-of,A,B,C]]),then([particular,A]))).",
                      "r(63,1,[],kow(if([[instance-of,B,A,C]]),then([particular,B])))."]
        fact = read_fact(0, fact_input[0], False)
        rules, rule_dict = read_rules(rule_input)
        valid_facts = []
        valid_facts = linkStep([fact], rules, rule_dict, valid_facts)
        print(rules)
        self.assertEqual(len(rules.items()), 3)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): [rules[61], rules[62], rules[63]]})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "process", "C": "t"}, 61), (fact, {"A": "my-thinking", "B": "process", "C": "t"}, 62),(fact, {"B": "my-thinking", "A": "process", "C": "t"}, 63)])
        facts = modusPonens(valid_facts, [fact], rules)
        self.assertEqual(len(facts), 3)
        self.assertEqual(facts[1].value, "universal")
        self.assertEqual(facts[1].args, ['process'])
        self.assertEqual(facts[1].index, 1)
        self.assertEqual(facts[2].value, "particular")
        self.assertEqual(facts[2].args, ['my-thinking'])
        self.assertEqual(facts[2].index, 2)

    def test_mp_with_multiple_args(self):
        pass
    def test_dont_conclude_on_then_or(self):
        pass

    #I guess this technically would count as Modus Tollens but it doesn't really matter
    def test_set_new_fact_to_false(self):
        pass

    def test_mp_with_skolems(self):
        pass

    def test_mp_with_nested_skolems_of_depth_1(self):
        pass

class ModusTollens(unittest.TestCase):
    def test_simple_mt(self):
        pass


if __name__ == '__main__':
    unittest.main()