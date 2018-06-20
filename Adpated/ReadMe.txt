Running Instructions:

The four Bayesian Networks were created in SamIam (version 3.0) and are of the .net format v5.7 of Hugin.

The alternative representations that were found for each of the four example networks are found in the 'output Network-X pre-Y' folders. 

X is the number of the input network, and Y is the precision places used. 

The naming convention for the found networks is:

[arrow_count]_[permutation].net

To run the algorithm (only works for Python 2):

python BNexpander.py Network-X.net

Then you need to set the precision places you want to use: this should be an integer and as large as you need.

This will create a new folder with the same root as BNexpander.py and fill it with all alternative representations.