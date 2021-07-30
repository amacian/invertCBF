import hashlib
import math
import random
import string
from typing import List

from LogScreen import LogScreen
from GenericHashFunctionsMD5 import GenericHashFunctionsMD5


# Adaptive bloom filter
class CountingBloomFilter:
    bloom_structure: list[int]

    def __init__(self, m=65536, nhash=5, hash_f=None):
        # number of counters
        self.m = m
        # the structure is stored as a flattened array
        self.bloom_structure = [0] * m
        # the hash class used to generate the functions
        if hash_f is None:
            self.hash = GenericHashFunctionsMD5(m, nhash)
        else:
            self.hash = hash_f
        # the number of hashes per group, apart from the word hash function
        self.nhash = nhash

    # clear the list of counters
    def clear(self):
        self.bloom_structure = [0] * len(self.bloom_structure)

    # Change the hash object that generates the function
    def set_hash(self, hash_object):
        if hash_object is not None:
            self.hash = hash_object
        return

    # Get the hash object that generates the function
    def get_hash(self):
        return self.hash

    # method to add an element into the filter
    def add(self, data):
        # extract a position from each hash to set the bit in the selected word
        for i in range(self.nhash):
            # position for the ith hash of the group_i function 
            # the final position in the array is a combination
            # of word index and bit index
            idx = self.hash.getbit_idx(data, i)
            # idx = int(bitidx)

            # set the appropriate bit
            self.bloom_structure[idx] += 1

        return

    # method to delete an element from the filter
    def remove(self, data):
        # extract a position from each hash to set the bit in the selected word
        for i in range(self.nhash):
            # position for the ith hash of the group_i function 
            # the final position in the array is a combination
            # of word index and bit index
            idx = self.hash.getbit_idx(data, i)
            # idx = int(bitidx)

            # set the appropriate bit
            self.bloom_structure[idx] -= 1

        return

    # check the bloom filter for the specified data
    def check(self, data, threshold=1):
        # extract a position from each hash to get the bit from the selected word
        for i in range(self.nhash):
            # position for the ith hash of the group_i function
            # the final position in the array is a combination
            # of word index and bit index
            idx = self.hash.getbit_idx(data, i)

            # check if the bit is at least the threshold for the specified word
            # if not, the data is a negative
            if self.bloom_structure[idx] < threshold:
                return False
        return True

    # Retrieve the value of a counter
    def get_counter(self, position):
        if len(self.bloom_structure) < position:
            return 0
        return self.bloom_structure[position]

    # Retrieve the structure of counters
    def get_counters(self):
        return self.bloom_structure

    # Debug function for printing content
    def printme(self):
        sc = LogScreen()
        for i in range(self.m):
            info = "Row=%d, count=%d" % (i, self.bloom_structure[i])
            sc.write(info)
        return
