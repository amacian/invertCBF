# On the Privacy of Counting Bloom Filters

This repository includes the implementation in Python of an algorithm to retrieve the content of Counting Bloom Filters 
for the paper:

P. Reviriego, A. Sánchez-Macián, S. Walzer, E. Merino-Gómez, S. Liu and F. Lombardi , "On the Privacy of Counting Bloom Filters", 
IEEE Transactions on Dependable and Secure Computing (in press)

## Dependencies
- Python > 3.9
- hashlib, random, string, getopt and math libraries
- For the [wordlex](http://www.lexique.org/?page_id=250) use cases, the [German](http://worldlex.lexique.org/files/De.Freq.2.rar) and [English](http://worldlex.lexique.org/files/Eng_US.Freq.2.rar) datasets.

## Content

this directory contains:

- runCBF.bat and runCBFdetail.bat scripts to retrieve the information used in some of the experiments of the paper and identify parameters.
- runUseCases.bat script to retrieve the information used in the paper to collect the results for the WordLex dataset use cases.
- expectedRecovered.sage script on sagemath (developed by S. Walzer) that reproduces the curves corresponding to the expected fraction of recovered elements
- this README file.
- the LICENSE file.

*src* directory contains:
- GenericHashFunctionsMD5.py (Generates the hash for the functions that select the counter positions using MD5).
- GenericHashFunctionsSHA512.py (Generates the hash for the functions that select the counter positions using SHA512).
- LogScreen and LogFile (To log the different messages generated during the execution).
- CountingBloomFilter.py (Implementation of the Counting Bloom Filter).
- tester.py (main script to generate the results of the experiments).

## Execution of the code

- Run the script runCBF.bat and retrieve the output from the logs directory.
- Do the same for the runCBFdetail.bat and process both files.
- Configure the "data" directory in the runUseCases.bat script and execute it to retrieve the information for the German and English datasets.

If different parameters are required, just run:

    python src/tester.py -m <size> -n <insertions> -u <universe_size> -s <step_size> -k <nhashes> -a <hash> '
              '-i <iterations>

E.g.

    python src/tester.py -m 65536 -n 10000 -u 240000 -s 30000 -k 5 -a md5 -i 500
