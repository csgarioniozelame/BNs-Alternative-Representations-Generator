from decimal import *


def isclose(a, b, rel_tol=Decimal(str(1e-09)), abs_tol=Decimal(str(0.0))):
    print abs(a-b),  max(rel_tol * max(abs(a), abs(b)), abs_tol)
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    

getcontext().prec = 100

a = 1

b = 0.7

seven = 7

sev = Decimal(7)

one = Decimal(1)

on = Decimal (1)

h = Decimal(str(1))

f = Decimal(1)

c = Decimal(str(0.7))


result1 = one + seven
result2 = one + sev

if Decimal(str(b)) == c:
	print 'Yes'

if Decimal(str(b)) == c:
	print 'o1 == o2'
	
if a == one:
	print 'a == one'

if a == h:
	print 'a == h'
print result1,'\n',result2

if not isclose(a, b):
	print "hi!"
	
if not isclose(a, on):
	print "hi there"
