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

overhead_udgm_dict = {}
overhead_terrainLOS_dict = {}
for line in log_overhead_file:
  m = re.search("Time (\d+\.\d+)s, nodes: (\d+), transmission: (\d+), radiomedium: (\w+), acv: (\d+\.\d+)%", line)
  if m:
    time = float(m.group(1))
    nodes = int(m.group(2))
    trans = int(m.group(3))
    medium = m.group(4)
    acv = float(m.group(5))
    if medium == "UDGM":
      if nodes in overhead_udgm_dict:
        overhead_udgm_dict[nodes].append(time)
      else:
        overhead_udgm_dict[nodes] = [time]
    elif medium == "TerrainLOSMedium":
      if nodes in overhead_terrainLOS_dict:
        overhead_terrainLOS_dict[nodes].append(time)
      else:
        overhead_terrainLOS_dict[nodes] = [time]
log_overhead_file.close()

nodes_list = []
overhead_list = []
for key in sorted(overhead_udgm_dict.keys()):
  udgm_mean = np.mean(overhead_udgm_dict[key])
  terrainLOS_mean = np.mean(overhead_terrainLOS_dict[key])
  print("UDGM, key: " + str(udgm_mean) + " std: " + str(np.std(overhead_udgm_dict[key])))
  print("TerrainLOS, key: " + str(terrainLOS_mean) + " std: " + str(np.std(overhead_terrainLOS_dict[key])))
  print("Difference: " + str(terrainLOS_mean - udgm_mean))
  nodes_list.append(key)
  overhead_list.append(terrainLOS_mean - udgm_mean)

plt.plot(nodes_list, overhead_list)
plt.xlabel("Nodes")
plt.ylabel("Overhead (s)")
plt.title("Overhead Vs. Number Of Nodes")
plt.show()
