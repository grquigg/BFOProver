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
