
# coding: utf-8

# <center>
# <h1>K-MEANS</h1>
# </center>

# In[1]:

import sys
import os
import math
from multiprocessing import Pool,current_process,cpu_count,active_children
from timeit import default_timer as timer
from functools import partial


# In[2]:

sys.version  # 2.7.13 - if higher version then packages may not work


# # Alternative ingest functions
#
# Store points in variable `batch` as dictionary. key is point-id (number) and value is the vector.

# In[3]:

# 5 columns: 7.52	1	11	0.0074	7	1
# Strip off Unqiue_Key. Produce dict with line numbers as key and 5d vector as value. No empties.
def readBoyanaFile(fname):
    fid = open(fname,'r')
    data = fid.readlines()
    l = map(lambda line : map(float, line.rstrip().split())[:-1],data)
    return {i:v for i,v in enumerate(l)}

# Read in data
#my_dir = os.path.expanduser("~/Desktop/")
my_fname = "N_combinedLogs_hourly.txt"
batch = readBoyanaFile(my_fname) #one big batch as dictionary
print('Total points: ' + str(len(batch)) )  # 4338
print('First line: {}'.format(batch.items()[0]))  # (0, [7.52, 1.0, 11.0, 0.0074, 7.0])


# In[7]:

# https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption
# 9 columns: 16/12/2006;17:24:00;4.216;0.418;234.840;18.400;0.000;1.000;17.000
# Strip off first 2 and float others. Skip lines with ? (empties)
#def readElectricFile(fname):
#    fid = open(fname,'r')
#    data = [value for value in fid.readlines() if "?" not in value]
#    l = map(lambda line : map(float, line.rstrip().split(";")[2:]), data[1:])
#    return {i:v for i,v in enumerate(l)}

# Read in data
#my_dir = os.path.expanduser("~/Desktop/")
#my_fname = "household_power_consumption.txt"
#batch = readElectricFile(my_dir+my_fname) #one big batch as dictionary
#print('Total points: ' + str(len(batch)) )  # 2049280
#print('First line: {}'.format(batch.items()[0]))  # (0, [4.216, 0.418, 234.84, 18.4, 0.0, 1.0, 17.0])


# # Choose k and starting k centers
#
# Google around for different strategies for choosing k and choosing starting center values.
#
# But first use my choices to make sure you get the same result.

# In[8]:

k = 3

blen = len(batch)

initial_C = {1: batch[blen/2], 2: batch[blen/3], 3: batch[blen/5]}  # keep this to reset to

C = initial_C

# Boyana - converged to 0 changes in 25 iterations (total time .76 seconds with 4 core)
'''{1: [20.0, 5.0, 3.0, 0.0, 0.0],
    2: [17.0, 4.0, 8.0, 0.0847, 80.0],
    3: [22.0, 3.0, 1.0, 0.5874, 558.0]}
'''
# Electric - converged to 0 changes in 13 iterations (total time 273 seconds with 4 core)
'''{1: [1.318, 0.066, 244.14, 5.4, 0.0, 0.0, 19.0],
    2: [2.228, 0.072, 240.04, 9.2, 0.0, 0.0, 18.0],
    3: [0.384, 0.188, 238.91, 1.8, 0.0, 0.0, 0.0]}
'''

C


# # Functions for first phase
#
# Assign each point to closest center using euclidean distance.
#
# Note possibility of parallelization of summing: https://stackoverflow.com/a/29785751.
#
# Probably can use similar strategy for taking minimum. Break into chunks and have each core min its chunk.

# In[9]:

# thought problem: do we need the sqrt? en.wikipedia.org/wiki/Euclidean_distance#Squared_Euclidean_distance
def euclidean_distance(vec1, vec2):
    return sum(map(lambda x,y: (x-y)**2, vec1, vec2))


# In[10]:

#Given a point id, find the closest center. Return its id.
def compute_center(point, all_centers):
    value = point[1]
    centers_list = all_centers.items()
    distances = map(lambda pair: (pair[0], euclidean_distance(value, pair[1])),centers_list)
    return min(distances, key=lambda t: t[1])[0]


# In[11]:

# do a test
compute_center(batch.items()[0], C)


# # Phase 1 test loop

# In[12]:

# number of workers
processors = cpu_count()
print("Total cores available: {}".format(processors))

#N = processors  # change this to experient with different times

N = 4
print("Total cores used: {}".format(N))

