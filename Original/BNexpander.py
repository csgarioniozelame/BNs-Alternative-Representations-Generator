# Program by Igor Bobeldijk (2016)
# 
# Open in terminal: 'python BNexpander.py [network-name].net'

import argparse
import os
from re import findall
from itertools import permutations, chain

argumentParser = argparse.ArgumentParser(description='Process BN file.')
argumentParser.add_argument('filename', metavar='filename.net', help='a BN file')
args = argumentParser.parse_args()
f = open(args.filename)

# the following dictionaries are filled with data from the .net file
variables = {}
relations = {}
potential = {}
labels = {}
positions = {}
network_parameters = ""

while True:
    line = f.readline()
    if "net" in line:
        # net are parameters ignored for now
        while "}" not in line:
            line = f.readline()
            network_parameters += line
    if "node" in line:
        states = []
        ID = findall(r'node ([A-Za-z\t .]+)', line)[0]
        label = ""
        position = ()
        while "}" not in line:
            if "states" in line:
                states = findall('"([^"]+)"', line)
            if "label" in line:
                label = findall('"([^"]+)"', line)[0]
            if "position" in line:
                position = findall('\d+\.\d+|\d+', line)
            line = f.readline()
        variables[ID] = states # add new variable
        labels[ID] = label
        positions[ID] = position
    if "potential" in line:
        #print "found potential"
        re_list = findall('\w+', line)
        ID = re_list[1]
        parents = findall('\w+', line)[2:]
        relations[ID] = parents # add new relationship
        data = []
        while "}" not in line:
            line = f.readline()
            data += findall('\d+\.\d+|\d+', line)
        potential[ID] = data 
    if line =="":
        #print "EOF"
        break



# isclose : checks if two floats are practiacally the same
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# num : turns a string into a number
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

# makeTable returns a matrix given a list of variable names
# row[0] = Var1, Var2, ..
# row[1:] = val1, val2, ..
def makeTable(V):
    pTable = []
    tableLength = 1
    lastLength = 1

    for v in V:
        length = len(variables[v])
        tableLength *= length
    
    for v in reversed(V):
        column = [v]
        currentLength = len(variables[v])
        for i in range(tableLength):
            column.append( i / lastLength % currentLength )
        lastLength *= currentLength
        pTable.append(column)

    return [list(a) for a in zip(*pTable[::-1])] # rotated list 

# makeCPT combines the potentials and relations in the network to create a CPT for a variable V
# returns a table with the following columns: (parent1,..,parentN,V,probability)
def makeCPT(v):
    V = relations[v] + [v]
    pTable = makeTable(V)
    pTable[0].append("Probability")
    for r, row in enumerate(pTable[1:]):
        row.append(num(potential[v][r]))
    return pTable

# makeJPD creates the full Joint Probability Table from the CPTs
def makeJPD():
    V = list(variables.keys())
    JPD = makeTable(V)
    Theta = {}                  # set of CPTs, one for each variable
    for v in V:
        Theta[v] = makeCPT(v)

    JPD[0].append("Probability")
    for r, row in enumerate(JPD[1:]):
        p = 1
        for i, val in enumerate(row):    
            values = []
            for parent in relations[V[i]]:
                values.append(row[V.index(parent)])
            values.append(val)

            for r in Theta[V[i]]:
                if values == r[:len(r)-1]:
                    p *= r[len(r)-1]
        row.append(round(p,8))
    return JPD

# generateBN will generate a Theta and G from the jpd given a sequence
def generateBN(jpd, sequence):
    Theta = {}                  # set of CPTs, one for each variable
    G = {}                      # set of parents for each variable
    
    last = []       
    for v in sequence:          # initize G with all possible parent connections
        G[v] = list(last)
        last.append(v)

    for v in sequence:          # for each variable in s generate the CPT and add it to Theta
        V = G[v] + [v]
        pTable = makeTable(V)

        pTable[0].append("Probability")
        for row in pTable[1:]:
            row.append(findCP(jpd, V,row))
        
        pTable = removeIndependencies(G,v,pTable)       # remove independencies from G
        Theta[v] = pTable
    
    #for v in G:
    #    G[v].sort()

    return G, Theta

def removeIndependencies(G,var,pTable):
    for v in G[var]:
        p1 = zip(*sliceTable(pTable, v, 0)[1:])[-1]
        p2 = zip(*sliceTable(pTable, v, 1)[1:])[-1]
        indep = True
        for i in range(len(p1)):
            if not isclose(p1[i],p2[i]):
                if p1[i] == -1 or p2[i] == -1:
                    break
                indep = False
                break
        
        if indep:
            G[var].remove(v)
            pTable = sliceTable(pTable, v, 0)
            i = pTable[0].index(v)
            for r in pTable:
                del r[i]              # remove column from table
                
    return pTable


def findCP(jpd, vars, vals):
    table = jpd
    pSum = 1 # sum of probability column

    for i,v in enumerate(vars):
        lastSum = pSum
        table = sliceTable(table, v, vals[i])
        pSum = sum(zip(*table[1:])[-1])

    if lastSum == 0:
        return -1 # undefined
    else:
        return pSum / lastSum

def sliceTable(pTable, var, val):   #returns sliced JPD given variable instance i.e. (jpd, 'A', 1)
    i = pTable[0].index(var)
    newTable = []
    newTable.append(pTable[0])
    for row in pTable[1:]:
        if row[i] == val:
            newTable.append(row)
    return newTable

def saveNetwork(G, Theta, permutation):
    
    a = 0                   # arrow_count
    for v in G:
        a += len(G[v])
    
    file_name = str(a) + '_' + ''.join(permutation) + '.net'
    folder = 'networks for ' + str(variables.keys())
    directory = os.path.join(os.path.dirname(__file__),folder)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, file_name)
    bn_file = open(path,'w')
    bn_file.write('net\n')
    bn_file.write(network_parameters)
    bn_file.write('\n')

    for v in variables:
        bn_file.write('node {}\n'.format(v))
        bn_file.write('{\n')
        bn_file.write('\tstates = ("{}");\n'.format('" "'.join(variables[str(v)])))
        bn_file.write('\tID = "{}";\n'.format(v))
        bn_file.write('\tposition = ({0} {1});\n'.format(positions[v][0],positions[v][1]))
        bn_file.write('\tlabel = "{}";\n'.format(labels[v]))
        bn_file.write('}\n\n')

    for v in variables:
        bn_file.write('potential ( {0} | {1} )\n'.format(v,' '.join(G[v])))
        bn_file.write('{\n')
        bn_file.write('\tdata = ')
        
        data = zip(*Theta[v][1:])[-1]
        while len(data) > 2:
            new_data = []
            for i in range(0, len(data),2):
                new_data.append((data[i], data[i+1]))
            data = new_data

        bn_file.write(str(tuple(data)).replace(',', ''))
        bn_file.write(';\n}\n\n')
    bn_file.close

print "relations:", relations
print "potential:", potential
print "variables:", variables

jpd = makeJPD()

for l in jpd:
    print l

graphs = {}
CPTs = {}
for p in permutations(variables.keys(), len(variables.keys())):
    G, Theta = generateBN(jpd, p)
    duplicate = False
    for g in graphs.values():
        for v in g:
            if sorted(g[v]) == sorted(G[v]):
                duplicate = True
            else:
                duplicate = False
                break
        if duplicate:
            break
    if not duplicate:
        graphs[p] = G
        CPTs[p] = Theta

for p in graphs:
   saveNetwork(graphs[p], CPTs[p], p)
        
