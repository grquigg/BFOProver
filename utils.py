DEBUG = False
SKOLEM_EXP = "(\[e,[0-9]+,\[([A-Z],)*[A-Z]\]\])"

def display(message, type, debug):
    if(type == "crit"):
        print(message)
    elif(type == "debug"):
        if(debug):
            print(message)

"""the init() function performs all of the required setup needed to parse all of the 
information provided in both the input_file and the rule_file in order to perform 
inference"""
def init(input_file, rule_file, skolem_table, skolem_counter):
    from parse_input import read_rules, read_fact
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