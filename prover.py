import argparse
import re
from rule import Rule
from fact import Fact

parser = argparse.ArgumentParser()
parser.add_argument("--start", default="mytest-input.txt")
parser.add_argument("--rulefile", default="BFO2020-kowalski-with-identity-rules.txt")
#used to control print statements
parser.add_argument("--debug", default=False)
args = parser.parse_args()
DEBUG = args.debug
SKOLEM_EXP = "(\[e,[0-9]+,\[([A-Z],)*[A-Z]\]\])"
#custom print function to control debug statements at a high level
def display(message, type, debug):
    if(type == "crit"):
        print(message)
    elif(type == "debug"):
        if(debug):
            print(message)

def parse_then_terms(then_string, skolem_list):
    then_clause = re.search('\[(.)*\]', then_string)
    res = then_clause.group(0)
    res = res[1:-1]
    terms = []
    parsed = list(re.finditer('\[(.)*?\]', res))
    if len(parsed) == 0:
        en = res.split(',')
        terms += en
    else:
        for entry in parsed:
            string = entry.group(0)[1:-1]
            en = string.split(',')
            terms.append(en)
    return terms

def parse_if_terms(if_string, arity, has_skolem, skolem_list):
    display("If terms", "debug", DEBUG)
    display(if_string, "debug", DEBUG)
    #trim off the outer-most brackets
    inner = re.search('\[(.)+\]', if_string)
    result = inner.group(0)
    result = result[1:-1]
    terms = []
    parsed_terms = re.split('\],', result)
    parsed_terms[-1] = parsed_terms[-1][:-1]
    display(parsed_terms, "debug", DEBUG)
    for entry in parsed_terms:
        entry = entry[1:]
        skolem_strings = {}
        if has_skolem:
            element = re.finditer(SKOLEM_EXP, entry)
            for i, el in enumerate(element):
                display("Run skolem", "debug", DEBUG)
                skolem_string = el.group(0)
                display(skolem_string, "debug", DEBUG)
                entry = entry.replace(skolem_string, f"sk{i}")
                display(entry, "debug", DEBUG)
                skolem_string = skolem_string[1:-1]
                display(skolem_string, "debug", DEBUG)
                args = re.findall("[A-Z]", skolem_string)
                skolem_number = re.search("[0-9]+", skolem_string)
                display(args, "debug", DEBUG)
                number = skolem_number.group(0)
                display(number, "debug", DEBUG)
                skolem = ["e", number, args]
                display(skolem, "debug", DEBUG)
                skolem_strings[f"sk{i}"] = skolem
        en = re.split(',', entry)
        for i in range(len(en)):
            element = en[i]
            if element in skolem_strings:
                en[i] = skolem_strings[element]
        display(en, "debug", DEBUG)
        terms.append(en)
    # display("Terms", "crit", DEBUG)
    # display(terms, "crit", DEBUG)
    return terms
#TO-DO: parse_rule needs to be massively overhauled considering that I know significantly more about how regexps work
#Try to piece together what exactly the regular expression of each rule is
#it's r(rule number, arity number, [skolem functions present in rule], kow(if([[args]]), then([args])))
def parse_rule(line, skolem_list):
    has_skolem = False
    #first search for numerical values to get the index and arity of each rule
    se = list(re.finditer('[0-9]+', line))
    index, arity = int(se[0].group(0)), int(se[1].group(0))
    display(f"Rule {index} has arity {arity}", "crit", DEBUG)

    #next we need to determine whether or not there are any skolems in the function
    bracket_search = re.search('\[([0-9]+)+(,[0-9]+)*\]', line)
    display(bracket_search, "debug", DEBUG)
    if(bracket_search != None):
        has_skolem = True
    #get the if terms
    if_clause = re.search('if\((\[(.)*?\])\)', line)
    if(if_clause == None):
        if_terms = ["True"]
    else:
        display(if_clause.group(0), "debug", DEBUG)
        if_terms = parse_if_terms(if_clause.group(0), arity, has_skolem, skolem_list)
    display(if_terms, "crit", DEBUG)
    then_clause = re.search('(then|then_or)\(\[(.)*?\]\)', line)
    if then_clause == None:
        then_terms = ["False"]
    else:
        display(then_clause.group(0), "debug", DEBUG)
        then_terms = parse_then_terms(then_clause.group(0), skolem_list)
    display(then_terms, "crit", DEBUG)
    new_rule = Rule(index, if_terms, then_terms, has_skolem, bracket_search)
    return new_rule

