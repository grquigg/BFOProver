import re
import copy
import csv
MAX_SKOLEM_DEPTH = 2
MAX_ARITY = 5
MAX_ARGS = 3
MAX_FACTS = 3
rules = []
class Rule(): # a rule has a list of terms
    def __init__(self, index, if_terms, then_terms, has_skolem, skolems):
        self.if_terms = if_terms
        self.then_terms = then_terms
        self.index = int(index)
        self.arity = len(self.if_terms)
        self.is_then_or()
        self.antecedents = 0
        self.has_skolem = has_skolem
        self.skolems = skolems
        if(self.is_then_or):
            self.antecedents = len(self.then_terms)
        else:
            self.antecedents = 1

    def is_then_or(self):
        #if each term in the list of then_terms of a rule is itself a list, then it's a then-or
        lists = [i for i in range(len(self.then_terms)) if isinstance(self.then_terms[i], list)]
        if(len(lists) == len(self.then_terms)):
            self.is_then_or = True
        else:
            self.is_then_or = False

    def __str__(self):
        return "if({}), then({})".format(self.if_terms, self.then_terms)

class Fact():
    def __init__(self, name, args, truth_value, derivation=None):
        self.name = name
        self.args = args
        self.truth_value = truth_value
        self.derivation = derivation #used to note the rules that were used to derive this fact
        self.rules_used = []
        self.rules_from = []
    
    def equate_args(self, args1, args2):
        if(len(args1) != len(args2)):
            return False
        for i in range(len(args1)):
            if("sk" in args1[i] and "sk" in args2[i]):
                # print(skolem_table)
                if(skolem_table[args1[i]][2] == skolem_table[args2[i]][2]):
                    continue
                else:
                    if("sk" in skolem_table[args1[i]][2][0] and "sk" in skolem_table[args2[i]][2][0]):
                        result = self.equate_args(skolem_table[args1[i]][2], skolem_table[args2[i]][2])
                        if(result):
                            if(args1[i] in skolems_per_fact):
                                return False
                            else:
                                print("Other case")
                                continue
                        else:
                            return False
                    else:
                        return False
            elif("sk" in args1[i] and "sk" not in args2[i]):
                return False
            elif("sk" in args2[i] and "sk" not in args1[i]):
                return False
            elif(args1[i] != args2[i]):
                return False
        return False

    def __eq__(self, object) -> bool:
        if(self.args == object.args and self.name == object.name and self.truth_value == object.truth_value):
            return True
        if(self.name == object.name and self.truth_value == object.truth_value):
            return self.equate_args(self.args, object.args)
        if(self.args == object.args and self.name == object.name and self.truth_value != object.truth_value):
            raise ValueError("Contradiction")
        return False

    def __str__(self) -> str:
        return "{n}: {s} => {t}".format(n=self.name, s=self.args, t=self.truth_value)

class SkolemFunction():
    def __init__(self, index, args, arity):
        pass

with open("BFO2020-kowalski.txt", "r") as kowalski:
    for line in kowalski:
        if(line[0] == "r"):
            rules.append(line)

#rules can be structured as follows: r\([0-9])
# print(len(rules))
# print(rules[0])

def output(file):
    pass

def split(string, index):
    terms = []
    replacements = []
    id1 = -1
    id2 = -1
    if '[' in string:
        id1 = string.index('[')
    if ']' in string:
        id2 = string.index(']')
    while '[' in string:
        if id1 < id2:
            index = string.index('[')
            replacements.append(split(string[index+1:], index+1))
            id = string.index(']')
            count = string[index:id].count('[') #initial justification
            match = re.finditer(']', string[index:])
            match = list(match)
            #finish this
            while(string[index:index+match[count-1].span(0)[1]].count('[') != count):
                count = string[index:index+match[count-1].span(0)[1]].count('[')

            string = string.replace(string[index:index+match[count-1].span(0)[1]], 're', 1)
            if '[' in string:
                id1 = string.index('[')
            if ']' in string:
                id2 = string.index(']')
        else:
            if(']' not in string): #then we can wrap up
                terms = string.split(',')
                return terms
            id = string.index(']') #look for the first instance of this within the scope
            terms = string[:id].split(',')
            while 're' in terms:
                index = terms.index('re')
                terms[index] = replacements[0]
                replacements.pop(0)
            return terms
    #there's an edge case here in cases with the string B,C]],immaterial-entity,C]
    if ']' not in string: #if everything is taken care of
        terms = string.split(',')
        while 're' in terms:
            index = terms.index('re')
            terms[index] = replacements[0]
            replacements.pop(0)
        return terms
    else: #if there is still a ]
        id = string.index(']') #locate where it is
        terms = string[:id].split(',')
        while 're' in terms:
            index = terms.index('re')
            terms[index] = replacements[0]
            replacements.pop(0)
        return terms

