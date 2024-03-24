import unittest
import sys
sys.path.append('../')
import parse_input
from parse_input import read_fact, parse_rule

class InputMethods(unittest.TestCase):

    # def test_single_fact(self):
    #     test_input = ["t([instance-of,me,object,t])."]
    #     fact = read_fact(0, test_input[0], skolems=False)
    #     self.assertEqual(fact.value, "instance-of")
    #     self.assertEqual(fact.type, "Fact")
    #     self.assertEqual(fact.args, ["me", "object", "t"])
    
    def test_single_rule(self):
        rule_input = ["r(1,1,[],kow(if([[identical,A,B]]),then([identical,B,A])))."]
        rule = parse_rule(rule_input[0], {})
        # self.assertEqual(rule.index, 1)
        # self.assertEqual(rule.arity, 1)
        # self.assertEqual(rule.if_terms, [["identical", "A", "B"]])
        # self.assertEqual(rule.then_terms, ["identical", "B", "A"])
        # self.assertFalse(rule.is_then_or)
        # self.assertFalse(rule.has_skolem)
        # self.assertEqual(rule.skolems, None)
        # self.assertEqual(rule.type, "Rule")
        # self.assertEqual(rule.args, [["A", "B"]])
        pass
    def test_single_rule_with_skolem(self):
        rule_input = ["r(108,1,[19],kow(if([[instance-of,B,history,A]]),then([history-of,B,[e,19,[B]]])))."]
        rule = parse_rule(rule_input[0], {})

    def test_single_rule_with_skolem_in_if(self):
        rule_input = ["r(66,2,[],kow(if([[identical,[e,9,[A]],A],[instance-of,A,temporal-region,A]]),false)).", "r(136,2,[],kow(if([[identical,[e,30,[B]],[e,31,[B]]],[instance-of,B,object-aggregate,A]]),false)).", "r(145,3,[],kow(if([[continuant-part-of,A,B,C],[identical,[e,35,[B,C]],B],[instance-of,B,material-entity,C]]),then([identical,A,B])))."]
        for input in rule_input:
            rule = parse_rule(input, {})

    def test_single_rule_with_multi_if_clauses(self):
        rule_input = ["r(55,2,[],kow(if([[continuant-part-of,C,A,B],[exists-at,A,B]]),then([exists-at,C,B])))."]
        rule = parse_rule(rule_input[0], {})

    def test_rule_with_multiple_skolems(self):
        rule_input = ["r(54,1,[6,7],kow(if([[universal,A]]),then([instance-of,[e,6,[A]],A,[e,7,[A]]])))."]
        rule = parse_rule(rule_input[0], {})

    # def test_single_fact_with_skolem(self):
    #     skolem_list = {}
    #     skolem_counter = 1
    #     test_input = ["t([instance-of,[e,19,[my-thinking,t]],object,t])."]
    #     fact = read_fact(0, test_input[0], skolems=True, skolem_list=skolem_list, skolem_count=skolem_counter)
    #     self.assertEqual(fact.value, "instance-of")
    #     self.assertEqual(fact.type, "Fact")
    #     self.assertEqual(fact.args, ["sk1", "object", "t"])
    #     self.assertEqual(len(skolem_list.items()), 1)
    #     self.assertEqual(skolem_list["sk1"], ["e", "19", ["my-thinking", "t"]])

    # def test_single_fact_with_multiple_skolems(self):
    #     skolem_list = {}
    #     skolem_counter = 1
    #     test_input = ["t([instance-of,[e,19,[my-thinking,t]],object,[e,20,[an-object,open-season,timeout]]])."]
    #     fact = read_fact(0, test_input[0], skolems=True, skolem_list=skolem_list, skolem_count=skolem_counter)
    #     self.assertEqual(fact.value, "instance-of")
    #     self.assertEqual(fact.type, "Fact")
    #     self.assertEqual(fact.args, ["sk1", "object", "sk2"])
    #     self.assertEqual(len(skolem_list.items()), 2)
    #     self.assertEqual(skolem_list["sk1"], ["e", "19", ["my-thinking", "t"]])
    #     self.assertEqual(skolem_list["sk2"], ["e", "20", ["an-object", "open-season", "timeout"]])


if __name__ == '__main__':
    unittest.main()