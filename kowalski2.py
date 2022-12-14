from audioop import mul
import re
import copy
import csv
import time
MAX_SKOLEM_DEPTH = 2
MAX_ARITY = 2
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
                                # print("Other case")
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
            print("CONTRADICTION")
            # print(self)
            # print(object)
            # print(skolem_table)
            # raise ValueError("Contradiction")
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

def parse_line(line, skolem_table, skolem_counter):
    #assert that the line is formatted properly
    format = re.search('\[(.)+\]', line)
    content = format.group(0)
    content = content[1:-1]
    terms = split(content, 0)
    for i in range(len(terms)):
        term = terms[i]
        if(is_skolem(term)):
            # print(term)
            key = ""
            if(term not in skolem_table.values()):
                print(skolem_counter)
                key = "sk" + str(skolem_counter)
                skolem_table[key] = term
                skolem_counter = len(skolem_table.items()) + 1
            else:
                for k, value in skolem_table.items():
                    if skolem_table[k] == term:
                        key = k
            terms[i] = key
    fact = Fact(terms[0], terms[1:], True)
    fact.rules_from.append(0)
    print(fact)
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

def is_variable(element):
    return len(element) == 1 and element.upper

def is_skolem(element):
    return isinstance(element, list)

def recursive_search(clause_index, rule, facts, dictionary, history, subs, skolem_table):
    if(len(history) > len(rule)):
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
                if(is_variable(str)):
                    if str in dict:
                        if dict[str] != skolem[2][i]:
                            return False
                    else:
                        dict[str] = skolem[2][i]
            
            return True

def substitute_skolem(skolem_table, skolem_counter, element, dict, args, index):
    # print("Substituting skolem")
    # print("Skolem counter:", skolem_counter)
    # print(dict)
    e = copy.copy(element)
    for i in range(len(e[2])):
        if(e[2][i] not in dict):
            return -1
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
                                    # print("VALID FACT")
                                    # print("New fact:", fact_counter)
                                    facts[fact_counter] = new_fact
                                    # print(new_fact)
                                    # print("")
                                    fact_counter += 1
                    else:
                        # print("Cannot conclude anything")
                        # print(candidate_facts)
                        candidate_if_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                        candidate_if_facts = [[fact for fact in clause if bool(fact[1].truth_value)] for clause in candidate_if_facts]

                        if ([] not in candidate_if_facts):
                            # print(candidate_if_facts)
                            terms = rule.if_terms + rule.then_terms
                            candidates = candidate_if_facts + [candidate_facts]
                            # print(candidates)
                            dict = {}
                            history = []
                            subs = []
                            recursive_search(0, terms, candidates, dict, history, subs, skolem_table)
                            if(len(subs) == 0):
                                continue
                            else:
                                raise ValueError("Check Modus ponendo tollens")
            else:
                # print("Rule #", index, ":", rule)
                candidate_facts = get_candidate_facts(rule.then_terms, facts, skolem_table)
                candidate_facts = [[fact for fact in clause if not bool(fact[1].truth_value)] for clause in candidate_facts]
                # print(candidate_facts)
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
        if(current_fact.name != clause[0]):
            if(existing != None):
                return existing
            return False
        if(existing != None):
            dictionary = copy.deepcopy(existing)
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
                    # print("Set {} to {}".format("sk", current_fact.args[i-1]))
                else:
                    failure = True
            else:
                if(element != current_fact.args[i-1]):
                    # print("FAIL, UNIVERSALS DO NOT MATCH")
                    failure = True
                    break
        if(failure):
            if(existing != None):
                return existing
            else:
                return False
        if(return_dict):
            return dictionary
        return True

