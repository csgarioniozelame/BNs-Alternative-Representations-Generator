# Program adapted by Kai Liang (2018) from Igor Bobeldijk (2016)
# 
# Open in terminal: 'python BNexpander.py [network-name].net'

import argparse
import os
from re import findall
from itertools import permutations, chain
from decimal import *

getcontext().prec = 100 # set the value of precision to 100 (if applicable)
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
        for index, item in enumerate(data): # convert all input probabilites to Decimals
			#print 'this is index', index  #i.e. 0,1,2,3...
			data[index] = Decimal(str(item))
			#print 'this is data[index]', data[index]  #i.e. probability
        potential[ID] = data
        #print 'potential is :',potential[ID]
    if line =="":
        #print "EOF"
        break



# isclose : checks if two Decimals are practically the same
# this function is not used anymore with the use of Decimals
# because of more accurate precisions
def isclose(a, b, rel_tol=Decimal(str(1e-09)), abs_tol=Decimal(str(0.0))):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# num : turns a string into a Decimal
def num(s):
    try:
        return Decimal(str(s))
    except ValueError:
        print 'string conversion error!'

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
    #print 'this is V', V  #i.e. ['B', 'E', 'A']
    pTable = makeTable(V)
    pTable[0].append("Probability")
    for r, row in enumerate(pTable[1:]):
		row.append(num(potential[v][r]))
		#print 'row is',row
    #print 'this is pTable', pTable
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
        p = Decimal(1)
        for i, val in enumerate(row):    
            values = []
            for parent in relations[V[i]]:
                values.append(row[V.index(parent)])
                #print 'values.append is', row[V.index(parent)]  #i.e. 0,1
            values.append(val)
            #print 'val is',val  #i.e. 0,1
            #print 'values is', values  #i.e. [0,0]

            for r in Theta[V[i]]:
                #print 'r[] is', r[:len(r)-1]  #i.e. [0,0]
                if values == r[:len(r)-1]:
                    p *= Decimal(str(r[len(r)-1]))
                    #print 'this is p:', p
                    #print 'this is r:', r[len(r)-1]  #i.e. 0.001
        row.append(p)
        #print 'this is p',p  #i.e. probability
        #print 'this is JPD', JPD
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
        #print 'this is Theta[',v,']:',Theta[v]
    
    #for v in G:
    #    G[v].sort()

    return G, Theta

def removeIndependencies(G,var,pTable):
    print 'before',pTable
    for v in G[var]:
        p1 = zip(*sliceTable(pTable, v, 0)[1:])[-1]
        p2 = zip(*sliceTable(pTable, v, 1)[1:])[-1]
        #print 'this is p1[',v,']:', p1
        #print 'this is p2[',v,']:', p2
        indep = True
        for i in range(len(p1)):
            if Decimal(p1[i]) == Decimal(p2[i]):
				print G[var]
				print 'this is p1[i] and p2[i]:', p1[i], p2[i], v
				print 'they are the same'
            if not Decimal(p1[i]) == Decimal(p2[i]): #isclose(p1[i],p2[i]):
                if Decimal(p1[i]) == Decimal(-1) or Decimal(p2[i]) == Decimal(-1): # turn into Decimal value comparisons
                    break
                indep = False
                break
        
        print 'indep is', indep
        if indep:
            G[var].remove(v)
            print v, 'is removed from', G[var]
            pTable = sliceTable(pTable, v, 0)
            i = pTable[0].index(v)
            for r in pTable:
                del r[i]              # remove column from table
    
    print 'after',pTable            
    return pTable


def findCP(jpd, vars, vals):
    table = jpd
    pSum = Decimal(1) # sum of probability column

    for i,v in enumerate(vars):
        lastSum = pSum
        table = sliceTable(table, v, vals[i])
        #print 'this is table', table
        pSum = Decimal(str(sum(zip(*table[1:])[-1])))
        #print 'this is pSum', pSum
	#print 'this is lastSum', lastSum
    if lastSum == Decimal(0):
        return Decimal(-1) # undefined
    else:
        return pSum / lastSum

def sliceTable(pTable, var, val):   # returns sliced JPD given variable instance i.e. (jpd, 'A', 1)
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
    print file_name
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
        
