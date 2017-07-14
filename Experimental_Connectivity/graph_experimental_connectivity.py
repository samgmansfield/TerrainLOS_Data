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
for key in [1, 10, 30, 40, 50]:
  graph_dict[key] = {}

for key in graph_dict:
  graph_dict[key]["acv"] = []
  graph_dict[key]["density"] = []
  graph_dict[key]["degree"] = []

loop_dict = {}
for key in graph_dict:
  loop_dict[key] = "ec_" + str(key) + "_log.txt" 

for key in loop_dict:
  # Contiki directory should not actually be used, I assume that the data has already been
  # previously collected.
  population = str(key)
  log = loop_dict[key]
  #output = subprocess.check_output(["python", "find_experimental_connectivity.py", "10", "101", "10", log, "contiki", population, "80"])
  output = subprocess.check_output(["python", "find_experimental_connectivity.py", "30", "101", "10", log, "contiki", population, "100"])
  
  for line in output.split("\n"):
    m = re.search("Connectivity limit for acv: (.+) is at density: (\d+), degree: (\d+\.\d+)", line)
    if m:
      acv = float(m.group(1))
      graph_dict[key]["acv"].append(acv)
      #density = float(m.group(2))/6.28
      density = float(m.group(2))
      graph_dict[key]["density"].append(density)
      degree = float(m.group(3))
      graph_dict[key]["degree"].append(degree)

for key in graph_dict:
  plt.plot(graph_dict[key]["acv"], graph_dict[key]["density"], label=str(key) + "_density")
  #plt.plot(graph_dict[key]["acv"], graph_dict[key]["degree"], label=str(key) + "_degree")
plt.legend()
plt.show()