def split_if_clause(if_clause, arity, index, skolems, has_skolem=False):
    s1 = re.search('\[.+\]', if_clause)
    result = s1.group(0)
    #trim off the outer-most brackets
    result = result[1:-1]
    #split based on differrent clauses
    terms = []
    terms = split(result, 0)
    # terms = list(filter(('').__ne__, terms))
    if(len(terms) != arity):
        raise Exception("Arity does not match number of clauses")
    for i in range(len(terms)):
        #trim off outer-most brackets
        if(has_skolem):
            if(any(isinstance(t, list) for t in terms[i])):
                skolem = next(t for t in terms[i] if isinstance(t, list))
                sk = skolem[1]
                if sk not in skolems:
                    skolems[sk] = []
                if index not in skolems[sk]:
                    skolems[sk].append(index)
    return terms

def split_then_clause(then_clause):
    s1 = re.search('\[.+\]', then_clause)
    result = s1.group(0)
    #trim off the outer-most brackets
    result = result[1:-1]
    terms = split(result, 0)
    return terms

def parse_rule(line, skolem_list):
    has_skolem = False
    parse_list = line.split(",") #this is bad
    # print(parse_list)
    se = re.finditer('[0-9]+', line)
    se = list(se)
    index = int(se[0].group(0))
    arity = int(se[1].group(0))
    find_skolems = re.search('\[([0-9]+)+(,[0-9]+)*\]', line)
    skolem_string = []
    if(find_skolems != None):
        has_skolem = True
        skolem_string = find_skolems.group(0)
        skolem_string = skolem_string[1:-1]
        skolem_string = skolem_string.split(",")
        for id in skolem_string:
            if id not in skolem_list:
                skolem_list[id] = []
            if index not in skolem_list[id]:
                skolem_list[id].append(index)

    #find if clause
    if_s = re.search('(if)\(.+?\)', line)
    if if_s != None:
        if_clause = if_s.group(0)

    #turn if clause into a rule
    if(if_s == None):
        if_terms = ["True"]
    else:
        if_terms = split_if_clause(if_clause, arity, index, skolem_list, has_skolem)
    #find then clause
    then_s = re.search('(then|then_or)\(.+?\)', line)
    if(then_s == None):
        then_terms = ["False"]
    else:
        then_clause = then_s.group(0)
        then_terms = split_then_clause(then_clause)
    # print("Index:", index)
    # print("If terms:", if_terms)
    # print("Then terms:", then_terms)
    rule = Rule(index, if_terms, then_terms, has_skolem, skolem_string)
    #handle the skolems after the fact has been created
    return rule

def parse_line(line):
    #assert that the line is formatted properly
    format = re.search('\[(.)+\]', line)
    content = format.group(0)
    content = content[1:-1]
    terms = content.split(", ")
    fact = Fact(terms[0], terms[1:], True)
    fact.rules_from.append(0)
    return fact

def read_rules(rule_file, skolem):
    rule_list = {}
    rule_count = 1
    with open(rule_file, "r") as rules:
        for line in rules:
            if(line[0] == "r"):
                rule = parse_rule(line, skolem)
                rule_list[rule_count] = rule
                rule_count += 1
    return rule_list

def query(rule_part, fact_part, facts):
    question = ["instance-of", fact_part, rule_part, "t"]
    # print("Question:", question)
    for key, value in facts.items():
        if value.name == question[0]:
            if(value.args == question[1:]):
                # print("YES")
                return True
    # print("NO")
    return False

def is_variable(element):
    return len(element) == 1 and element.upper

def is_skolem(element):
    return isinstance(element, list)

def recursive_search(clause_index, rule, facts, dictionary, history, subs, skolem_table):
    if(len(history) > len(rule)):
        print(history)
        raise ValueError("STOP")
    current_clause = rule[clause_index]
    for i in range(len(facts[clause_index])):
        fact = facts[clause_index][i]
        # print("Fact# {} for clause {}".format(fact[0], clause_index))
        failure = False
        dict_copy = copy.copy(dictionary)
        current_fact = fact[1]
        if(current_fact.name != current_clause[0]):
            # print("FAIL, PREDICATE NAMES DO NOT MATCH")
            continue
        else:
            for i in range(1, len(current_clause)):
                element = current_clause[i]
                if(is_variable(element)):
                    if element in dictionary:
                        if(current_fact.args[i-1] != dictionary[element]):
                            # print("FAIL, INCONSITENCY BETWEEN VARIABLES")
                            failure = True
                            break
                    else:
                        dict_copy[element] = current_fact.args[i-1]
                        # print("Set {} to {}".format(element, current_fact.args[i-1]))
                elif(is_skolem(element)):
                    # print("Set skolem {}".format(element))
                    # print("Current fact args {}".format(current_fact.args[i-1]))
                    if(check_skolem(element, current_fact.args[i-1], skolem_table, dict_copy)):
                        if("sk" in dict_copy):
                            raise ValueError()
                        dict_copy["sk"] = current_fact.args[i-1]
                        # print("Set {} to {}".format("sk", current_fact.args[i-1]))
                    else:
                        failure = True
                else:
                    if(element != current_fact.args[i-1]):
                        # print("FAIL, UNIVERSALS DO NOT MATCH")
                        failure = True
                        break
            if(not failure):
                if(clause_index != len(rule) - 1):
                    assert isinstance(fact[0], int)
                    history.append(fact[0])
                    recursive_search(clause_index+1, rule, facts, dict_copy, history, subs, skolem_table)
                else:
                    s = copy.deepcopy(history)
                    s.append(fact[0])
                    subs.append((s, dict_copy))
    if(len(history) != 0):
        history.pop(len(history)-1)

def check_mtp_with_falsehoods():
    pass

def get_candidate_facts(clauses, facts, skolem_table):
    candidate_facts = []
    for clause in clauses: #do some more prefiltering
        #identify the universals in the clause
        keywords = [term for term in clause if not is_skolem(term) and not is_variable(term)]
        valid = []
        for id, fact in facts.items():
            if (fact.name == clause[0]):
                keywords_in_clause = [term for term in keywords if term in fact.args]
                if(len(keywords_in_clause)+1 == len(keywords) and check_internal_subs(fact, clause, skolem_table)):
                    valid.append((id, fact))
        candidate_facts.append(valid)
    return candidate_facts

def check_skolem(element, fact_part, table, dict):
    if("sk" not in fact_part):
        return False
    else:
        skolem = table[fact_part]
        if(skolem[1] != element[1]):
            return False
        else: #if this is true
            #we check this recursively
            for i in range(len(element[2])):
                str = element[2][i]
                print(str)
                if(is_variable(str)):
                    if str in dict:
                        if dict[str] != skolem[2][i]:
                            return False
                    else:
                        dict[str] = skolem[2][i]
                        print("Set {} to {} from check_skolem".format(str, skolem[2][i]))
            
            return True

def substitute_skolem(skolem_table, skolem_counter, element, dict, args, index):
    # print("Substituting skolem")
    # print("Skolem counter:", skolem_counter)
    # print(dict)
    e = copy.copy(element)
    for i in range(len(e[2])):
        e[2][i] = dict[e[2][i]]
    replacement = "sk"
    if e in skolem_table.values():
        function = [key for key, value in skolem_table.items() if value == e]
        replacement = function[0]
    else:
        replacement += str(skolem_counter)
        skolem_table[replacement] = e
    args[index] = replacement


def verify_skolem():
    pass

