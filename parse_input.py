import re
import utils
from utils import display, is_skolem
from node import FactNode
from rule import RuleNode

def read_rules(rules: list[str]) -> tuple[dict[int], dict[str,tuple[int,int]]]:
    parsed_rules = {}
    rule_dict = {}
    for rule in rules:
        parsed = parse_rule(rule)
        if parsed not in parsed_rules.values():
            parsed_rules[parsed.index] = parsed
            for i in range(len(parsed.values)):
                if parsed.values[i] not in rule_dict:
                    rule_dict[parsed.values[i]] = []
                rule_dict[parsed.values[i]].append((parsed.index, i))
    return parsed_rules, rule_dict

def parse_terms(if_string: str) -> list:
    clauses = []
    results = list(re.finditer('\[((((?:\w-?)+)|(\[e,[0-9]+,\[(?:\w,?)+\]\])),?)+\]', if_string))
    for result in results:
        terms = list(re.finditer('(\w-?)+|(\[e,[0-9]+,\[(?:\w,?)+\]\])', result.group(0)))
        processed = []
        for term in terms:
            if not(is_skolem(term.group(0))):
                processed.append(term.group(0))
            else:
                t = term.group(0)[1:-1]
                vars = list(re.finditer('(e),([0-9]+),(\[(?:[A-Z],?)+\])', t))
                skolem_vals = [vars[0].group(1), int(vars[0].group(2))]
                skolem_vars = vars[0].group(3)[1:-1].split(',')
                skolem_vals.append(skolem_vars)
                processed.append(skolem_vals)
        clauses.append(processed)
    return clauses
# #TO-DO: parse_rule needs to be massively overhauled considering that I know significantly more about how regexps work
# #Try to piece together what exactly the regular expression of each rule is
# #it's r(rule number, arity number, [skolem functions present in rule], kow(if([[args]]), then([args])))
def parse_rule(line: str):
    expression_parse = re.search('r\(([0-9]+),([0-9]+),(\[([0-9]*,?)*\])', line)
    if_clause = re.search('if\(\[(\[(.)*\])\]\),', line)
    rule_index = int(expression_parse.group(1))
    arity = int(expression_parse.group(2))
    skolems = expression_parse.group(3)
    #deal with if terms
    if_terms = parse_terms(if_clause.group(1))

    #deal with then terms
    then_clause = re.search('then\((\[(.)*\])\)|false|then_or\((\[(.)*\])\)', line)
    then_terms = []
    if(then_clause.group(0)=="false"):
        then_terms = ["false"]
    else:
        then_terms = parse_terms(then_clause.group(0))
    #deal with skolems
    has_skolems = False
    skolem_list = None
    if skolems != "[]":
        skolem_list = skolems[1:-1].split(',')
        for i in range(len(skolem_list)):
            skolem_list[i] = int(skolem_list[i])
        has_skolems = True
    new_rule = RuleNode(rule_index, if_terms, then_terms, has_skolems, skolem_list)
    return new_rule

"""The read_rules file opens rule_file and loads each different rule into a rule dictionary."""
# def read_rules(rule_file, skolem):
#     rule_list = {}
#     with open(rule_file, "r") as rules:
#         for i, line in enumerate(rules):
#             if(line[0] == "r"):
#                 rule = parse_rule(line, skolem)
#                 rule_list[i] = rule
#     return rule_list

def read_fact(index, line, skolems=False, skolem_list=None, skolem_count=0):
    #look for stuff within two square brackets
    format = re.search('\[(.)+\]', line)
    content = format.group(0)
    content = content[1:-1]
    # print(f"Content after {content}")
    #we're obviously going to have to deal with nested skolems as well
    if(skolems):
        if(not skolem_count or skolem_count == 0):
            raise ValueError("Cannot set skolems to True and not provide any arguments!")
        # format = re.findall('(\[e,[0-9]+,\[(((\w)+-?)+,)+((\w)+-)*(\w)+\]\])', content)
        format = re.findall('(\[e,[0-9]+,\[(((\w)+-?)+,?)+\]\])', content)
        for i in range(len(format)):
            skolem = format[i][0]
            args = []
            funct_dec = skolem[1:-1].split(',')
            args += funct_dec[0:2]
            vars = re.search('(\[(.)+\])', skolem[1:-1]).group(0)[1:-1]
            args += [vars.split(',')]
            if args not in skolem_list.values():
                key = f"sk{skolem_count}"
                skolem_list[key] = args
                content = content.replace(skolem, key)
                skolem_count += 1
    #look for skolems - we need to make our search string as specific as possible
    #assuming that user doesn't pass in skolem functions for now

    terms = content.split(",")
    fact = FactNode(index, terms[0], terms[1:])
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
