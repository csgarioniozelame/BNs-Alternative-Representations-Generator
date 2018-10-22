# An automatic generator of alternative representations of Bayesian Networks (BN)

## About
- This repository contains codes for a completed bachelor project, they are used to 
    generate all possible alternative Bayesian networks (BN) given an input BN.
- The example input networks were created in SamIam and are of the .net format v5.7 of Hugin. 
    These can also be opened and saved with Genie. They can be found in dir/Adapted.

## Compile
- To run the program, first go to dir/Adapted.
- Use command python BNexpander.py Network-X.net (where Network-x.net is the input BN).
- Then type in your desired precision of calculation (can be infinitely large).
- The program will return with all the alternative representations of the input BN in a folder
    output Network-X prec-X.
- The naming of the alternative representation is: [arrow_count]_[permutation].net


## Copyright
- They cannot be used, copied, spread without permission.
- Copyright belongs to Kai Liang (kai.liang@student.uva.nl).
