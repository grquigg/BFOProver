import unittest
import sys
sys.path.append('../')
from parse_input import read_fact, parse_rule, read_rules

class InputMethods(unittest.TestCase):
    
    def test_single_rule(self):
        rule_input = ["r(1,1,[],kow(if([[identical,A,B]]),then([identical,B,A])))."]
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 1)
        self.assertEqual(rule.arity, 1)
        self.assertEqual(rule.if_terms, [["identical", "A", "B"]])
        self.assertEqual(rule.then_terms, [["identical", "B", "A"]])
        self.assertFalse(rule.is_then_or)
        self.assertFalse(rule.has_skolem)
        self.assertEqual(rule.skolems, None)
        self.assertEqual(rule.values, ["identical"])
        self.assertEqual(rule.type, "Rule")
        self.assertEqual(rule.args, [["A", "B"]])
        pass
    def test_single_rule_with_skolem(self):
        rule_input = ["r(108,1,[19],kow(if([[instance-of,B,history,A]]),then([history-of,B,[e,19,[B]]])))."]
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 108)
        self.assertEqual(rule.arity, 1)
        self.assertEqual(rule.if_terms, [["instance-of", "B", "history", "A"]])
        self.assertEqual(rule.then_terms, [['history-of', 'B', ['e', 19, ['B']]]])
        self.assertFalse(rule.is_then_or)
        self.assertTrue(rule.has_skolem)
        self.assertEqual(rule.skolems, [19])
        self.assertEqual(rule.type, "Rule")
        self.assertEqual(rule.values, ["instance-of"])
        self.assertEqual(rule.args, [["B", "history", "A"]])

    def test_single_rule_with_skolem_in_if(self):
        rule_input = ["r(66,2,[],kow(if([[identical,[e,9,[A]],A],[instance-of,A,temporal-region,A]]),false)).", 
                      "r(136,2,[],kow(if([[identical,[e,30,[B]],[e,31,[B]]],[instance-of,B,object-aggregate,A]]),false)).", "r(145,3,[],kow(if([[continuant-part-of,A,B,C],[identical,[e,35,[B,C]],B],[instance-of,B,material-entity,C]]),then([identical,A,B])))."]
        
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 66)
        self.assertEqual(rule.arity, 2)
        self.assertEqual(rule.if_terms, [["identical", ["e", 9, ["A"]], "A"], ["instance-of","A","temporal-region","A"]])
        self.assertEqual(rule.type, "Rule")
        self.assertEqual(rule.values, ["identical", "instance-of"])
        self.assertEqual(rule.args, [[["e", 9, ["A"]], "A"],["A","temporal-region","A"]])
        self.assertEqual(rule.then_terms, ["false"])
        self.assertFalse(rule.has_skolem)
        self.assertFalse(rule.is_then_or)

        rule = parse_rule(rule_input[1])
        self.assertEqual(rule.index, 136)
        self.assertEqual(rule.arity, 2)
        self.assertEqual(rule.if_terms, [['identical', ['e', 30, ['B']], ['e', 31, ['B']]], ['instance-of', 'B', 'object-aggregate', 'A']])
        self.assertEqual(rule.values, ["identical", "instance-of"])
        self.assertEqual(rule.args, [[['e', 30, ['B']], ['e', 31, ['B']]], ['B', 'object-aggregate', 'A']])
        self.assertEqual(rule.then_terms, ["false"])
        self.assertFalse(rule.has_skolem)
        self.assertFalse(rule.is_then_or)
    
    def test_single_rule_with_multi_if_clauses(self):
        rule_input = ["r(55,2,[],kow(if([[continuant-part-of,C,A,B],[exists-at,A,B]]),then([exists-at,C,B])))."]
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 55)
        self.assertEqual(rule.arity, 2)
        self.assertEqual(rule.if_terms, [["continuant-part-of","C","A","B"], ["exists-at", "A","B"]])
        self.assertEqual(rule.args, [["C","A","B"], ["A","B"]])
        self.assertEqual(rule.values, ["continuant-part-of", "exists-at"])
        self.assertEqual(rule.then_terms, [['exists-at', 'C', 'B']])
        self.assertFalse(rule.has_skolem)
        self.assertFalse(rule.is_then_or)

    def test_rule_with_multiple_skolems(self):
        rule_input = ["r(54,1,[6,7],kow(if([[universal,A]]),then([instance-of,[e,6,[A]],A,[e,7,[A]]])))."]
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 54)
        self.assertEqual(rule.arity, 1)
        self.assertEqual(rule.if_terms, [["universal", "A"]])
        self.assertEqual(rule.args, [["A"]])
        self.assertEqual(rule.values, ["universal"])
        self.assertEqual(rule.then_terms, [['instance-of', ['e', 6, ['A']], 'A', ['e', 7, ['A']]]])
        self.assertFalse(rule.is_then_or)
        self.assertTrue(rule.has_skolem)
        self.assertEqual(rule.skolems, [6,7])

    def test_then_or_rule(self):
        rule_input =["r(15,1,[],kow(if([[continuant-part-of,A,B,C]]),then_or([[continuant-part-of,B,A,C],[proper-continuant-part-of,A,B,C]])))."]
        rule = parse_rule(rule_input[0])
        self.assertEqual(rule.index, 15)
        self.assertEqual(rule.arity, 1)
        self.assertEqual(rule.if_terms, [['continuant-part-of', 'A', 'B', 'C']])
        self.assertEqual(rule.args, [["A", "B", "C"]])
        self.assertEqual(rule.values, ["continuant-part-of"])
        self.assertEqual(rule.then_terms, [['continuant-part-of', 'B', 'A', 'C'], ['proper-continuant-part-of', 'A', 'B', 'C']])
        self.assertTrue(rule.is_then_or)
        self.assertFalse(rule.has_skolem)
        self.assertEqual(rule.skolems, None)

    def test_single_fact(self):
        test_input = ["t([instance-of,me,object,t])."]
        fact = read_fact(0, test_input[0], skolems=False)
        self.assertEqual(fact.value, "instance-of")
        self.assertEqual(fact.type, "Fact")
        self.assertEqual(fact.args, ["me", "object", "t"])
        
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

    def test_other_fact_with_skolem(self):
        skolem_list = {}
        skolem_counter = 1
        fact_input = ["t([occupies-spatiotemporal-region,my-thinking,[e,100,[my-thinking]]])."]
        fact = read_fact(0, fact_input[0], skolems=True, skolem_list=skolem_list, skolem_count=skolem_counter)
        self.assertEqual(fact.args, ["my-thinking", "sk1"])

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

    def test_dont_duplicate_identical_rules(self):
        rule_input = ["r(54,1,[6,7],kow(if([[universal,A]]),then([instance-of,[e,6,[A]],A,[e,7,[A]]]))).",
                      "r(54,1,[6,7],kow(if([[universal,A]]),then([instance-of,[e,6,[A]],A,[e,7,[A]]]))).",
                      "r(100,1,[6,7],kow(if([[universal,A]]),then([instance-of,[e,6,[A]],A,[e,7,[A]]])))."]
        rules, rule_dict = read_rules(rule_input)
        self.assertEqual(len(rules.items()), 1)


if __name__ == '__main__':
    unittest.main()