def skolem_search(skolem, skolem_table, depth):
    if(depth > MAX_SKOLEM_DEPTH):
        return False
    sk = skolem_table[skolem]
    for e in sk[2]:
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
        multiple_candidates = False
        candidate_facts = get_candidate_facts(rule.if_terms, current_fact, skolem_table)
        candidate_facts = [[fact for fact in candidate if bool(fact[1].truth_value)] for candidate in candidate_facts]
        if ([] in candidate_facts and len(rule.if_terms) == 1):
            return
        if(list(current_fact.keys())[0] == 297 and rule.index == 111):
            pass
            print("FLAG")
            print(candidate_facts)
        #first we want to check the candidates for the consequent
        consequence_facts = get_candidate_facts([rule.then_terms], facts, skolem_table)
        
        rule_terms, candidates = get_non_empty(candidate_facts, rule.if_terms)
        dict = {}
        valid_fact = False
        called_index = -1
        derivation = []
        # print("Derivation step 1")
        for i in range(len(candidates)):
            for j in range(len(candidates[i])):
                can = candidates[i][j]
                print(can[1])
                print(rule_terms[i])
                dict = check_internal_subs(can[1], rule_terms[i], skolem_table, return_dict=True, existing=dict)
                print(dict)
                if(dict != False and len(dict.items()) != 0):
                    called_index = rule.if_terms.index(rule_terms[i])
                    derivation.append(list(current_fact.keys())[0])
                    break
            if(dict != False and len(dict.items()) != 0):
                break
        
        if(list(current_fact.keys())[0] == 297 and rule.index == 111):
            pass
            print("FLAG 2")
            print(dict)
        if(dict == False or len(dict.items()) == 0):
            return
        # print("GOOD")
        print(list(current_fact.values())[0])
        print(dict)
        print("Rule #", rule.index)
        print(rule)
        print("Derivation step 2")
        print(called_index)
        arg_array = [[] for i in range(len(rule.if_terms))]
        arg_array[called_index] = substitute(rule.if_terms[called_index], dict, new_skolem, skolem_table, skolem_counter)
        possible_subs = [] #this is where things get complicated
        for i in range(len(rule.if_terms)):
            if(i != called_index):
                args = substitute(rule.if_terms[i], dict, new_skolem, skolem_table, skolem_counter)
                print("Result of substitute:", args)
                if(args == None): #on fails
                    candidate_facts = get_candidate_facts([rule.if_terms[i]], facts, skolem_table)
                    candidate_facts = candidate_facts[0]
                    for j in range(len(candidate_facts)):
                        print(candidate_facts[j][1])
                        new_dict = check_internal_subs(candidate_facts[j][1], rule.if_terms[i], skolem_table, return_dict=True, existing=dict)
                        print(new_dict)
                        print(dict)
                        if(new_dict == dict and len(new_dict.items()) == len(dict.items())):
                            print("No dice")
                            continue
                        else:
                            possible_subs.append(new_dict)
                else:
                    arg_array[i] = args
                    print(arg_array[i])
                    temp_fact = Fact(args[0], args[1:], True)
                    if(temp_fact not in facts.values()):
                        arg_array[i] = []
                    else:
                        print("Fact found")
                        derivation.append(list(facts.values()).index(temp_fact))
        print("Check")
        print(arg_array)
        print(possible_subs)
        if([] in arg_array and len(possible_subs) != 0):
            if(len(possible_subs) == 1):
                dict = possible_subs[0]
                for i in range(len(arg_array)):
                    if(arg_array[i] == []):
                        print(rule.if_terms[i])
                        arg_array[i] = substitute(rule.if_terms[i], dict, new_skolem, skolem_table, skolem_counter)
                        if(arg_array[i] == None):
                            arg_array[i] = []
                print("RESULT")
            else:
                arg_list = []
                sub_list = []
                for sub in possible_subs:
                    args_copy = copy.deepcopy(arg_array)
                    for i in range(len(arg_array)):
                        print("New entry")
                        if(args_copy[i] == []):
                            args_copy[i] = substitute(rule.if_terms[i], sub, new_skolem, skolem_table, skolem_counter)
                            if(args_copy[i] != None):
                                print(args_copy[i])
                                temp_fact = Fact(args_copy[i][0], args_copy[i][1:], True)
                                if(temp_fact not in facts.values()):
                                    print("CANNOT PROCESS")
                                    args_copy[i] = []
                            else:
                                args_copy[i] = []
                    print(args_copy)
                    if([] not in args_copy):
                        if(len(arg_list) != 0):
                            multiple_candidates = True
                        arg_list.append(args_copy)
                        sub_list.append(sub)
                if(len(arg_list) == 1):
                    arg_array = arg_list[0]
                    possible_subs = sub_list
                elif(len(arg_list) == 0):
                    arg_array = [[]]
                else:
                    arg_array = arg_list
                    possible_subs = sub_list
        print(arg_array)
        if([] not in arg_array):
            valid_fact = True
        else:
            return
        sub_con = {}
        if(valid_fact != True):
            return
        arg_arrays = []
        if(multiple_candidates == True):
            #we want to resort them based on the minimum number of distinct terms that they have and the number of skolems
            # print(current_fact)
            # print(arg_array)
            arg_arrays = arg_array
        else:
            arg_arrays.append(arg_array)
        # print(possible_subs)
        print("CHECK")
        for i in range(len(arg_arrays)):
            # print("Top")
            # print(arg_arrays[i])
            if(len(arg_arrays) > 1):
                # print("FLAG 4")
                dict = possible_subs[i]
            # print(dict)
            # if([] not in consequence_facts):
            #     # print("Rule.then_terms:", rule.then_terms)
            #     # print("Similar facts")
            #     print(dict)
            #     consequence_facts = consequence_facts[0]
            #     print(consequence_facts)
            #     for fact in consequence_facts:
            #         sub_con = check_internal_subs(fact[1], rule.then_terms, skolem_table, return_dict=True)
            #         if(sub_con != False and len(sub_con.items()) != 0):
            #             break
            # if(sub_con != False and len(sub_con.items()) != 0):
            #     if(strong_equality(dict, sub_con)):
            #         valid_fact = False
            #     elif(all(key in sub_con.keys() for key in dict.keys())):
            #         for key in dict.keys():
            #             if sub_con[key] != dict[key]:
            #                 if "sk" in sub_con[key] and "sk" not in dict[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" in dict[key] and "sk" not in sub_con[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" not in dict[key] and "sk" not in sub_con[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" in dict[key] and "sk" in sub_con[key]:
            #                     # print("Skolems")
            #                     break
            #             else:
            #                 continue
            #             valid_fact = False
            #     elif(all(key in dict.keys() for key in sub_con.keys())):
            #         for key in sub_con.keys():
            #             if sub_con[key] != dict[key]:
            #                 if "sk" in sub_con[key] and "sk" not in dict[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" in dict[key] and "sk" not in sub_con[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" not in dict[key] and "sk" not in sub_con[key]:
            #                     valid_fact = True
            #                     break
            #                 elif "sk" in dict[key] and "sk" in sub_con[key]:
            #                     break
            #             else:
            #                 continue
            #             valid_fact = False
            if(len(rule.if_terms) > current_arity):
                return
            if(valid_fact):
                print("Valid fact")
                # print("Rule #{}: {}".format(rule.index, rule))
                # print(dict)
                # print(rule.if_terms)
                # print(rule.then_terms)
                args = substitute(rule.then_terms, dict, new_skolem, skolem_table, skolem_counter)
                print(args)
                if(args == None):
                    return
                new_fact = Fact(args[0], args[1:], True)
                new_fact.derivation = derivation
                free_variables = sum(map(lambda x: is_variable(x) == True, args))
                if(free_variables == 0 and new_fact not in facts.values()):
                    if(len(new_skolem) != 0 or rule.has_skolem):
                        if(check_fact(facts, new_fact, dict, skolem_table)):
                            print("New fact #{}: {}".format(fact_counter, new_fact))
                            facts[fact_counter] = new_fact
                            facts[fact_counter].rules_from.append(rule.index)
                            # print(new_fact.derivation)
                            # print("")
                            # for fact in new_fact.derivation:
                            #     facts[fact].rules_used.append(rule.index)
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
                            # continue
                    else:
                        c = check_fact(facts, new_fact, dict, skolem_table)
                        # print(c)
                        # print("New fact #{}: {}".format(fact_counter, new_fact))
                        facts[fact_counter] = new_fact
                        facts[fact_counter].rules_from.append(rule.index)
                        # print(new_fact.derivation)
                        # for fact in new_fact.derivation:
                        #     facts[fact].rules_used.append(rule.index)
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


