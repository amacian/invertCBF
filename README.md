# On the Privacy of Counting Bloom Filters

This repository includes the implementation in Python of an algorithm to retrieve the content of Counting Bloom Filters 
for the paper:

P. Reviriego, A. Sánchez-Macián, S. Walzer, E. Merino and O. Rottenstreich, "On the Privacy of Counting Bloom Filters", 
under submission to IEEE ...

## Dependencies
- Python > 3.9
- hashlib, random, string, getopt and math libraries

## Content

this directory contains:

- runCBF.bat and runCBFdetail.bat scripts to retrieve the information used in the paper
- this README file.
- the LICENSE file.

*src* directory contains:
- GenericHashFunctionsMD5.py (Generates the hash function to select the word and the groups of hash functions to select the bits using MD5)
- GenericHashFunctionsSHA512.py (Generates the hash function to select the word and the groups of hash functions to select the bits using SHA512)
- LogScreen and LogFile (To log the different messages generated during the execution).
- CountingBloomFilter.py (Implementation of the Counting Bloom Filter).
- tester.py (main script to generate the results of the experiments)

## Execution of the code

- Run the script runCBF.bat and retrieve the output from the logs directory.
- Do the same for the runCBFdetail.bat and process both files.

If different parameters are required, just run:

    python src/tester.py -m <size> -n <insertions> -u <universe_size> -s <step_size> -k <nhashes> -a <hash> '
              '-i <iterations>

E.g.

    python src/tester.py -m 65536 -n 10000 -u 240000 -s 30000 -k 5 -a md5 -i 500