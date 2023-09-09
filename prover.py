import argparse
import re
parser = argparse.ArgumentParser()
parser.add_argument("--start", default="mytest-input.txt")
parser.add_argument("--rulefile", default="BFO2020-kowalski-with-identity-rules.txt")
#used to control print statements
parser.add_argument("--debug", default=False)
args = parser.parse_args()
DEBUG = args.debug
#custom print function to control debug statements at a high level
def display(message, type, debug):
    if(type == "crit"):
        print(message)
    elif(type == "debug"):
        if(debug):
            print(message)

def parse_if_terms(if_string, arity, has_skolem, skolem_list):
    if(has_skolem):
        raise NotImplementedError("Skolem functions")
    inner = re.search('\[(.)*\]', if_string)
    result = inner.group(0)
    result = result[1:-1]
    terms = []
    parsed_terms = re.finditer('\[(.)*?\]', result)
    for entry in parsed_terms:
        string = entry.group(0)[1:-1]
        en = string.split(',')
        terms.append(en)
    display(terms, "debug", DEBUG)
    return terms
#TO-DO: parse_rule needs to be massively overhauled considering that I know significantly more about how regexps work
#Try to piece together what exactly the regular expression of each rule is
#it's r(rule number, arity number, [skolem functions present in rule], kow(if([[args]]), then([args])))
def parse_rule(line, skolem_list):
    has_skolem = False
    #first search for numerical values to get the index and arity of each rule
    se = list(re.finditer('[0-9]+', line))
    index, arity = int(se[0].group(0)), int(se[1].group(0))
    display(f"Rule {index} has arity {arity}", "debug", DEBUG)

    #next we need to determine whether or not there are any skolems in the function
    bracket_search = re.search('\[([0-9]+)+(,[0-9]+)*\]\),', line)
    display(bracket_search, "debug", DEBUG)
    if(bracket_search != None):
        has_skolem = True
    #get the if terms
    if_clause = re.search('if\((\[(.)*?\])\)', line)
    display(if_clause.group(0), "debug", DEBUG)
    if_terms = parse_if_terms(if_clause.group(0), arity, has_skolem, skolem_list)

"""The read_rules file opens rule_file and loads each different rule into a rule dictionary."""
def read_rules(rule_file, skolem):
    rule_list = {}
    rule_count = 1
    with open(rule_file, "r") as rules:
        for line in rules:
            if(line[0] == "r"):
                rule = parse_rule(line, skolem)
                rule_list[rule_count] = rule
                rule_count += 1
                raise NotImplementedError("Stop")
    return rule_list

"""the init() function performs all of the required setup needed to parse all of the 
information provided in both the input_file and the rule_file in order to perform 
inference"""
def init(input_file, rule_file, skolem_table, skolem_counter):
    sk_consts = {}
    rules = read_rules(rule_file, sk_consts)
    facts = {}
    fact_counter = 1
    with open(input_file, "r") as file:
        for line in file:
            if(line[0] == "%"):
                continue
            fact = parse_line(line, skolem_table, skolem_counter)
            skolem_counter = len(skolem_table.items()) + 1
            facts[fact_counter] = fact
            fact_counter+=1
    return rules, facts, fact_counter, sk_consts

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

    #and skolem counter being set to 1
    skolem_counter = 1
    input_file = args.start
    rule_file = args.rulefile
    rules, start_facts, fact_counter, skolem_list = init(input_file, rule_file, skolem_table, skolem_counter)