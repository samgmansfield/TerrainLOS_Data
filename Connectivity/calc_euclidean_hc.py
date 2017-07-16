# calc_euclidean_hyp_conn.py
#
# The idealized hypothetical model is actually too reliable. This script instead uses a purely
# random layout and determine connectivity based on the ACV and the euclidean distance.
#
# Author: Sam Mansfield

import networkx as nx
import random
import numpy as np
import sys

def print_usage():
  print("Correct usage:")
  print("  python calc_euclidean_hyp_conn.py density acv contiki_dir population")
  print("  contiki_dir, population: dummy variables for compatibility")
  exit()

def distance(loca, locb):
  return np.sqrt((loca[0] - locb[0])**2 + (loca[1] - locb[1])**2)

if len(sys.argv) != 5:
  print_usage()

nodes = 100
density = int(sys.argv[1])
# Should be in the range 0-100
acv = float(sys.argv[2])

area = 3300*3300
trans = np.sqrt((density*area)/(nodes*np.pi))

loops = 25
connected = 0
avg_degree = []
for l in range(0, loops):
  g = nx.Graph()
  g.add_nodes_from(range(0, nodes, 1))

  nodes_dict = {}
  for n in range(0, nodes, 1):
    x = random.random()*3300
    y = random.random()*3300
    nodes_dict[n] = (x, y)   
  
  for i in range(0, nodes, 1):
    for j in range(i + 1, nodes, 1):
      if random.random()*100 < acv and distance(nodes_dict[i], nodes_dict[j]) < trans:
        g.add_edge(i, j)

  if nx.is_connected(g):
    connected += 1
  
  avg_degree.append(np.mean(g.degree().values()))

print("Connected " + str(float(connected)*100/loops) + "%, nodes: " + str(nodes) + ", density: " + str(density) + ", acv: " + str(acv) + "%, degree: " + str(np.mean(avg_degree)))
