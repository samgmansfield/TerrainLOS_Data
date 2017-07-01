# graph_timiing.py
#
# Graphs the timing data stored in a log based on the calculatinos of TimeTerrainLOS.java.
#
# Author: Sam Mansfield

import sys
import re
import numpy as np
from matplotlib import pyplot as plt

def print_usage():
  print("Correct Usage:")
  print("  python graph_timing.py log_path")
  exit()

if len(sys.argv) != 2:
  print_usage()

log_path = sys.argv[1]

log = open(log_path, "r")

area_dict = {}
for line in log:  
  m = re.search("Nodes: (\d+), Area: (\d+), Total Time: (\d+)", line)
  if m:
    nodes = m.group(1)
    area = m.group(2)
    time = int(m.group(3))

    if area in area_dict:
      if nodes in area_dict[area]:
        area_dict[area][nodes].append(time)
      else:
        area_dict[area][nodes] = [time]
    else:
      area_dict[area] = {}
      area_dict[area][nodes] = [time]

graph_dict = {}
for area in sorted(area_dict):
  print("Area: " + str(area))
  if area not in graph_dict:
    graph_dict[area] = {}
    graph_dict[area]["x"] = []
    graph_dict[area]["y"] = []
  for nodes in sorted(area_dict[area]):
    mean_time = np.mean(area_dict[area][nodes])
    print("Nodes: " + str(nodes) + " time: " + str(mean_time))
    graph_dict[area]["x"].append(nodes)
    graph_dict[area]["y"].append(mean_time)

for graph in graph_dict:
  plt.plot(graph_dict[graph]["x"], graph_dict[graph]["y"])
plt.show()