def substitute(clause, dict, new_skolems, skolem_table, skolem_counter):
    args = copy.deepcopy(clause)
    for i in range(len(args)):
        element = args[i]
        if(is_variable(element)):
            if element in dict:
                args[i] = dict[element]
            else:
                # print("Not enough information")
                return None
        elif(is_skolem(element)):
            skolem_copy = copy.copy(skolem_table)
            result = substitute_skolem(skolem_table, skolem_counter, element, dict, args, i)
            if(result == -1):
                return None
            if(skolem_table != skolem_copy):
                new_skolems.append(args[i])
            skolem_counter = len(skolem_table.items())+1
    return args

def check_slots(non_empty, facts):
    if(len(non_empty) > 0):
        for candidate in non_empty:
            for fact in candidate:
                if(facts[fact[0]].truth_value):
                    return True
        return False

def check_app(candidates, facts):
    c_true = 0
    c_false = 0
    for i in range(len(candidates)):
        found_true = False
        candidate = candidates[i]
        for fact in candidate:
            if(facts[fact[0]].truth_value):
                c_true += 1
                found_true = True
                break
        if(not found_true and len(candidate) != 0):
            c_false += 1
    # print(c_true)
    if(c_true >= len(candidates)-1):
        return True
    return False

def get_non_empty(candidate_facts, if_terms):
    rule_terms = []
    candidates = []
    for i in range(len(candidate_facts)):
        candidate = candidate_facts[i]
        if(len(candidate) > 0):
            rule_terms.append(if_terms[i])
            candidates.append(candidate)
    return rule_terms, candidates

