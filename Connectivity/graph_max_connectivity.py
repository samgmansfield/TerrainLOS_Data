# graph_max_connectivity.py
#
# Graphs the max connectivity per ACV for the populations 30, 40, and 50. 
# 
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt

def print_usage():
  print("Correct usage:")
  print("  python graph_max_connectivity.py log_path1 log_path2 ...")
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
  graph_dict[key]["connectivity"] = []

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

for key in sorted(graph_dict):
  if label:
    plt.plot(graph_dict[key]["acv"], graph_dict[key]["connectivity"], label=str(key) + " population")
  else:
    plt.plot(graph_dict[key]["acv"], graph_dict[key]["connectivity"])

if label:
  plt.legend()
plt.show()
