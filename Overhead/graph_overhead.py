# graph_overhead.py
#
# 
#
# Author: Sam Mansfield

import re
import sys
from matplotlib import pyplot as plt
import numpy as np

def print_usage():
  print("Correct usage")
  print("  python graph_overhead.py log_overhead")
  exit()

if len(sys.argv) != 2:
  print_usage()

log_overhead = sys.argv[1]

log_overhead_file = open(log_overhead, "r")

overhead_dict = {}
for line in log_overhead_file:
  m = re.search("Time (\d+\.\d+)s, nodes: (\d+), transmission: (\d+), radiomedium: (\w+), acv: (\d+\.\d+)%, output_dag: (.+)", line)
  if m:
    time = float(m.group(1))
    nodes = int(m.group(2))
    trans = int(m.group(3))
    medium = m.group(4)
    acv = float(m.group(5))
    output_dag = m.group(6)

    tup = (nodes, trans, medium, output_dag)
    if tup in overhead_dict:
      overhead_dict[tup].append(time)
    else:
      overhead_dict[tup] = [time]

log_overhead_file.close()

nodes_list = []
overhead_list = []
for tup in sorted(overhead_dict):
  mean = np.mean(overhead_dict[tup]) 
  std = np.std(overhead_dict[tup])
  print(str(tup) + ": mean: " + str(mean) + ", std: " + str(std))
  
  #udgm_mean = np.mean(overhead_udgm_dict[nodes])
  #terrainLOS_mean = np.mean(overhead_terrainLOS_dict[nodes])
  #print("UDGM, avg: " + str(udgm_mean) + " std: " + str(np.std(overhead_udgm_dict[nodes])))
  #print("TerrainLOS, avg: " + str(terrainLOS_mean) + " std: " + str(np.std(overhead_terrainLOS_dict[nodes])))
  #print("Difference: " + str(terrainLOS_mean - udgm_mean))
  #nodes_list.append(nodes)
  #overhead_list.append(terrainLOS_mean - udgm_mean)

#plt.plot(nodes_list, overhead_list)
#plt.xlabel("Nodes")
#plt.ylabel("Overhead (s)")
#plt.title("Overhead Vs. Number Of Nodes")
#plt.show()