def get_derivation(fact, facts): #get all other facts used in a derivation
    derivation = []
    if(facts[fact].derivation == None):
        return [fact]
    else:
        for f in facts[fact].derivation:
            if f not in derivation:
                derivation += get_derivation(f, facts)
    return derivation + [fact]

def evaluate_skolem():
    pass
#modus tollendo ponens

def add_facts():
    pass

def check_falsehoods(rules, facts, fact_counter, skolem_table, skolem_counter, skolem_list, current_skolem=None):
    print("Check falsehoods")
    print("Modus ponendo tollens")
    print("Current skolem:", current_skolem)
    skolem_save = copy.deepcopy(skolem_table)
    for index, rule in rules.items():
        if(rule.then_terms == ["False"]):
            fact_counter = check_mtp(rule, facts, skolem_table, index, skolem_counter, fact_counter, skolem_list, current_skolem)
    print("Modus tollendo ponens")
    for index, rule in rules.items():
        if(rule.then_terms != ["False"]):
            if(not rule.is_then_or):
                candidate_facts = get_candidate_facts([rule.then_terms], facts, skolem_table)
                candidate_facts = [[fact for fact in clause if not bool(fact[1].truth_value)] for clause in candidate_facts]
                if([] not in candidate_facts):
                    if(len(candidate_facts) > 1):
                        raise ValueError("Need to worry about this as well")
                    candidate_facts = candidate_facts[0]
                    if(len(rule.if_terms) == 1): #then we can immediately infer that this fact is also false
                        pass
                        for fact in candidate_facts:
                            if(not fact[1].truth_value): #if the fact is false
                                dict = check_internal_subs(fact[1], rule.then_terms, skolem_table, return_dict=True)
                                args = copy.deepcopy(rule.if_terms[0])
                                for i in range(len(args)):
                                    element = args[i]
                                    if(is_variable(element)):
                                        if(element in dict):
                                            args[i] = dict[element]
                                new_fact = Fact(args[0], args[1:], False, derivation=fact[0])
                                free_variables = sum(map(lambda x: bool(is_variable(x)), args))
                                if(new_fact not in facts.values() and free_variables == 0): #double check there are no free variables in the substitution
                                    print("VALID FACT")
                                    print("New fact:", fact_counter)
                                    facts[fact_counter] = new_fact
                                    print(new_fact)
                                    print("")
                                    fact_counter += 1
                    else:
                        print("Cannot conclude anything")
                        print(candidate_facts)
                        candidate_if_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                        candidate_if_facts = [[fact for fact in clause if bool(fact[1].truth_value)] for clause in candidate_if_facts]

                        if ([] not in candidate_if_facts):
                            print(candidate_if_facts)
                            terms = rule.if_terms + rule.then_terms
                            candidates = candidate_if_facts + [candidate_facts]
                            print(candidates)
                            dict = {}
                            history = []
                            subs = []
                            recursive_search(0, terms, candidates, dict, history, subs, skolem_table)
                            if(len(subs) == 0):
                                continue
                            else:
                                raise ValueError("Check Modus ponendo tollens")
                            print(candidate_if_facts)
                            for fact in candidate_facts:
                                print(fact[1].truth_value)
            else:
                print("Rule #", index, ":", rule)
                candidate_facts = get_candidate_facts(rule.then_terms, facts, skolem_table)
                candidate_facts = [[fact for fact in clause if not bool(fact[1].truth_value)] for clause in candidate_facts]
                print(candidate_facts)
                if([] not in candidate_facts):
                    candidate_if_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                    terms = rule.if_terms + rule.then_terms
                    candidates = candidate_if_facts + candidate_facts
                    dict = {}
                    history = []
                    subs = []
                    recursive_search(0, terms, candidates, dict, history, subs, skolem_table)
                    if(len(subs) == 0):
                        continue
                    else:
                        print(subs)
                        for substitution in subs:
                            print(substitution)
                        print("Check Modus ponendo tollens")


    print("Done")
    print_facts(facts)
    pass

def print_facts(facts):
    for index, fact in facts.items():
        print("Fact # {}: {}.".format(index, fact))