# This function called when set up pool of processors. For now, just prints debugging info.
def start_process():
    #print( 'Starting {} with pid {}'.format(current_process().name,current_process().pid)) #delayed print from when pool initialized
    return

# Start a pool of N workers
pool = Pool(processes=N,
            initializer=start_process
           )


# In[13]:

iterations = 1  # just for testing
total_time = 0
for i in range(iterations):
    print("========= Starting iteration " + str(i))


    # assign points to centers 2D
    start = timer()
    partial_compute = partial(compute_center, all_centers = C) #moved this inside loop b/c gets updated after each iteration

    new_p_to_c_map = pool.map(partial_compute, batch.items())

    end = timer()

    t = end - start
    total_time += t
    print( "time of part 1: " + str(t))

pool.close() # no more tasks
pool.join()  # wrap up current tasks


# In[14]:

new_p_to_c_map[:50] #[1,1,2,3,3,3,3,3,2,2, ...]


# # Functions for second phase
#
# You now have points mapped to centers. In particular, `new_p_to_c_map` is a list of center-ids *e.g., 1,2,3. The value of
# `new_p_to_c_map[0]` is the center-id that goes with point 0.
#
# Now we need to recompute mean for all k centers.

# In[15]:

# your functions go here

# compute the new center point for each section
# points is a list(not dictionary) key value pairs of (key = point num, value = n-dimensional point
# points_to_centers is the section each point is in
# returns a dictionary of the new centers of each section (key = section, value = n-dimensional center)
# tried different ways to parallelize portions of this with pool.map, all resulted in extreme slowdown
def compute_new_centers(points, points_to_centers):
    num_points = len(points[0][1])
    new_centers = [[0]*num_points for x in range(k)]

    for i in range(len(points)):
        new_centers[points_to_centers[i]-1] = map(lambda x,y: x+y, points[i][1], new_centers[points_to_centers[i]-1])

    for key in range(k):
        new_centers[key] = map(lambda x: x/points_to_centers.count(key+1), new_centers[key])

    # build the list
    return {i+1:v for i,v in enumerate(new_centers)}

# Gets the count of the number of different items in old_centers and new_centers. Assumes they are the same length
def count_changed_centers(old_centers, new_centers):
    count = 0
    for i in range(len(old_centers)):
        count += int(old_centers[i] != new_centers[i])
    return count



# # Ready to start clustering
#
# Do set-up first. You can rerun some of these cells to try new experiments.

# In[16]:

# number of workers
processors = cpu_count()
print("Total cores available: {}".format(processors))

#N = processors  # change this to experient with different times

N = 4
print("Total cores used: {}".format(N))


# In[17]:

iterations = 50
print("Number of iterations: {}".format(iterations))


# In[18]:

# Use this to reset before each new run
p_to_c_map = [-1]*len(batch)  # -1 is not a center-id so changes on first iter will be maximum.
C = initial_C  # reset C to starting center values


# # Main loop
#
# Will stop either after so many interations or when changes to `p_to_c_map` become 0, i.e., no points changed allegiance during the current iteration.

# In[19]:

# Start a pool of N workers
pool = Pool(processes=N,
            initializer=start_process,
           )

total_time = 0

for i in range(iterations):
    print("========= Starting iteration " + str(i))


    # assign points to centers 2D
    start = timer()
    partial_compute = partial(compute_center, all_centers = C)
    new_p_to_c_map = pool.map(partial_compute, batch.items())

    end = timer()

    t = end - start
    total_time += t
    print( "time of part 1: " + str(t))

    start = timer()
    new_C = compute_new_centers(batch.items(), new_p_to_c_map)  # compute new values of centers
    end = timer()
    t = end - start
    total_time += t
    print( "time of part 2: " + str(t))
    for tup in zip(C.values(), new_C.values()):
        print(tup[0])
        print(tup[1])
        print(euclidean_distance(tup[0],tup[1]))
        print("-----------")

    changed_centers = count_changed_centers(p_to_c_map, new_p_to_c_map)  # hoping value is 0
    print('Changes: {}'.format(changed_centers))

    C = new_C  # update centers with new values
    p_to_c_map = new_p_to_c_map  #update map

    if changed_centers == 0:
          break  # last iteration caused no allegiance changes

pool.close() # no more tasks
pool.join()  # wrap up current tasks
print("Total time: " + str(total_time))


# In[ ]:




# In[ ]:
