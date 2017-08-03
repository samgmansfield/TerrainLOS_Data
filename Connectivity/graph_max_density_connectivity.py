# graph_max_connectivity.py
#
# Graphs the max connectivity per ACV for given logs. Only examines the 
# simulations run with a density of 628.
# 
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt
from collections import defaultdict
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  python graph_max_density_connectivity.py log_path1 log_path2 ...")
  exit()

if len(sys.argv) < 2:
  print_usage()

pop_dict = {}

for log_path in sys.argv:
  # Relies on the naming convention that the only number in the file name is the population and
  # that the name of the python script does not have a number in it..
  m = re.search("(\d+)", log_path) 
  if m: 
    pop = int(m.group(1))
    # Keys are acvs at the designated population
    pop_dict[pop] = defaultdict(list)
    log = open(log_path, "r")
    for line in log:
      m_acv = re.search("^Connected (\d+\.\d+), .+ density: (\d+), acv: (\d+\.\d+)%", line)
      if m_acv:
        connectivity = float(m.group(1))
        density = int(m.group(2))
        acv = float(m.group(3))
        if density == 628:
          pop_dict[pop][acv].append(connectivity)

for pop in sorted(pop_dict):
  acv_list = []
  connectivity_list = []
  for acv in sorted(pop_dict[pop])
    acv_list.append(acv)
    connectivity_list.append(np.mean(pop_dict[pop][acv]))
  plt.plot(acv_list, connectivity_list, label = str(pop))

plt.legend()
plt.show()
