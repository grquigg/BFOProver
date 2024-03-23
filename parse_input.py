import re
import utils
from utils import display
from node import FactNode
from rule import RuleNode

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
    display("If terms", "debug", utils.DEBUG)
    display(if_string, "debug", utils.DEBUG)
    #trim off the outer-most brackets
    inner = re.search('\[(.)+\]', if_string)
    result = inner.group(0)
    result = result[1:-1]
    terms = []
    parsed_terms = re.split('\],', result)
    parsed_terms[-1] = parsed_terms[-1][:-1]
    display(parsed_terms, "debug", utils.DEBUG)
    for entry in parsed_terms:
        entry = entry[1:]
        skolem_strings = {}
        if has_skolem:
            element = re.finditer(utils.SKOLEM_EXP, entry)
            for i, el in enumerate(element):
                display("Run skolem", "debug", utils.DEBUG)
                skolem_string = el.group(0)
                display(skolem_string, "debug", utils.DEBUG)
                entry = entry.replace(skolem_string, f"sk{i}")
                display(entry, "debug", utils.DEBUG)
                skolem_string = skolem_string[1:-1]
                display(skolem_string, "debug", utils.DEBUG)
                args = re.findall("[A-Z]", skolem_string)
                skolem_number = re.search("[0-9]+", skolem_string)
                display(args, "debug", utils.DEBUG)
                number = skolem_number.group(0)
                display(number, "debug", utils.DEBUG)
                skolem = ["e", number, args]
                display(skolem, "debug", utils.DEBUG)
                skolem_strings[f"sk{i}"] = skolem
        en = re.split(',', entry)
        for i in range(len(en)):
            element = en[i]
            if element in skolem_strings:
                en[i] = skolem_strings[element]
        display(en, "debug", utils.DEBUG)
        terms.append(en)
    # display("Terms", "crit", DEBUG)
    # display(terms, "crit", DEBUG)
    return terms
# #TO-DO: parse_rule needs to be massively overhauled considering that I know significantly more about how regexps work
# #Try to piece together what exactly the regular expression of each rule is
# #it's r(rule number, arity number, [skolem functions present in rule], kow(if([[args]]), then([args])))
def parse_rule(line: str, skolem_list: dict):
    has_skolem = False
    #first search for numerical values to get the index and arity of each rule
    se = list(re.finditer('[0-9]+', line))
    index, arity = int(se[0].group(0)), int(se[1].group(0))
    # display(f"Rule {index} has arity {arity}", "crit", utils.DEBUG)

    #next we need to determine whether or not there are any skolems in the function
    bracket_search = re.search('\[([0-9]+)+(,[0-9]+)*\]', line)
    # display(bracket_search, "debug", utils.DEBUG)
    if(bracket_search != None):
        has_skolem = True
    #get the if terms
    if_clause = re.search('if\((\[(.)*?\])\)', line)
    if(if_clause == None):
        if_terms = ["True"]
    else:
        # display(if_clause.group(0), "debug", utils.DEBUG)
        if_terms = parse_if_terms(if_clause.group(0), arity, has_skolem, skolem_list)
    # display(if_terms, "crit", utils.DEBUG)
    then_clause = re.search('(then|then_or)\(\[(.)*?\]\)', line)
    if then_clause == None:
        then_terms = ["False"]
    else:
        # display(then_clause.group(0), "debug", utils.DEBUG)
        then_terms = parse_then_terms(then_clause.group(0), skolem_list)
    # display(then_terms, "crit", utils.DEBUG)
    new_rule = RuleNode(index, if_terms, then_terms, has_skolem, bracket_search)
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
    print("\n" + content)
    content = content[1:-1]
    print(f"Content after {content}")
    #we're obviously going to have to deal with nested skolems as well
    if(skolems):
        if(not skolem_count or skolem_count == 0):
            raise ValueError("Cannot set skolems to True and not provide any arguments!")
        format = re.findall('(\[e,[0-9]+,\[(((\w)+-)*(\w)+,)+((\w)+-)*(\w)+\]\])', content)
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