def get_empty(candidate_facts, if_terms):
    rule_terms = []
    for i in range(len(candidate_facts)):
        candidate = candidate_facts[i]
        if(len(candidate) == 0):
            rule_terms.append(if_terms[i])
    return rule_terms

def get_num_true(facts, gen):
    true = 0
    for f in gen:
        if f != None:
            if(bool(facts[f].truth_value)):
                true+=1
    return true

def get_num_false(facts, gen):
    false = 0
    for f in gen:
        if f != None:
            if(not bool(facts[f].truth_value)):
                false += 1
    return false
def strong_equality(dict1, dict2):
    for key in dict1.keys():
        if(key in dict2 and dict2[key] != dict1[key]):
            return False
    return True

def check_combinations(dict, candidate_facts, rules, current_rule, subs, facts, non_empty, skolem_table):
    array = []
    index = 0 
    for i in range(len(current_rule)):
        fact_found = False
        if(current_rule[i] not in rules):
            array.append(None)
        else:
            candidate = candidate_facts[i]
            if(len(candidate) > 0):
                for fact in candidate:
                    substitutions = check_internal_subs(fact[1], rules[index], skolem_table, return_dict=True)
                    if(substitutions != False and strong_equality(dict, substitutions)):
                        dict.update(substitutions)
                        array.append(fact[0])
                        fact_found = True
            if(not fact_found):
                array.append(None)
            index += 1
    subs.append((array, dict))

def check_mtp(rule, facts, skolem_table, index, skolem_counter, fact_counter, current_fact):
    new_skolem = []
    candidate_facts = get_candidate_facts(rule.if_terms, current_fact, skolem_table)
    non_empty = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) != 0]
    if(check_slots([candidate_facts[i] for i in non_empty], facts)):
        # print("Rule #", rule.index)
        # print(rule)
        # print("Candidate facts: {}".format(candidate_facts))
        #check for contradiction
        if(len(rule.if_terms) == 1):
            raise ValueError("Contradiction")
        if(len(rule.if_terms) > 1): #then we can immediately conclude that the other fact must be false
            old_candidate_facts = copy.deepcopy(candidate_facts)

            candidate_facts = [[] for i in range(len(old_candidate_facts))]
            extra_candidate_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
            if(len(candidate_facts) > 1):
                if([] in old_candidate_facts and [] not in extra_candidate_facts):
                    #for each non empty clause in the old_candidate_facts
                    non_empty = [i for i in range(len(old_candidate_facts)) if len(old_candidate_facts[i]) != 0]
                    if(len(non_empty) > 1):
                        for i in range(len(candidate_facts)):
                            if(i == non_empty[0]):
                                candidate_facts[i] = old_candidate_facts[i]
                            else:
                                candidate_facts[i] = extra_candidate_facts[i]
                    elif(len(non_empty) == 1):
                        candidate_facts = old_candidate_facts
                else:
                    candidate_facts = extra_candidate_facts
            else:
                candidate_facts = old_candidate_facts
            # print("Candidates: ", candidate_facts)
            if(check_app(candidate_facts, facts)):
                dict = {}
                history = []
                subs = []
                rule_terms, candidates = get_non_empty(candidate_facts, rule.if_terms)
                # print("Len(non_empty): {}".format(len(non_empty)))
                # print("Len(candidates): {}".format(len(candidates)))
                for i in range(len(non_empty)):
                    entry = non_empty[i]
                    # print(non_empty)
                    # print(entry)
                    # print(candidates[i])
                    
                    for can in candidates[i]:
                        substitutions = check_internal_subs(can[1], rule_terms[i], skolem_table, return_dict=True)
                        if(substitutions != False):
                            # print(substitutions)
                            break
                if(substitutions == False):
                    return 
                check_combinations(substitutions, candidate_facts, rule_terms, rule.if_terms, subs, facts, non_empty, skolem_table)
                if(len(subs) > 0):
                    for sub in subs:
                        # print(sub)
                        key = list(current_fact.keys())[0]
                        if(key not in sub[0]):
                            continue

                        empty_terms = [rule.if_terms[i] for i in range(len(rule.if_terms)) if sub[0][i] == None]
                        # print(empty_terms)
                        sub = (list(set(list(sub[0]))), sub[1])
                        if(len(empty_terms) == 0):
                            if(get_num_true(facts, sub[0]) == len(rule.if_terms)):
                                # print(sub[0])
                                # print(sub)
                                # print(rule.index)
                                # print(rule.if_terms)
                                # print(rule.then_terms)
                                # for f in sub[0]:
                                    # print("Rules used")
                                    # print(bool(facts[f].truth_value))
                                    # print(facts[f].rules_used)
                                    # print(facts[f].derivation)
                                    # print("Continued")
                                    # print(facts[facts[f].derivation[0]].derivation)
                                    # print(facts[facts[f].derivation[0]].rules_used)
                                raise ValueError("CONTRADICTION")
                            else:
                                return
                        if(len(empty_terms) > 1):
                            return
                        arg = []
                        for i in range(len(empty_terms)):
                            args = substitute(empty_terms[i], sub[1], new_skolem, skolem_table, skolem_counter)
                            if(args != None):
                                # print("ARGS:", args)
                                arg.append(args)
                            else:
                                return 
                        args = arg[0]
                        new_fact = Fact(args[0], args[1:], False, derivation=[list(current_fact.keys())[0]])
                        free_variables = sum(map(lambda x: is_variable(x) == True, args))
                        # print(args)
                        # print(free_variables)
                        # print("Rule #", rule.index)
                        # print(sub)
                        # if(sub[0][0] != None):
                        #     print(facts[sub[0][0]])
                        #     print(facts[sub[0][0]].rules_used)
                        #     print(facts[sub[0][0]].derivation)
                        #     if (facts[sub[0][0]].derivation != None):
                        #         for fact in facts[sub[0][0]].derivation:
                        #             if(fact != None):
                        #                 print(facts[fact])
                        if(new_fact not in facts.values() and free_variables == 0):
                            # print("VALID FACT")
                            # print("New fact:", fact_counter)
                            facts[fact_counter] = new_fact
                            # print(new_fact)
                            # print(new_fact.derivation)
                            # print("")
                            fact_counter += 1
                            for fact in new_fact.derivation:
                                facts[fact].rules_used.append(rule.index)