"""The read_rules file opens rule_file and loads each different rule into a rule dictionary."""
def read_rules(rule_file, skolem):
    rule_list = {}
    with open(rule_file, "r") as rules:
        for i, line in enumerate(rules):
            if(line[0] == "r"):
                rule = parse_rule(line, skolem)
                rule_list[i] = rule
    return rule_list

def read_fact(line, skolem_table, skolem_counter):
    #look for stuff within two square brackets
    format = re.search('\[(.)+\]', line)
    content = format.group(0)
    content = content[1:-1]
    #assuming that user doesn't pass in skolem functions for now
    terms = content.split(",")
    fact = Fact(terms[0], terms[1:], True)
    fact.rules_from.append(0)
    return fact

"""the init() function performs all of the required setup needed to parse all of the 
information provided in both the input_file and the rule_file in order to perform 
inference"""
def init(input_file, rule_file, skolem_table, skolem_counter):
    sk_consts = {}
    rules = read_rules(rule_file, sk_consts)
    facts = {}
    with open(input_file, "r") as file:
        for i, line in enumerate(file):
            if(line[0] == "%"):
                continue
            fact = read_fact(line, skolem_table, skolem_counter)
            print(fact)
            facts[i] = fact
    print(facts)
    fact_counter = len(facts.items()) + 1
    return rules, facts, fact_counter, sk_consts

#given a list of candidate clauses and their consistency, determine whether or not there is a match in any of the clauses
def get_candidate_facts(clauses, current_facts, skolem_table):
    candidate_facts = []
    for clause in clauses:
        valid = []
        for fact in current_facts:
            print(fact)

#this is the function that arguably needs the biggest overhaul
#thankfully, immutable dicts are our friends in this instance
def unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=0):
    fact_count = len(facts.items())
    new_skolem = []
    multiple_candidates = False
    candidate_facts = get_candidate_facts(rule.if_terms, [current_fact], skolem_table)
    pass

#cutoff is the last rule we should read from the current iteration of this code
#I use a memoization approach to ensure that we're not trying to match strings that we've already gone
#through previously
#there are several optimization tricks we can use to speed up the search for matches
#the first is that we sort the rules by arity
def modus_ponens(rules, facts, fact_counter, skolem_list, cutoff, arity_index):
    print("Running modus ponens")
    #memoization
    fact_memo = set()
    current_fact = fact_counter - 1
    while(current_fact > cutoff):
        display(f"Current fact: {current_fact}", "debug", DEBUG)
        #current_fact being in the set means that we've already discovered all there is to 
        #know about the existing fact
        if current_fact not in fact_memo:
            #run inference on the current fact
            for _, rule in rules:
                if(rule.is_then_or or rule.then_terms == ['False']):
                    continue
                if(len(rule.if_terms) <= arity_index):
                    unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=arity_index)

            # add the current_fact to the set
            fact_memo.add(current_fact)
            current_fact -= 1

def run_inference(rules, facts, fact_counter, skolem_list, skolems_per_fact):
    #forward chaining of positive rules using modus_ponens
    print("Running inference")
    modus_ponens(rules, facts, fact_counter, skolem_list, 0, 1)

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
    rules, start_facts, fact_counter, skolem_list = init(input_file, rule_file, skolem_table, skolem_counter)
    print(fact_counter)
    rules = sorted(rules.items(), key=lambda x: x[1].arity)
    run_inference(rules, start_facts, fact_counter, skolem_list, skolems_per_fact)