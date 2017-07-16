# calc_euclidean_discrete_hyp_conn.py
#
# This script instead uses a purely
# random layout and determines connectivity based on the ACV and the euclidean distance
# and groups nodes into discrete regions similar to the way DEMs are used to determine
# LOS.
#
# Author: Sam Mansfield

import networkx as nx
import random
import numpy as np
import sys
from collections import defaultdict

def print_usage():
  print("Correct usage:")
  print("  python calc_euclidean_discrete_hyp_conn.py density acv contiki_dir population")
  exit()

def distance(loca, locb):
  return np.sqrt((loca[0] - locb[0])**2 + (loca[1] - locb[1])**2)

def region(node):
  return int(int(node[0]/33) + int(node[1]/33)*ew)

if len(sys.argv) != 5:
  print_usage()

nodes = 100
density = int(sys.argv[1])
# Should be in the range 0-100
acv = float(sys.argv[2])

population = float(sys.argv[4])
ew = int(np.sqrt(nodes/(population/100)))
sw = int(np.sqrt(nodes/(population/100)))
print("ew: " + str(ew) + " sw: " + str(sw))

area = ew*33*sw*33
trans = np.sqrt((density*area)/(nodes*np.pi))

# Divide map into regions
# e.g. If ew = 2 and sw = 2
# 0 - - ew 
# | 0 1 |
# | 2 3 |
# sw- -
# Given a coordinate (x, y) the region can be found using the formula: x/33 + ew*(y/33)
los_map = defaultdict(list)
for r1 in range(0, ew*sw - 1):
  # By default you can always see yourself
  los_map[r1].append(r1)
  for r2 in range(r1 + 1, ew*sw):
    if random.random()*100 < acv:
      # LOS maps are symmetric
      los_map[r1].append(r2)
      los_map[r2].append(r1)

# Test whether we achieve the ACV we intended
visibility = []
for key in los_map:
  # Subtract 1 since we don't include the initial location as a data point
  visibility.append((len(los_map[key]) - 1)/float(ew*sw - 1))

print(np.mean(visibility))

loops = 25
connected = 0
avg_degree = []
for l in range(0, loops):
  g = nx.Graph()
  g.add_nodes_from(range(1, nodes + 1, 1))

  nodes_dict = {}
  for n in range(1, nodes + 1, 1):
    x = random.random()*ew*33 - 1
    y = random.random()*sw*33 - 1
    nodes_dict[n] = (x, y)   
    if region(nodes_dict[n]) not in los_map:
      print("Unkown region for x: " + str(x) + " y: " + str(y))
  
  for i in range(1, nodes, 1):
    for j in range(i + 1, nodes + 1, 1):
      nodei = nodes_dict[i]
      nodej = nodes_dict[j]
      if distance(nodei, nodej) < trans and region(nodej) in los_map[region(nodei)]:
        g.add_edge(i, j)

  if nx.is_connected(g):
    connected += 1
  else:
    print("Network not connected") 
    print("Number of nodes in dag: " + str(nx.number_of_nodes(g)))
    stranded_nodes = []
    nodes_in_dag = g.nodes()
    for n in range(1, nodes + 1):
      if n not in nodes_in_dag:
        stranded_nodes.append(n)
    print("stranded_nodes: " + str(stranded_nodes))
  
  avg_degree.append(np.mean(g.degree().values()))

print("Connected " + str(float(connected)*100/loops) + "%, nodes: " + str(nodes) + ", density: " + str(density) + ", acv: " + str(acv) + "%, degree: " + str(np.mean(avg_degree)) + ", population: " + str(population))
