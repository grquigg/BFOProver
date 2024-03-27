import argparse
from rule import RuleNode
from node import FactNode
import utils
from utils import display
import re
parser = argparse.ArgumentParser()
parser.add_argument("--start", default="mytest-input.txt")
parser.add_argument("--rulefile", default="BFO2020-kowalski-with-identity-rules.txt")
#used to control print statements
parser.add_argument("--debug", default=False)
args = parser.parse_args()
utils.DEBUG = args.debug
#custom print function to control debug statements at a high level

def modusPonens(valid_facts: list[(FactNode, dict, int)], facts: list[FactNode], rules: list[RuleNode]):
    fact_counter = len(facts)
    for fact, sub, rule_index in valid_facts:
        args = rules[rule_index].then_terms[0][1:]
        fact = FactNode(fact_counter, rules[rule_index].then_terms[0][0], [])
        for i in range(len(args)):
            if args[i] in sub:
                args[i] = sub[args[i]]
        fact.args = args
        #unfortunately we have to go through all of this logic regardless of whether the fact was already generated or not, which can be cumbersome
        if fact not in facts:
            facts.append(fact)
        fact_counter += 1
    return facts

def linkStep(facts: list[FactNode], rules: list[RuleNode], rules_dict: dict[tuple[int,int]], valid_facts: list[(FactNode, dict, int)]):
    for i, fact in enumerate(facts):
        for rule in rules_dict[fact.value]:
            #create an empty dict
            print(rules[rule[0]])
            print(fact)
            assert(type(rules[rule[0]]) == RuleNode)
            assert(len(rules[rule[0]].args[rule[1]]) == len(fact.args))
            values = {}
            valid_fact = True
            for i in range(len(fact.args)):
                is_var = re.search('[A-Z]', rules[rule[0]].args[rule[1]][i])
                if not is_var: #assure all non vars is equal
                    if(rules[rule[0]].args[rule[1]][i] != fact.args[i]):
                        valid_fact = False
                        break
                else:
                    if rules[rule[0]].args[rule[1]][i] in values:
                        if values[rules[rule[0]].args[rule[1]][i]] != fact.args[i]:
                            valid_fact = False
                            break
                    else:
                        values[rules[rule[0]].args[rule[1]][i]] = fact.args[i]
            if valid_fact:
                fact_args = tuple(fact.args)
                if(fact_args not in fact.neighbors):
                     fact.neighbors[fact_args] = []
                if(rules[rule[0]] not in fact.neighbors[fact_args]):
                    fact.neighbors[fact_args].append(rules[rule[0]])
                valid_facts.append((fact, values, rules[rule[0]].index))
        fact.linked = True
    return valid_facts
        

#given a list of candidate clauses and their consistency, determine whether or not there is a match in any of the clauses
#ideally the algorithm jumps straight into determining whether the substitution is actually valid from this line
def get_candidate_facts(rule, current_facts, facts, skolem_table, return_valid=False):
    clauses = rule.if_terms
    candidate_facts = []
    mappings = []
    for i, clause in enumerate(clauses):
        valid = []
        for fact in current_facts:
            match, mapping = rule.match([facts[fact].name] + facts[fact].args, i)
            if match:
                valid.append((fact, mapping))
        candidate_facts.append(valid)
    return candidate_facts

#this is the function that arguably needs the biggest overhaul
#thankfully, immutable dicts are our friends in this instance
def unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=0):
    display(f"Rule: {rule.index}", "crit", utils.DEBUG)
    fact_count = len(facts.items())
    new_skolem = []
    multiple_candidates = False
    candidate_facts = get_candidate_facts(rule, [current_fact], facts, skolem_table, return_valid=True)
    empty = [len(candidate) for candidate in candidate_facts]
    max_cans = max(empty)
    if max_cans > 0:
        display(f"Rule: {rule}", "crit", utils.DEBUG)
        display(candidate_facts, "crit", utils.DEBUG)
        raise NotImplementedError()
    pass

#cutoff is the last rule we should read from the current iteration of this code
#I use a memoization approach to ensure that we're not trying to match strings that we've already gone
#through previously
#there are several optimization tricks we can use to speed up the search for matches
#the first is that we sort the rules by arity

def run_inference(rules, facts, fact_counter, skolem_list, skolems_per_fact):
    #forward chaining of positive rules using modus_ponens
    print("Running inference")
    # modus_ponens(rules, facts, fact_counter, skolem_list, 0, 1)

if __name__ == "__main__":
    args = parser.parse_args()
    print("Hello")
    if not args.start:
        raise ValueError("No file with starting facts provided")
    print(args.start)
    if not args.rulefile:
        raise ValueError("No rulefile provided")
    print(args.rulefile)

    #we start out by having skolem_table be an empty list
    skolem_table = {}
    skolems_per_fact = {}
    #and skolem counter being set to 1
    skolem_counter = 1
    input_file = args.start
    rule_file = args.rulefile
    # rules, start_facts, fact_counter, skolem_list = init(input_file, rule_file, skolem_table, skolem_counter)
    # print(fact_counter)
    # rules = sorted(rules.items(), key=lambda x: x[1].arity)
    # run_inference(rules, start_facts, fact_counter, skolem_list, skolems_per_fact)