def get_variable_count(clauses):
    variable_count = 0
    variables = []
    for clause in clauses:
        for term in clause:
            if(is_variable(term) and term not in variables):
                variable_count += 1
                variables.append(term)
    return variable_count

def derive_falsehoods(facts, rules, fact_counter, rule_order, skolem_table, skolem_counter):
    print("Modus Tollendo Tollens")
    fact_index = len(facts.items())
    fact_count = len(facts.items())
    fact_counter = len(facts.items())
    while(fact_index > 0):
        # print("Current fact", str(fact_index) + "," + str(facts[fact_index]))
        current_fact = {fact_index: facts[fact_index]}
        for index in rule_order:
            rule = rules[index]
            if(rule.then_terms == ["False"]):
                # if len(facts[fact_index].rules_used) != 0:
                #     if index in facts[fact_index].rules_used:
                #         print("Rule found")
                #         continue
                if(bool(facts[fact_index].truth_value)):
                    check_mtp(rule, facts, skolem_table, index, skolem_counter, fact_counter, current_fact)
                    fact_counter = len(facts.items())+1
            else:
                if(not bool(rule.is_then_or)):
                    # print(current_fact)
                    get_false = get_candidate_facts([rule.then_terms], current_fact, skolem_table)
                    # assert len(get_false) == 1
                    false = get_false[0]
                    if(len(false) != 0):
                        falses = [facts[fact[0]] for fact in false if not fact[1].truth_value]
                        if(len(falses) != 0):
                            # print("Rule #", index)
                            # print(false)
                            then_term_variables = get_variable_count([rule.then_terms])
                            if_term_variables = get_variable_count(rule.if_terms)
                            if(then_term_variables == if_term_variables):
                                moves = check_internal_subs(falses[0], rule.then_terms, skolem_table, return_dict=True)
                                # print(moves)
                                new_skolems = []
                                if(len(rule.if_terms) == 1):
                                    # print("SPECIAL CASE")
                                    for clause in rule.if_terms: #every clause is a new fact
                                        args = substitute(clause, moves, new_skolems, skolem_table, skolem_counter)
                                        new_fact = Fact(args[0], args[1:], False, derivation=[list(current_fact.keys())[0]])
                                        free_variables = sum(map(lambda x: is_variable(x) == True, args))
                                        if(new_fact not in facts.values() and free_variables == 0):
                                            # print("VALID FACT")
                                            # print("New fact:", fact_counter)
                                            facts[fact_counter] = new_fact
                                            # print(new_fact)
                                            # print(new_fact.derivation)
                                            # print("")
                                            fact_counter += 1
                                            for fact in new_fact.derivation:
                                                facts[fact].rules_used.append(rule.index)
        fact_index -= 1
        if(fact_count != len(facts.items()) and fact_index == 0):
            # print("End of loop")
            # print_facts(facts)
            fact_index = len(facts.items())
            fact_count = len(facts.items())

