import hashlib
import math


class GenericHashFunctionsSHA512:

    def __init__(self, k=1024, nhash=2):
        # the underlying hash function to be used. Just one in this class
        # the sha result is split in a way the subsets are used for
        # all the hash functions
        self.hash = hashlib.sha512

        # the number of hashes
        self.nhash = nhash
        # the size of each bit index
        self.bitidx_size = int(math.log2(k))
        # keep the last hash element and its value to avoid hash recalculation
        self.lastelement = str(42)
        self.lasthash = bin(int(self.hash(self.lastelement.encode()).hexdigest(), 16))[2:].zfill(512)

        # sha512 hash provides 512 bits. With those bits we have to build:
        #   * The nhash functions (g) to select the bits to be set/retrieved
        assert 512 >= (nhash * self.bitidx_size)
        return

    # Retrieves the bit index using the nth hash for the element
    def getbit_idx(self, element_int, n):
        # Turn element into a string
        element = str(element_int)
        if self.lastelement != element:
            # Calculate the sha512 hash for the element and use
            # its hex representation
            hexval = self.hash(element.encode()).hexdigest()
            # Assign this element as the active element
            self.lastelement = element
            # Converting into binary adding 0s at the beginning to avoid losing
            # the first values when they are 0
            # Cache the hashed value
            self.lasthash = bin(int(hexval, 16))[2:].zfill(512)

        # Calculate the bit index selecting the start position by skipping
        # the previous n-1 bit indices
        start = self.bitidx_size * n
        # the bit index includes bitidx_size bits from the hash
        bitidx = int(self.lasthash[start:start + self.bitidx_size], 2)
        return bitidx

