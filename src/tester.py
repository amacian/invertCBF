import random
import sys
import getopt
from CountingBloomFilter import CountingBloomFilter
from LogScreen import LogScreen
from LogFile import LogFile
from GenericHashFunctionsSHA512 import GenericHashFunctionsSHA512


# Function to generate the random set of elements.
# Current version uses strings
# num is the number of elements to generate
# if a CountingBloomFilter cbf is passed, elements are stored there
# if a list ds is passed, elements are stored there
# exclude set are a elements that should not be selected
# maxVal is the maximum int value
def generate_random_elements(num, cbf=None, ds=None, max_val=1000000000, exclude=None):
    # Elements are added to the set to check for repetitions
    if exclude is None:
        exclude = set()
    s = set()
    s.clear()

    # Keeps data of stored elements
    stored = 0
    # Generate elements until the value "stored" is reached
    while stored < num:
        # Generate integers between 1 and 1 billion 
        entry = random.randint(1, max_val)
        # if entry was already selected or is in the exclude set,
        # go to next iteration
        if entry in s or entry in exclude:
            continue
        # When an CountingBloomFilter is received
        if cbf is not None:
            # Add the entry to the filter
            cbf.add(entry)
        # When a list is received
        if ds is not None:
            # Add the element to the list
            ds.append(entry)
        # Another element has been stored
        stored = stored + 1
        # Add it to the set so they are not repeated
        s.add(entry)

    return


# Main method
def main():
    # Default values for
    # Number of counters in the filter
    m = 65536
    # Number of correct insertions to be done into the filter
    n = 10000
    # Size of the universe of elements
    u = 240000
    # Step to increase the universe size
    # Try u, then u+step, u+2*step...
    step = 30000
    # bit width per word
    k = 5
    # Hash function to be used (md5 by default)
    hash_f = 'md5'
    # Number of iterations
    it = 10

    # Retrieve the option values from command line
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:n:u:s:k:a:i:")
    except getopt.GetoptError:
        print('argv[0] -m <size> -n <insertions> -u <universe_size> -s <step_size> -k <nhashes> -a <hash> '
              '-i <iterations>')
        sys.exit(2)

    for opt, arg in opts:
        # Help option. Print help and leave.
        if opt == '-h':
            print(
                'argv[0] -m <size> -n <insertions> -u <universe_size> -s <step_size> -k <nhashes> -a <hash> '
                '-i <iterations>')
            sys.exit()
        # -m option for setting the number of counters in the filter
        elif opt == "-m":
            m = int(arg)
        # -n option for setting the number of correct elements that will be inserted into the filter
        elif opt == "-n":
            n = int(arg)
        # -u option for setting the size of the universe
        elif opt == "-u":
            u = int(arg)
        # -s option for setting the step to increase the size
        elif opt == "-s":
            step = int(arg)
            # -k option to set the number of hash elements to select the bits to be set
        elif opt == "-k":
            k = int(arg)
        # -a option to change the default md5 hash to other ("sha512" supported)
        elif opt == "-a":
            hash_f = arg
        # -i option to change the number of iterations
        elif opt == "-i":
            it = int(arg)

    # Pass the parameters to the run function
    run(m, n, u, step, it, k, hash_f)
    return


# Get the set of elements from the Universe (1 to maxVal) that may be included into the filter.
# m is the number of positions (counters) of the CBF
# k is the number of hash functions
# cbf is the Counting Bloom Filter
# p is the P array with all the elements from the universe that returned positive from CBF
# sc is the printing element (LogScreen o LogFile) to print information
def peeling(m, k, cbf, p, sc):
    # Retrieve the hash function used
    hashf = cbf.get_hash()
    # T array  with m positions to store the elements that are mapped to them
    elements = [None] * m
    # Count of elements mapped to each position
    count = [0] * m

    # For all the positions in p
    for i in range(len(p)):
        # for the k hash functions
        for j in range(k):
            # Get the position mapped for the element p[i] and the jth hash function
            pos = hashf.getbit_idx(p[i], j)
            # Retrieve the position pos of the T array            
            list_pos = elements[pos]
            # If no elements are assigned to that position, create a list and assign it
            if list_pos is None:
                list_pos = list()
                elements[pos] = list_pos
            # Include the element into the list of elements mapped to the position
            list_pos.append(p[i])
            # Increase the count of elements mapped to the position
            count[pos] += 1

    # Set that will store the positives that were extracted from the filter
    positives = set()
    # Values for the CBF counters
    counters = cbf.get_counters()

    while True:
        # If we found an element that could be extracted in this iteration
        found = False
        # Go through the m positions
        # TODO: exclude positions that were 0 in the previous iterations to speed up the process
        for i in range(m):
            # when the ith position does not have values, go to next position
            if count[i] == 0:
                continue
            # the position has values => it is not empty
            # we only want those positions where we have the same number of elements in T and CBF
            if count[i] != counters[i]:
                continue
            # we found at least one position
            found = True
            # add the elements of the ith position to the positives
            positives.update(elements[i])
            # all these elements must be removed as well, but not from elements
            removers = elements[i].copy()
            # call the function that clears the removers and related false positives
            # pass True as last parameter as they are real positives
            clear_positions(elements, removers, counters, count, hashf, k, sc, True)
        # if no new positives were found in the iteration, we should finish the algorithm
        if not found:
            break

    # return elements that were retrieved from the CBF
    return positives