#error with immaterial entity facts being fired
def forward_chaining(facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact, cutoff, arity_index):
    fact_count = len(facts.items())
    fact_index = fact_counter-1
    fact_checks = {}
    for index, fact in facts.items():
        fact_checks[index] = False
    current_fact = {fact_counter-1: facts[fact_counter-1]}
    fact_index = fact_counter-1
    start_time = time.time()
    while(fact_index > cutoff):
        fact_count = len(facts.items())
        # print("Current fact #{}:{}".format(fact_index, facts[fact_index]))
        current_fact = {fact_index: facts[fact_index]}
        if(not fact_checks[fact_index]):
            for index in rule_order:
                num_old_facts = len(facts.items())
                rule = rules[index]
                if(not rule.is_then_or and rule.then_terms != ['False']):
                    if(len(rule.if_terms) <= arity_index):
                        unify(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact, current_arity=arity_index)
                        fact_counter = len(facts.items()) + 1
                        skolem_counter = len(skolem_table.items())+1
            if(fact_count != len(facts.items()) and arity_index > 1):
                f = len(facts.items())
                forward_chaining(facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact, fact_count, 1)
                fact_count = len(facts.items())
                if(f != len(facts.items())):
                    fact_count = len(facts.items())
        if(arity_index == 1):
            fact_checks[fact_index] = True
        if(fact_count != len(facts.items()) and arity_index == 1):
            for i, f in facts.items():
                if i not in fact_checks:
                    fact_checks[i] = False
            fact_index = len(facts.items())
        else:
            fact_index -= 1
        if(fact_index == cutoff and arity_index < MAX_ARITY):
            if(fact_index == 0):
                end_time = time.time()
                print("Finished arity {} in {} seconds".format(arity_index, end_time-start_time))
                start_time = time.time()
            # print("MOVE ONTO ARITY", arity_index+1)
            fact_index = len(facts.items())
            for i, f in facts.items():
                fact_checks[i] = False
            arity_index += 1
    # print("GENERATED ALL POSITIVE FACTS")

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


def init(input_file, skolem_table, skolem_counter, rule_file="BFO2020-kowalski-with-identity-rules.txt"):
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
            fact = parse_line(line, skolem_table, skolem_counter)
            skolem_counter = len(skolem_table.items()) + 1
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

def modus_tollens(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact):
    #get valid positions for the rule
    candidate_facts = get_candidate_facts(rule.then_terms, current_fact, skolem_table)
    rule_terms, candidates = get_non_empty(candidate_facts, rule.then_terms)
    if(len(candidates) == 0):
        return
    print(rule)
    print(current_fact)
    print(candidate_facts)
    print(rule_terms)
    print(candidates)
    subs = {}
    for pos in range(len(rule_terms)):
        for candidate in candidates[pos]:
            subs = check_internal_subs(candidate[1], rule_terms[pos], skolem_table, return_dict=True, existing=subs)
            if(subs != False):
                print(subs)
                break
        
    if(subs == False or len(subs.items()) == 0):
        return
    empty = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) == 0]
    non_empty = [i for i in range(len(candidate_facts)) if len(candidate_facts[i]) != 0]
    for j in non_empty:
        then_args = [None for i in range(len(rule.then_terms))]
        then_args[j] = substitute(rule.then_terms[j], subs, [], skolem_table, skolem_counter)
        if(then_args[j] == None):
            return
        then_args[j].append(bool(list(current_fact.values())[0].truth_value))
        for k in empty:
            print(rule.then_terms[k])
            args = substitute(rule.then_terms[k], subs, [], skolem_table, skolem_counter)
            print(args)
            if(args != None):
                temp_fact_true = Fact(args[0], args[1:], True)
                temp_fact_false = Fact(args[0], args[1:], False)
                found_fact = False
                if(temp_fact_true in facts.values()):
                    if(list(facts.values()).index(temp_fact_true) != -1):
                        then_args[k] = args
                        then_args[k].append(True)
                        found_fact = True
                if(temp_fact_false in facts.values()):
                    if(list(facts.values()).index(temp_fact_false) != -1):
                        then_args[k] = args
                        then_args[k].append(False)
                        found_fact = True
            else: #None is return when there isn't enough info
                candidates = get_candidate_facts([rule.then_terms[k]], facts, skolem_table)
                if(len(candidates[0]) == 0):
                    print("No candidates")
                    then_args[k] = None
                else:
                    print(rule.then_terms[k])
                    print("Candidate facts:")
                    for candidate in candidates[0]:
                        print(candidate[1])
                        d = check_internal_subs(candidate[1], rule.then_terms[k], skolem_table, return_dict=True, existing=subs)
                        if(d == subs):
                            continue
                        else:
                            print(d)
                            subs = d
                            then_args[k] = substitute(rule.then_terms[k], subs, [], skolem_table, skolem_counter)
                            print(then_args)
                            then_args[k].append(bool(candidate[1].truth_value))
        if(None in then_args):
            num_none = len([i for i in range(len(then_args)) if then_args[i] == None])
            num_false = len([i for i in range(len(then_args)) if then_args[i] != None and bool(then_args[i][-1]) == False])
            if(num_false == len(rule.then_terms)-1 and num_none == 1):
                print("PASSED CHECK ONE")
                print(then_args)
                #then we apply the same algorithm to the if terms
                if_args = [None for n in range(len(rule.if_terms))]
                saved_copy = copy.deepcopy(subs)
                for i in range(len(rule.if_terms)):
                    arg = substitute(rule.if_terms[i], subs, [], skolem_table, skolem_counter)
                    print("Result of substitution:", arg)
                    if(arg != None):
                        test_fact = Fact(arg[0], arg[1:], True)
                        if(test_fact in facts.items()):
                            then_args[i] = arg
                        else:
                            print("This fact does not exist as true")
                            return
                    else:
                        candidate_facts = get_candidate_facts([rule.if_terms[i]], facts, skolem_table)
                        candidate_facts = candidate_facts[0]
                        if(len(candidate_facts) == 0):
                            return
                        print(candidate_facts)
                        for can in candidate_facts:
                            if(bool(can[1].truth_value) == False): #cannot accept false facts
                                continue
                            print(can[1])
                            d = check_internal_subs(can[1], rule.if_terms[i], skolem_table, return_dict=True, existing=subs)
                            if(d != subs):
                                print("More info gathered")
                                print(d)
                                subs = d
                                arg = substitute(rule.if_terms[i], subs, [], skolem_table, skolem_counter)
                                if(arg != None):
                                    if_args[i] = arg
                            else:
                                continue
                if(None in if_args):
                    print("Cannot conclude anything")
                    return
                else:
                    print(if_args)
                    raise NotImplementedError()

    #fix subs so that they cannot be changed
    
