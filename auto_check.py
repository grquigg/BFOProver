import csv
def compareOutput(file1, file2):
    factlist1 = []
    factlist2 = []
    fact_map = []
    with open(file1, newline="\n") as f1:
        r = csv.reader(f1, delimiter=",")
        for row in r:
            factlist1.append(row[1:6])
    with open(file2, newline="\n") as f2:
        reader = csv.reader(f2, delimiter=',')
        for row in reader:
            fact = row[1:6]
            fact[0] = fact[0].upper()
            if fact in factlist1:
                if fact in factlist2:
                    print("Duplicate")
                    continue
                factlist2.append(fact)
                index = factlist1.index(fact)
                entry = (row[0], index+1)
                fact_map.append(entry)
                print("Fact #{}: CHECK".format(row[0]))
            else:
                print("Fact #{}: FAIL".format(row[0]))
    print(len(factlist2))
    return fact_map

if __name__ == '__main__':
    file1 = "CLIFreasoner-table2.csv"
    file2 = "output_final.csv"
    fact_map = compareOutput(file1, file2)
    sorted_fact_map = sorted(fact_map, key=lambda x: x[1])
    facts_in_sort = [False for i in range(3439)]
    for f in sorted_fact_map:
        if not facts_in_sort[f[1]]:
            facts_in_sort[f[1]] = True
    for j in range(len(facts_in_sort)):
        if not facts_in_sort[j]:
            print("Fact #{} not in data".format(j))