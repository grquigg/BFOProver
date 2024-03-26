import unittest
import sys
sys.path.append('../')
from parse_input import read_fact, parse_rule, read_rules
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
        rule_dict = {"instance-of": [(0,0)]}
        valid_facts = []
        valid_facts = linkStep([fact], [rule], rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): [rule]})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "process", "C": "t"}, 61)])

    def test_simple_link_with_skolem(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(172,1,[45],kow(if([[instance-of,B,process,A]]),then([occurrent-part-of,[e,45,[B]],B])))."]
        fact = read_fact(0, fact_input[0], False)
        rule = parse_rule(rule_input[0])
        self.assertEqual(fact.value, rule.values[0])
        rule_dict = {"instance-of": [(0,0)]}
        valid_facts = []
        valid_facts = linkStep([fact], [rule], rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "process", "t"): [rule]})
        self.assertEqual(valid_facts, [(fact, {"A": "t", "B": "my-thinking"}, 172)])
    """
    tests whether or not a link is created when a fact interacts with a rule where non variables elements in the
    fact and the predicate are not equal
    """
    def test_link_should_not_work(self):
        fact_input = ["t([instance-of,my-thinking,process,t])."]
        rule_input = ["r(172,1,[45],kow(if([[instance-of,B,occurrent,A]]),then([occurrent-part-of,[e,45,[B]],B])))."]
        fact = read_fact(0, fact_input[0], False)
        rule = parse_rule(rule_input[0])
        self.assertEqual(fact.value, rule.values[0])
        rule_dict = {"instance-of": [(0,0)]}
        valid_facts = []
        valid_facts = linkStep([fact], [rule], rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {})
        self.assertEqual(valid_facts, [])
    """
    sk10 is the first instance of a fact with a nested skolem
    used by rule 355 using fact 16
    """
    def test_link_with_skolem(self):
        skolem_table = {}
        skolem_counter = 1
        fact_input = ["t([occupies-temporal-region,my-thinking,[e,100,[my-thinking]]])."]
        rule_input = ["r(355,1,[109],kow(if([[occupies-temporal-region,A,B]]),then_or([[instance-of,A,process,[e,109,[A,B]]],[instance-of,A,process-boundary,[e,109,[A,B]]]])))."]
        fact = read_fact(0, fact_input[0], skolems=True, skolem_list=skolem_table, skolem_count=skolem_counter)
        rule = parse_rule(rule_input[0])
        self.assertEqual(fact.args, ["my-thinking", "sk1"])
        rule_dict = {"occupies-temporal-region": [(0,0)]}
        valid_facts = []
        valid_facts = linkStep([fact], [rule], rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("my-thinking", "sk1"): [rule]})
        self.assertEqual(valid_facts, [(fact, {"A": "my-thinking", "B": "sk1"}, 355)])

        pass
    """
    rule 108 is the first instance of function where two facts are used to derive a fact
    291 and 297. We don't care about the skolem as much as we care about making sure that the facts are linking together
    """
    def test_complex_link(self):
        fact_input = ["t([history-of,sk33,me]).", "t([instance-of,sk33,history,sk34])."]
        rule_input = ["r(108,2,[],kow(if([[history-of,C,B],[instance-of,C,history,A]]),then([instance-of,B,material-entity,A])))."]
        facts = [read_fact(0, fact_input[0]), read_fact(1, fact_input[1])]
        rule = parse_rule(rule_input[0])
        rule_dict = {"history-of": [(0, 0)], "instance-of": [(0,1)]}
        valid_facts = []
        valid_facts = linkStep(facts, [rule], rule_dict, valid_facts)
        self.assertEqual(facts[0].neighbors, {("sk33", "me"): [rule]})
        self.assertEqual(facts[1].neighbors, {("sk33", "history", "sk34"): [rule]})
        self.assertEqual(valid_facts, [(facts[0], {"C": "sk33", "B": "me"}, 108), (facts[1], {"C": "sk33", "A": "sk34"}, 108)])
    
    """
    a test to ensure that existing links aren't destroyed when added new ones to Fact().neighbors
    """
    def test_multiple_links_per_fact(self):
        fact_input = ["t([history-of,sk33,me])."]
        rule_input = ["r(108,2,[],kow(if([[history-of,C,B]]),then([instance-of,B,material-entity,A]))).",
                      "r(110,2,[],kow(if([[history-of,C,B]]),then([instance-of,B,object,A])))."]
        fact = read_fact(0, fact_input[0])
        rules = [parse_rule(rule_input[0]), parse_rule(rule_input[1])]
        rule_dict = {"history-of": [(0, 0),(1,0)]}
        valid_facts = []
        valid_facts = linkStep([fact], rules, rule_dict, valid_facts)
        self.assertEqual(fact.neighbors, {("sk33", "me"): rules})
        self.assertEqual(valid_facts, [(fact, {"C": "sk33", "B": "me"}, 108), (fact, {"C": "sk33", "B": "me"}, 110)])
    
    
    """
    a test to make sure that existing links aren't duplicated
    """
    def test_existing_link(self):
        fact_input = ["t([history-of,sk33,me]).", "t([instance-of,sk33,history,sk34])."]
        rule_input = ["r(108,2,[],kow(if([[history-of,C,B],[instance-of,C,history,A]]),then([instance-of,B,material-entity,A]))).",
                      "r(109,2,[],kow(if([[history-of,C,B],[instance-of,C,history,A]]),then([instance-of,B,material-entity,A])))."]
        facts = [read_fact(i, fact_input[i]) for i in range(len(fact_input))]
        rules = read_rules(rule_input)
        rule_dict = {"history-of": [(0, 0)], "instance-of": [(0,1)]}
        valid_facts = []
        valid_facts = linkStep(facts, rules, rule_dict, valid_facts)
        self.assertEqual(facts[0].neighbors, {("sk33", "me"): rules})
        self.assertEqual(valid_facts, [(facts[0], {"C": "sk33", "B": "me"}, 108), (facts[1], {"C": "sk33", "A": "sk34"}, 108)])

    # """
    # a test to make sure that false facts are linked to corresponding args in then_or clauses
    # """
    # def test_tollens_link(self):
    #     pass

    def test_rules_cannot_link_together(self):
        pass

    def test_facts_cannot_link_together(self):
        pass


if __name__ == '__main__':
    unittest.main()