def mtt(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact):
        print("Rule #", rule.index)
        print(current_fact)
        candidate_facts = get_candidate_facts(rule.then_terms, current_fact, skolem_table)
        rule_terms, candidates = get_non_empty(candidate_facts, rule.then_terms)
        if(len(candidates) != 0):
            candidate_all_facts = get_candidate_facts(rule.then_terms, facts, skolem_table)
            print(candidate_all_facts)
            
            non_empty = [i for i in range(len(candidate_all_facts)) if len(candidate_all_facts[i]) != 0]
            subs = []
            count = 0
            print(non_empty)
            for entry in non_empty:
                print(candidate_all_facts[entry])
                for can in candidate_all_facts[entry]:
                    substitutions = check_internal_subs(can[1], rule.then_terms[entry], skolem_table, return_dict=True)
                    if(substitutions != False):
                        print(substitutions)
                        break
            # assert count == 1 or count == 0
            check_combinations(substitutions, candidate_all_facts, rule_terms, rule.then_terms, subs, facts, non_empty, skolem_table)
            if(len(subs) > 0):
                for sub in subs:
                    print(sub)
                    key = list(current_fact.keys())[0]
                    if(key not in sub[0]):
                        continue
                    num_false = get_num_false(facts, sub[0])
                    if(num_false != len(rule.then_terms)-1):
                        continue
                    #then we need to double check that the if statements are true
                    print("Candidate if facts")
                    candidate_if_facts = get_candidate_facts(rule.if_terms, facts, skolem_table)
                    print(candidate_if_facts)
                    if [] not in candidate_if_facts:
                        s2 = []
                        fact_part = list(current_fact.values())[0]
                        non_empty = [i for i in range(len(candidate_if_facts)) if len(candidate_if_facts[i]) != 0]
                        print(non_empty)
                        print(fact_part)
                        #there's a case of ambiguity here
                        check_combinations(sub[1], candidate_if_facts, rule.if_terms, rule.if_terms, s2, facts, non_empty, skolem_table)
                        if(len(s2) > 0):
                            for s in s2:
                                num_false = get_num_false(facts, sub[0])
                                if(num_false == len(rule.then_terms)):
                                    print("Rule #", rule.index)
                                    print(s[0])
                                    print(rule.then_terms)
                                    raise ValueError("Contradiction")
                                num_false = get_num_false(facts, s[0])
                                if(num_false == 0 and None not in s[0]):
                                    print("Rule #", rule.index)
                                    print(s)
                                    print("VALID fact")
                                    t = get_empty(candidate_facts, rule.then_terms)
                                    print(t)
                                    if(t == []):
                                        print("Cannot conclude anything")
                                        return
                                    args = substitute(t[0], sub[1], [], skolem_table, skolem_counter)
                                    new_fact = Fact(args[0], args[1:], True)
                                    if new_fact not in facts.items():
                                        new_fact.derivation = sub[0]
                                        for fact in s[0]:
                                            if fact != None and fact not in new_fact.derivation:
                                                new_fact.derivation.append(fact)
                                        facts[fact_counter] = new_fact
                                        # print(new_fact.derivation)
                                        # print("")
                                        # if(fact_counter == 1764):
                                        #     raise NotImplementedError()
                                        facts[fact_counter].rules_from.append(rule.index)
                                        fact_counter += 1
                                        # for fact in new_fact.derivation:
                                        #     facts[fact].rules_used.append(rule.index)
                                        # print(facts[fact].derivation)
                                        # print("RETURN")
                                        return



