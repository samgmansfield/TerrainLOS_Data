# graph_memory.py
#
# Graphs the memory data stored in a log based on the calculatinos of TimeTerrainLOS.java.
#
# Author: Sam Mansfield

import sys
import re
import numpy as np
from matplotlib import pyplot as plt

def print_usage():
  print("Correct Usage:")
  print("  python graph_memory.py log_path")
  exit()

if len(sys.argv) != 2:
  print_usage()

log_path = sys.argv[1]

log = open(log_path, "r")

area_dict = {}
for line in log:  
  m = re.search("Nodes: (\d+), Area: (\d+), Memory: (.+)$", line)
  if m:
    nodes = m.group(1)
    area = int(m.group(2))
    memory = float(m.group(3))/(1024)

    if area in area_dict:
      area_dict[area].append(memory)
    else:
      area_dict[area] = [memory]

graph_dict = {}
graph_dict["area"] = []
graph_dict["memory"] = []
for area in sorted(area_dict):
  #print("Area: " + str(area))
  graph_dict["area"].append(area)
  mean_memory = np.mean(area_dict[area])
  #print("Nodes: " + str(nodes) + " memory: " + str(mean_memory))
  graph_dict["memory"].append(mean_memory)

plt.plot(graph_dict["area"], graph_dict["memory"])
plt.xlabel("Area (Arcseconds^2)")
plt.ylabel("Memory Usage (KBytes)")
plt.show()
