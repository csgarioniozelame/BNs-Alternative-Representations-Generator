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
        #print len(potential[ID])
        for index1 in range(len(potential[ID])):
			for index2 in range(index1, len(potential[ID]),2):
				if (potential[ID][index1] == potential[ID][index2]) & (index1 != index2):
					print potential[ID][index1], 'has occured more than once in', ID, 'in file', args.filename
    if line =="":
        #print "EOF"
        break
