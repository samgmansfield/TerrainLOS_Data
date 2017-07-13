# graph_max_connectivity.py
#
# Graphs the max connectivity per ACV for the populations 30, 40, and 50. 
# 
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt

graph_dict = {}
for key in [1, 10, 20, 30, 40, 50]:
  graph_dict[key] = {}

for key in graph_dict:
  graph_dict[key]["acv"] = []
  graph_dict[key]["connectivity"] = []

loop_dict = {}
for key in graph_dict:
  loop_dict[key] = "ec_" + str(key) + "_log.txt"

# First loop through and find the max connectivity per ACV
for key in loop_dict:
  log = open(loop_dict[key], "r")
  
  for line in log:
    m = re.search("Connected (\d+\.\d+)%.+acv: (\d+\.\d)%", line)
    if m:
      connectivity = float(m.group(1))
      acv = float(m.group(2))
      if acv not in graph_dict[key]:
        graph_dict[key][acv] = connectivity
      else:
        if graph_dict[key][acv] < connectivity:
          graph_dict[key][acv] = connectivity
  log.close()

for key in graph_dict:
  for acv in sorted(graph_dict[key]):
    if acv != "acv" and acv != "connectivity":
      graph_dict[key]["acv"].append(acv)
      graph_dict[key]["connectivity"].append(graph_dict[key][acv])

for key in graph_dict:
  plt.plot(graph_dict[key]["acv"], graph_dict[key]["connectivity"], label=str(key))

plt.legend()
plt.show()