# Function that clears the element from its positions in T and also clears all the related false positives
# elements is the T array
# positives is the list of elements to be removed
# count_cbf is the list of counters from the CBF
# count is the list of counters from T
# hashf is the hash function used in the CBF
# k is the number of positions
# sc is the printing element (LogScreen o LogFile) to print information
# is_positive indicates if it is a real positive (true) or a false positive (false)
def clear_positions(elements, positives, count_cbf, count, hashf, k, sc, is_positive):
    # Additional elements to be removed
    additional = list()
    # and iterate over them
    num = len(positives)

    # Traverse the positives list
    for i in range(num):
        # get next element to be removed
        next_positive = positives[i]
        # for the k hash functions
        for j in range(k):
            # Get the position mapped for the element and the jth hash function
            jpos = hashf.getbit_idx(next_positive, j)
            # Element might have been removed in a different level of recursion
            if elements[jpos].count(next_positive) == 0:
                break
            # Remove the element from the position
            elements[jpos].remove(next_positive)
            # Reduce the T counter for that position
            count[jpos] -= 1
            # Reduce the CBF counter only when it is a real positive
            if is_positive:
                count_cbf[jpos] -= 1
            # If no more elements are mapped to this position in the CBF
            # we can remove all the pending elements from T and they are false positives
            if count_cbf[jpos] == 0 and count[jpos] != 0:
                # Add those elements to additional list
                additional.extend(elements[jpos])

    # Recursive call to remove the false positive elements
    if len(additional) > 0:
        # Pass False as last parameter as they are false positives
        clear_positions(elements, additional, count_cbf, count, hashf, k, sc, False)

    return


# Function to find all elements from the universe that returns a positive from CBF
# cbf is the Counting Bloom Filter
# max_val is the maximum integer value. Universe will include elements from 1 to max_val

def find_p(cbf, max_val):
    # Create the list P of (true and false) positive elements
    p = list()
    # Check all elements of the universe, from 1 to max_val
    for i in range(max_val):
        # If one of the positions is 0, then it is a negative
        # Otherwise, add it to P
        if cbf.check(i, 1):
            p.append(i)

    return p


# Run the actual experiment using the parameters received
def run(m=65536, n=10000, u=240000, step=30000, iters=10, k=5, hash_f='md5'):
    max_val = u
    sc = LogScreen()

    # Directory to write the logs
    directory = './logs/'

    # Definition of the name of the output files.
    log_output = 'result_m%s_n%s_k%s_h%s_i%s' % (m, n, k, hash_f, iters)
    log = LogFile(directory + log_output, "w")

    # CountingBloomFilter file
    cbf = None

    # Number of times to execute each experiment to get an average
    total_iterations = iters

    # Message printing the parameters used for the experiment
    info = "Initializing parameters counters=%d, insertions=%d, hashes=%d, hash_f=%s" % (
        m, n, k, hash_f)
    sc.write(info)

    # Build the filter passing a SHA512 hash function
    if hash_f == 'sha512':
        sha = GenericHashFunctionsSHA512(k=m, nhash=k)
        cbf = CountingBloomFilter(m=m, nhash=k, hash_f=sha)
        # Otherwise build it using the default MD5 hash
    else:
        cbf = CountingBloomFilter(m=m, nhash=k)

    # list to store the true positive elements to check if they were retrieved correctly
    ds = list()

    info = "universe;false_pos;success_iter_perc;average_retrieved;worst_retrieved;iterations"
    log.write(info + "\n")

    # Continue the execution until the number of FP does not allow any iteration to retrieve the content
    while True:
        # Number of total elements from P (true and false positives)
        total_elements = 0
        # Number of iterations completed successfully
        total_completed = 0
        # Number of total elements retrieved from the CBF
        total_extracted = 0
        # Number of elements retrieved in the worst case iteration
        worst_extracted = n

        # Run for the number of iterations expected
        for i in range(total_iterations):

            # Clear the CBF and ds list for next iteration
            cbf.clear()
            ds.clear()

            # Generate a set of n elements between 1 and max_val.
            # Include the values in CBF and add them to ds.
            generate_random_elements(n, cbf, ds, max_val)

            sc.write("length stored: %s in iteration %d" % (len(ds), i))

            # Find all elements of the universe 1 to max_val that gets a positive result from CBF
            p = find_p(cbf, max_val)
            # Accumulate the elements in total_elements for later processing.
            total_elements += len(p)
            # Retrieve all the elements from CBF that you are capable of
            positives = peeling(m, k, cbf, p, sc)
            # If ds and positives have the same size and there is no difference between them
            if len(positives) == len(ds) and len(positives.difference(ds)) == 0:
                # The iteration was completed successfully
                total_completed = total_completed + 1
            # Accumulate the number of elements retrieved in total_extracted for later processing.
            total_extracted += len(positives)
            # Check for the worst case iteration and store the number of elements extracted
            if len(positives) < worst_extracted:
                worst_extracted = len(positives)
            # peeling(m, k, cbf, ds, sc)

        # Update the average of elements extracted by dividing the accumulated sum by the number of iterations
        total_extracted = (total_extracted / total_iterations)
        # Number of false positives by getting the average of elements from P and subtracting the real positives
        false_positives = (total_elements / total_iterations) - n

        sc.write("False positives: %d and success in %d %% iterations" % (false_positives,
                                                                          (total_completed / total_iterations * 100)))
        sc.write("Average extracted: %d; Worst case: %d" % (total_extracted,
                                                            worst_extracted))
        # Store the information into a file
        info = "%s;%d;%s;%s;%s;%s" % (max_val, false_positives, (total_completed / total_iterations * 100),
                                      total_extracted, worst_extracted, total_iterations)
        log.write(info + "\n")
        log.flush()

        # If no iteration could retrieve the set of elements, finish the process
        if total_completed == 0:
            break
        # Otherwise, increase the universe in step elements and run the process again
        max_val += step

    return

if __name__ == "__main__":
    main()

