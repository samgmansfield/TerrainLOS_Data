# graph_experimental_connectivity.py
#
# Graphs the experimental connectivity of 80% for the populations 30, 40 , and 50. 
# This script is dependent
# on the python script find_experimental_connectivity.py.
# 
# This script uses the output of find_experimental_connectivity_limit.py to graph the
# connectivity limit at each acv.
#
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt

graph_dict = {}
graph_dict[30] = {}
graph_dict[40] = {}
graph_dict[50] = {}

for key in graph_dict:
  graph_dict[key]["acv"] = []
  graph_dict[key]["density"] = []

loop_dict = {}
loop_dict[30] = "ec_30_log.txt" 
loop_dict[40] = "ec_40_log.txt" 
loop_dict[50] = "ec_50_log.txt" 

for key in loop_dict:
  # Contiki directory should not actually be used, I assume that the data has already been
  # previously collected.
  population = str(key)
  log = loop_dict[key]
  output = subprocess.check_output(["python", "find_experimental_connectivity.py", "30", "101", "10", log, "contiki", population, "100"])
  
  for line in output.split("\n"):
    m = re.search("Connectivity limit for acv: (.+) is at density: (\d+), degree: (\d+\.\d+)", line)
    if m:
      acv = float(m.group(1))
      graph_dict[key]["acv"].append(acv)
      density = float(m.group(2))/6.28
      graph_dict[key]["density"].append(density)
      degree = float(m.group(3))

for key in graph_dict:
  plt.plot(graph_dict[key]["acv"], graph_dict[key]["density"], label=str(key))
plt.legend()
plt.show()