def derive_then_ors(facts, rules, fact_counter, rule_order, skolem_table, skolem_counter):
    # print('DERIVE_THEN_ORS')
    # print_facts(facts)
    fact_count = len(facts.items())
    fact_counter = len(facts.items()) + 1
    fact_index = fact_counter-1
    current_fact = {fact_counter-1: facts[fact_counter-1]}
    while(fact_index > 0):
        fact_count = len(facts.items())
        print("Fact #{}: {}".format(fact_index, facts[fact_index].name))
        current_fact = {fact_index: facts[fact_index]}
        # print(current_fact)
        for index in rule_order:
            num_old_facts = len(facts.items())
            rule = rules[index]
            if(bool(rule.is_then_or)):
                if(len(rule.if_terms)):
                    modus_tollens(facts, current_fact, rule, fact_counter, skolem_table, skolem_counter, skolems_per_fact)
                    fact_counter = len(facts.items()) + 1
                    skolem_counter = len(skolem_table.items())+1
        fact_index -= 1

if __name__ =="__main__":
    input_file = "mytest-input.txt"
    skolem_table = {}
    skolem_counter = 1
    rules, start_facts, fact_counter, skolem_list = init(input_file, skolem_table, skolem_counter)
    rule_order = organize_rules(rules)
    fact_count = len(start_facts.items())
    skolems_per_fact = {}
    initial_facts = len(start_facts.items())
    print("Forward chaining")
    start_time = time.time()
    forward_chaining(start_facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact, 0, 1)
    skolem_counter = len(skolem_table.items()) + 1
    end_time = time.time()
    true_cutoff = len(start_facts.items())
    print("Finished forward chaining in {} seconds".format(end_time-start_time))
    # start_time = time.time()
    # derive_falsehoods(start_facts, rules, fact_counter, rule_order, skolem_table, skolem_counter)
    # skolem_counter = len(skolem_table.items()) + 1
    # end_time = time.time()
    # print("Finished deriving falsehoods in {} seconds".format(end_time-start_time))
    # start_time = time.time()
    # derive_then_ors(start_facts, rules, fact_counter, rule_order, skolem_table, skolem_counter)
    # end_time = time.time()
    # print("Finished deriving then ors in {} seconds".format(end_time-start_time))
    # skolem_counter = len(skolem_table.items()) + 1
    write_facts_to_csv("./output_final.csv", start_facts)
    # while(len(start_facts.items()) - initial_facts > 0):
    #     initial_facts = len(start_facts.items())
    #     print("Forward chaining")
    #     start_time = time.time()
    #     forward_chaining(start_facts, rules, fact_counter, rule_order, skolem_counter, skolem_table, skolems_per_fact, true_cutoff, 1)
    #     true_cutoff = len(start_facts.items())
    #     skolem_counter = len(skolem_table.items()) + 1
    #     end_time = time.time()
    #     print("Finished forward chaining in {} seconds".format(end_time-start_time))
    #     start_time = time.time()
    #     derive_falsehoods(start_facts, rules, fact_counter, rule_order, skolem_table, skolem_counter)
    #     skolem_counter = len(skolem_table.items()) + 1
    #     end_time = time.time()
    #     print("Finished deriving falsehoods in {} seconds".format(end_time-start_time))
    #     start_time = time.time()
    #     derive_then_ors(start_facts, rules, fact_counter, rule_order, skolem_table, skolem_counter)
    #     end_time = time.time()
    #     print("Finished deriving then ors in {} seconds".format(end_time-start_time))
    #     skolem_counter = len(skolem_table.items()) + 1
    #     write_facts_to_csv("./output_final.csv", start_facts)
    #     break
    for key, value in skolem_table.items():
        print(key, skolem_table[key])
    # print_facts(start_facts)