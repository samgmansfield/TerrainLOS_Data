# graph_hypothetical_connectivity.py
#
# This script is dependent
# on the python script find_hypothetical_connectivity_limit.py.
# 
# This script uses the outpt of find_hypothetical_connectivity_limit.py to graph the
# connectivity limit at each acv.
#
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt

output = subprocess.check_output(["python", "find_hypothetical_connectivity_limit.py", "30", "101", "10", "hc_log.txt", "80"])

acv_list = []
density_list = []
degree_list = []
for line in output.split("\n"):
  m = re.search("Connectivity limit for acv: (.+) is at density: (\d+), degree: (\d+\.\d+)", line)
  if m:
    acv = float(m.group(1))
    acv_list.append(acv)
    density = int(m.group(2))
    density_list.append(density)
    degree = float(m.group(3))
    degree_list.append(degree)

plt.plot(acv_list, density_list)
plt.plot(acv_list, degree_list)
plt.xlabel("ACV")
plt.ylabel("Degree")
plt.title("Hypothetical Connectivity Minimum Degree vs. ACV")
plt.show()
