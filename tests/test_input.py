import unittest
import sys
sys.path.append('../')
import parse_input
from parse_input import read_fact, parse_rule

class InputMethods(unittest.TestCase):

    def test_single_fact(self):
        test_input = ["t([instance-of,me,object,t])."]
        fact = read_fact(0, test_input[0], skolems=False)
        self.assertEqual(fact.value, "instance-of")
        self.assertEqual(fact.type, "Fact")
        self.assertEqual(fact.args, ["me", "object", "t"])
    
    def test_single_rule(self):
        rule_input = ["r(1,1,[],kow(if([[identical,A,B]]),then([identical,B,A])))."]
        rule = parse_rule(rule_input[0], {})
        self.assertEqual(rule.index, 1)
        self.assertEqual(rule.arity, 1)
        self.assertEqual(rule.if_terms, [["identical", "A", "B"]])
        self.assertEqual(rule.then_terms, ["identical", "B", "A"])
        self.assertFalse(rule.is_then_or)
        self.assertFalse(rule.has_skolem)
        self.assertEqual(rule.skolems, None)
        self.assertEqual(rule.type, "Rule")
        self.assertEqual(rule.args, [["A", "B"]])
        pass

    def test_single_fact_with_skolem(self):
        skolem_list = {}
        skolem_counter = 1
        test_input = ["t([instance-of,[e,19,[my-thinking,t]],object,t])."]
        fact = read_fact(0, test_input[0], skolems=True, skolem_list=skolem_list, skolem_count=skolem_counter)
        self.assertEqual(fact.value, "instance-of")
        self.assertEqual(fact.type, "Fact")
        self.assertEqual(fact.args, ["sk1", "object", "t"])
        self.assertEqual(len(skolem_list.items()), 1)
        self.assertEqual(skolem_list["sk1"], ["e", "19", ["my-thinking", "t"]])

    def test_single_fact_with_multiple_skolems(self):
        skolem_list = {}
        skolem_counter = 1
        test_input = ["t([instance-of,[e,19,[my-thinking,t]],object,[e,20,[an-object,open-season,timeout]]])."]
        fact = read_fact(0, test_input[0], skolems=True, skolem_list=skolem_list, skolem_count=skolem_counter)
        self.assertEqual(fact.value, "instance-of")
        self.assertEqual(fact.type, "Fact")
        self.assertEqual(fact.args, ["sk1", "object", "sk2"])
        self.assertEqual(len(skolem_list.items()), 2)
        self.assertEqual(skolem_list["sk1"], ["e", "19", ["my-thinking", "t"]])
        self.assertEqual(skolem_list["sk2"], ["e", "20", ["an-object", "open-season", "timeout"]])


if __name__ == '__main__':
    unittest.main()