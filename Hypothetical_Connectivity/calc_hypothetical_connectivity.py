# calc_hypothetical_connectivity.py
#
# Takes as arguments the number of nodes, the degree, and ACV. Based on these inputs
# creates a network and examines if the network is connected using the networkx python
# library. This script uses the variable loops to set the choose the number of 
# scenarios to average and outputs the percentage of those scenarios where the 
# network is connected.
# 
# Note: if "test" is passed via the command line instead of an ACV the script is in 
# test mode and examines whether with an ACV of 100% is the degree equal the desired 
# degree. The script test_calc_hypothetical_connectivity.py uses this feature to
# test this script.
#
# Author: Sam Mansfield

import networkx as nx
import sys
import time
import random
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  python calc_hypothetical_connectivity.py nodes density acv")
  exit()

if len(sys.argv) != 4:
  print_usage()

# Number of nodes
#n = 100
n = int(sys.argv[1])

# Density of the network, must be less than the number of nodes
#density = 10
density = int(sys.argv[2])
if density > n - 1:
  density = n - 1

# Number of total possible links
#links = (n - 1)*(1 + (n - 1))/2

# Percentage a link is established
#acv = 0.5
test = 0
if sys.argv[3] == "test":
  test = 1
  acv = 1
else:
  acv = float(sys.argv[3])
  if acv > 1:
    acv = acv/100

# Iterate through "loop" number of random scenarios and check for connectedness
i = 0
loops = 10000
if test:
  loops = 1

# Progress is only for calculating time of completion
progress = loops/100
if progress == 0:
  progress = 1

t = time.time()
connected = 0
avg_degree = []
while i < loops:
  #if (i%progress == 0) and i != 0:
  #  print("Estimated time to completion: " + str(((loops - i)/progress)*(time.time() - t)))
  #  t = time.time()

  g = nx.Graph()
  g.add_nodes_from(range(0, n))
  # Generate random a random graph based on the probability of forming a link 

  # Set to n, so that the next run decreases density
  next_connect_node = n
  d = density
  for j in range(0, n):
    for k in range(0, d):
      if next_connect_node >= n:
        next_connect_node = j + 1
        # This should only affect the next iteration
        d = d - 1
      if random.random() <= acv:
        g.add_edge(j, next_connect_node)
        #print(str(j) + "->" + str(next_connect_node))
      next_connect_node += 1
  
  if nx.is_connected(g):
    connected += 1
    # G.degree() returns a dictionary where the key is the node and the value
    # is that ndoes degree
    avg_degree.append(np.mean(g.degree().values()))

  i += 1

if test:
  actual_degree = nx.degree_histogram(g)[density]
  if actual_degree == n:
    print("PASSED")
  else:
    print("FAILED, " + str(actual_degree) + " != " + str(density))
else:
  print("Connected " + str(float(connected)*100/loops) + "%, nodes: " + str(n) + ", density: " + str(density) + ", acv: " + str(acv) + ", degree: " + str(np.mean(avg_degree)))