def check_internal_subs(fact, clause, skolem_table, return_dict=False, existing=None):
        failure = False
        current_clause = clause
        current_fact = fact
        dictionary = {}
        if(existing != None):
            dictionary = existing
        for i in range(1, len(current_clause)):
            element = current_clause[i]
            if(is_variable(element)):
                if element in dictionary:
                    if(current_fact.args[i-1] != dictionary[element]):
                        # print("FAIL, INCONSITENCY BETWEEN VARIABLES")
                        failure = True
                        break
                else:
                    dictionary[element] = current_fact.args[i-1]
            elif(is_skolem(element)):
                if(check_skolem(element, current_fact.args[i-1], skolem_table, dictionary)):
                    # print("Success")
                    if("sk" not in dictionary):
                        dictionary["sk"] = []
                    if(current_fact.args[i-1] not in dictionary["sk"]):
                        dictionary["sk"].append(current_fact.args[i-1])
                    print("Set {} to {}".format("sk", current_fact.args[i-1]))
                else:
                    failure = True
            else:
                if(element != current_fact.args[i-1]):
                    # print("FAIL, UNIVERSALS DO NOT MATCH")
                    failure = True
                    break
        if(failure):
            return False
        if(return_dict):
            return dictionary
        return True

def skolem_search(skolem, skolem_table, depth):
    if(depth > MAX_SKOLEM_DEPTH):
        return False
    sk = skolem_table[skolem]
    print("Look through skolem function", skolem)
    for e in sk[2]:
        print(e)
        if "sk" in e:
            if(skolem_search(e, skolem_table, depth+1)):
                continue
            else:
                return False
    return True
    pass
def check_fact(facts, new_fact, dict, skolem_table):
    reverse_dict = {}
    char = 'A'
    c = copy.deepcopy(new_fact)
    for i in range(len(c.args)):
        element = c.args[i]
        if "sk" in element:
            # result = skolem_search(element, skolem_table, 1)
            # print(result)
            # if(not result):
            #     print("Exceeds maximum skolem depth.")
            #     return False
            reverse_dict[element] = str(char)
            char = chr(ord(char) + 1)
            c.args[i] = reverse_dict[element]
    clause = [c.name]
    clause += c.args
    candidates = get_candidate_facts([clause], facts, skolem_table)
    if(len(candidates) != 0 and [] not in candidates):
        for candidate in candidates:
            for fact in candidate:
                # print(fact[1])
                for i in range(len(fact[1].args)):
                    arg = fact[1].args[i]
                    # print(new_fact.args[i])
                    # print("sk" in new_fact.args[i])
                    # print(arg)
                    # print("sk" in arg)
                    if("sk" in arg and "sk" not in new_fact.args[i]):
                        return True
                    elif("sk" not in arg and "sk" in new_fact.args[i]):
                        return False
        return False
    else:
        return True
    pass

def unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=2):
    #we should look for valid facts that match the index of the rule
            fact_count = len(facts.items())
            new_skolem = []
            candidate_facts = get_candidate_facts(rule.if_terms, current_fact, skolem_table)
            if ([] in candidate_facts and len(rule.if_terms) == 1):
                return
            if(len(rule.if_terms) > current_arity):
                return
            if(len(rule.if_terms) > 1):
                empty = [[] for i in range(len(candidate_facts))]
                if(candidate_facts == empty):
                    return
            dict = {}
            history = []
            substitutions = []
            if(len(rule.if_terms) > 1):
                print("Rule #", rule.index)
                old_candidate_facts = copy.deepcopy(candidate_facts)

                candidate_facts = [[] for i in range(len(old_candidate_facts))]
                extra_candidate_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                if([] in old_candidate_facts and [] not in extra_candidate_facts):
                    #for each non empty clause in the old_candidate_facts
                    non_empty = [i for i in range(len(old_candidate_facts)) if len(old_candidate_facts[i]) != 0]
                    if(len(non_empty) == 1):
                        for i in range(len(candidate_facts)):
                            if(i == non_empty[0]):
                                candidate_facts[i] = old_candidate_facts[i]
                            else:
                                candidate_facts[i] = extra_candidate_facts[i]
                    else:
                        candidate_facts = extra_candidate_facts
                else:
                    candidate_facts = extra_candidate_facts
            else:
                pass
            recursive_search(0, rule.if_terms, candidate_facts, dict, history, substitutions, skolem_table)
            if(len(rule.if_terms) > 1):
                key = list(current_fact.keys())[0]
                substitutions = [s for s in substitutions if key in s[0]]

            if(len(substitutions) == 0):
                return
            if(len(rule.if_terms) > 1):
                if(len(substitutions) != 1):
                    substitutions.reverse()
            for substitution in substitutions:
                dict = substitution[1]
                args = copy.deepcopy(rule.then_terms)
                for i in range(len(args)):
                    element = args[i]
                    if(is_variable(element)):
                        if element in dict:
                            args[i] = dict[element]
                        else:
                            raise ValueError("Major consistency error")
                    elif(is_skolem(element)):
                        skolem_copy = copy.copy(skolem_table)
                        substitute_skolem(skolem_table, skolem_counter, element, dict, args, i)
                        if(skolem_table != skolem_copy):
                            new_skolem.append(args[i])
                        skolem_counter = len(skolem_table.items())+1
                new_fact = Fact(args[0], args[1:], True, derivation=substitution[0])
                free_variables = sum(map(lambda x: is_variable(x) == True, args))
                # print("Fact not in facts: {}".format(new_fact not in facts.values()))
                if(free_variables == 0 and new_fact not in facts.values()):
                    if(len(new_skolem) != 0 or rule.has_skolem):
                        if(check_fact(facts, new_fact, dict, skolem_table)):
                            print("New fact #{}: {}".format(fact_counter, new_fact))
                            facts[fact_counter] = new_fact
                            facts[fact_counter].rules_from.append(rule.index)
                            print("")
                            for fact in new_fact.derivation:
                                facts[fact].rules_used.append(rule.index)
                            for element in facts[fact_counter].args:
                                if "sk" in element:
                                    if element not in skolems_per_fact:
                                        skolems_per_fact[element] = []
                                    skolems_per_fact[element].append(fact_counter)
                            fact_counter += 1
                        else:
                            for skolem in new_skolem:
                                if skolem in skolem_table:
                                    del skolem_table[skolem]
                            skolem_counter = len(skolem_table.items()) + 1
                            continue
                    else:
                        c = check_fact(facts, new_fact, dict, skolem_table)
                        print(c)
                        print("New fact #{}: {}".format(fact_counter, new_fact))
                        facts[fact_counter] = new_fact
                        facts[fact_counter].rules_from.append(rule.index)
                        for fact in new_fact.derivation:
                            facts[fact].rules_used.append(rule.index)
                        for element in facts[fact_counter].args:
                            if "sk" in element:
                                if element not in skolems_per_fact:
                                    skolems_per_fact[element] = []
                                skolems_per_fact[element].append(fact_counter)
                        fact_counter += 1
                else:
                    for skolem in new_skolem:
                        if skolem in skolem_table:
                            del skolem_table[skolem]


def substitute(clause, dict):
    args = copy.deepcopy(clause)
    for i in range(len(args)):
        element = args[i]
        if(is_variable(element)):
            if element in dict:
                args[i] = dict[element]
            else:
                print("Not enough information")
                return None
    return args

def check_mtp(rule, facts, skolem_table, index, skolem_counter, fact_counter, current_fact):
    new_skolem = []
    candidate_facts = get_candidate_facts(rule.if_terms, current_fact, skolem_table)
    non_empty = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) != 0]
    if(len(non_empty) > 0):
        print("Rule #", rule.index)
        print("Candidate facts: {}".format(candidate_facts))
        #check for contradiction
        if(list(current_fact.values())[0].truth_value):
            if(len(rule.if_terms) == 1):
                raise ValueError("Contradiction")
            if(len(rule.if_terms) == 2): #then we can immediately conclude that the other fact must be false
                print("Then we can immediately conclude that the other fact must be false")
                empty = [j for j in range(len(candidate_facts)) if j not in non_empty]
                moves = check_internal_subs(list(current_fact.values())[0], rule.if_terms[non_empty[0]], skolem_table, return_dict=True)
                print(moves)
                args = substitute(rule.if_terms[empty[0]], moves)
                if(args != None):
                    print(args)
                    new_fact = Fact(args[0], args[1:], False, derivation=[list(current_fact.keys())[0]])
                    free_variables = sum(map(lambda x: bool(is_variable(x)), args))
                    if(new_fact not in facts.values() and free_variables == 0):
                        print("VALID FACT")
                        print("New fact:", fact_counter)
                        facts[fact_counter] = new_fact
                        print(new_fact)
                        print(new_fact.derivation)
                        print("")
                        fact_counter += 1
                        for fact in new_fact.derivation:
                            facts[fact].rules_used.append(rule.index)
            else:
                print("Rule #", rule.index)
                candidate_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                non_empty = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) != 0]
                if (len(non_empty) >= len(candidate_facts)-1):
                    dict = {}
                    history = []
                    subs = []
                    check_elements = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) != 0]
                    if(len(non_empty) == len(candidate_facts) - 1):

                        candidates = [candidate_facts[j] for j in check_elements]
                        rule_terms = [rule.if_terms[k] for k in check_elements]
                    else:
                        candidates = candidate_facts
                        rule_terms = rule.if_terms
                    recursive_search(0, rule_terms, candidates, dict, history, subs, skolem_table)
                    print(subs)
                    key = list(current_fact.keys())[0]
                    print(key)
                    subs = [s for s in subs if key in s[0]]
                    print(subs)
                    if(len(subs) == 0):
                        print("No facts found for given rule")
                    for substitution in subs:
                        print(substitution)
                        for i in range(len(rule.if_terms)):
                            if(i not in check_elements):
                                args = substitute(rule.if_terms[i], substitution[1])
                                if(args != None):
                                    new_fact = Fact(args[0], args[1:], False, derivation=[list(current_fact.keys())[0]])
                                    free_variables = sum(map(lambda x: bool(is_variable(x)), args))
                                    if(new_fact not in facts.values() and free_variables == 0):
                                        print("VALID FACT")
                                        print("New fact:", fact_counter)
                                        facts[fact_counter] = new_fact
                                        print(new_fact)
                                        print(new_fact.derivation)
                                        print("")
                                        fact_counter += 1
                                        for fact in new_fact.derivation:
                                            facts[fact].rules_used.append(rule.index)

def derive_falsehoods(facts, rules, fact_counter, rule_order, skolem_table, skolem_counter):
    print("Modus Tollendo Tollens")
    fact_index = len(facts.items())
    fact_count = len(facts.items())
    while(fact_index > 0):
        print("Fact", str(fact_index) + "," + str(facts[fact_index]))
        current_fact = {fact_index: facts[fact_index]}
        for index in rule_order:
            rule = rules[index]
            if(rule.then_terms == ["False"]):
                # if len(facts[fact_index].rules_used) != 0:
                #     if index in facts[fact_index].rules_used:
                #         print("Rule found")
                #         continue
                check_mtp(rule, facts, skolem_table, index, skolem_counter, fact_counter, current_fact)
                fact_counter = len(facts.items())+1
                if(len(facts.items()) != fact_count):
                    print("NEW FACT")
                    break
        if(len(facts.items()) > 600):
            return None
        if(len(facts.items()) == fact_count):
            fact_index -= 1
        else:
            fact_count = len(facts.items())
            fact_index = len(facts.items())

#error with immaterial entity facts being fired
def forward_chaining(facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact):
    fact_count = len(facts.items())
    fact_index = fact_counter-1
    fact_checks = {}
    for index, fact in facts.items():
        fact_checks[index] = False
    current_fact = {fact_counter-1: facts[fact_counter-1]}
    print(current_fact)
    print_facts(facts)
    fact_index = fact_counter-1
    arity_index = 1
    cut_off = 0
    while(fact_index > 0):
        fact_count = len(facts.items())
        print("Fact #{}:{}".format(fact_index, facts[fact_index]))
        current_fact = {fact_index: facts[fact_index]}
        if(not fact_checks[fact_index]):
            for index in rule_order:
                num_old_facts = len(facts.items())
                rule = rules[index]
                if(not rule.is_then_or):
                    if(len(rule.if_terms) <= arity_index):
                        unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=arity_index)
                        fact_counter = len(facts.items()) + 1
                        skolem_counter = len(skolem_table.items())+1
                        if(len(rule.if_terms) > 1 and fact_count != len(facts.items())):
                            break
        if(arity_index == 1):
            fact_checks[fact_index] = True
        if(fact_count != len(facts.items())):
            for i, f in facts.items():
                if i not in fact_checks:
                    fact_checks[i] = False
            fact_index = len(facts.items())
        else:
            fact_index -= 1
        if(fact_index == 0 and arity_index < MAX_ARITY):
            print("MOVE ONTO ARITY", arity_index+1)
            fact_index = len(facts.items())
            for i, f in facts.items():
                fact_checks[i] = False
            arity_index += 1
    print("GENERATED ALL POSITIVE FACTS")
    print_facts(facts)
    print(skolem_table)

def write_facts_to_csv(file, facts):
    f = open(file, 'w')

    writer = csv.writer(f, lineterminator='\n')

    for index, fact in facts.items():
        data = []
        data.append(index)
        data.append(fact.truth_value)
        data.append(fact.name)
        for i in range(MAX_ARGS):
            if(i < len(fact.args)):
                data.append(fact.args[i])
            else:
                data.append("")
        data.append("<--")
        for j in range(len(fact.rules_from)):
            data.append(fact.rules_from[j])
        for k in range(MAX_FACTS):
            if(fact.derivation != None):
                if(k < len(fact.derivation)):
                    data.append(fact.derivation[k])
                else:
                    data.append("")
            else:
                data.append("")
        writer.writerow(data)


def init(input_file, rule_file="BFO2020-kowalski-with-identity-rules.txt"):
    sk_consts = {}
    rules = read_rules(rule_file, sk_consts)
    # print(sk_consts["134"])
    # print(sk_consts["136"])
    # print(rules[457])
    # print(rules[458])
    facts = {}
    fact_counter = 1
    with open(input_file, "r") as file:
        for line in file:
            if(line[0] == "%"):
                continue
            fact = parse_line(line)
            facts[fact_counter] = fact
            fact_counter+=1
    return rules, facts, fact_counter, sk_consts

def organize_rules(rules):
    rule_order = {}
    for key, value in rules.items():
        if value.antecedents not in rule_order:
            rule_order[value.antecedents] = {}
        if value.arity not in rule_order[value.antecedents]:
            rule_order[value.antecedents][value.arity] = []
        rule_order[value.antecedents][value.arity].append(value.index)
    order = []
    for value in rule_order.values():
        for val in value.values():
            for rule in val:
                order.append(rule)
    return order
    #1. check start conditions
    #2. Generate indexes for the antecedents
    #3. Organize rules
    #4. Read input
    #inference loop
    #while the number of new facts does not equal the number of current facts:
    #   start with forward chaining for positive facts
    #   check for inconsistencies
    #   derive what can be derived
    #   derive negative facts
    #   derive facts through then_or rules
    #   obtain the number of facts through then_or rules

#   Check for starting conditions
#   list_question_types: indexing the rules
#   saveData
# process the rules with the least number of conditions first
# if there are more facts at the end of the procedure than the beginning, keep looping. 
#1. forward chaining,
#2. check for falsehoods every time a new rule is created

#Detect equalities amongst input

#Generate positive facts
#Check for equality
#Check for inconsistencies
#Check for negative facts

#how to check 

#generate Skolem constant
#avoid Skolem cycles

#equalities 

#identical
if __name__ =="__main__":
    input_file = "mytest-input.txt"
    rules, start_facts, fact_counter, skolem_list = init(input_file)
    rule_order = organize_rules(rules)
    fact_count = len(start_facts.items())
    skolem_counter = 1
    skolem_table = {}
    skolems_per_fact = {}
    # derive_falsehoods(start_facts, rules, fact_counter, rule_order, skolem_list)
    forward_chaining(start_facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact)
    skolem_counter = len(skolem_table.items()) + 1
    # if(len(start_facts.items()) != fact_count):
    #     derive_falsehoods(start_facts, rules, fact_counter, rule_order, skolem_table, skolem_counter)
    write_facts_to_csv("./output.csv", start_facts)