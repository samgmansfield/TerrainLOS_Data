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

def print_usage():
  print("Correct usage:")
  print("  python graph_connectivity_limit.py log_path1 log_path2 ...")
  exit()

if len(sys.argv) < 2:
  print_usage()

graph_dict = {}
loop_dict = {}
label = True
if len(sys.argv) == 2:
  label = False
  log_path = sys.argv[1]
  loop_dict[log_path] = log_path
  graph_dict[log_path] = {}
else:
  for log_path in sys.argv:
    m = re.search("(\d+)", log_path) 
    if m: 
      pop = int(m.group(1))
      loop_dict[pop] = log_path
      graph_dict[pop] = {}

for key in graph_dict:
  graph_dict[key]["acv"] = []
  graph_dict[key]["density"] = []
  graph_dict[key]["degree"] = []

for key in loop_dict:
  # Contiki directory should not actually be used, I assume that the data has already been
  # previously collected.
  population = str(key)
  log = loop_dict[key]
  output = subprocess.check_output(["python", "find_experimental_connectivity.py", "10", "101", "10", log, "contiki", population, "100"])
  
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

for key in sorted(graph_dict):
  if label:
    plt.plot(graph_dict[key]["acv"], graph_dict[key]["density"], label=str(key) + " population")
  else:
    plt.plot(graph_dict[key]["acv"], graph_dict[key]["density"])
if label:
  plt.legend()
plt.show()
