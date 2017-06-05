# graph_hypothetical_connectivity.py
#
# Takes as input acv_start, acv_stop, acv_step, and acv_log. This script is dependent
# on the python script find_hypothetical_connectivity_limit.py.
# 
# This script uses the outpt of find_hypothetical_connectivity_limit.py to graph the
# connecvitvity limit at each acv.
#
# Author: Sam Mansfield

import subprocess
import re
import sys
from matplotlib import pyplot as plt

def print_usage():
  print("Correct usage")
  print("  python graph_hyppothetical_connectivity.py acv_start acv_stop acv_step acv_log")
  exit()

if len(sys.argv) != 5:
  print_usage()

acv_start = sys.argv[1]
acv_stop = sys.argv[2]
acv_step = sys.argv[3]
acv_log = sys.argv[4]

output = subprocess.check_output(["python", "find_hypothetical_connectivity_limit.py", acv_start, acv_stop, acv_step, acv_log])

acv_list = []
degree_list = []
for line in output.split("\n"):
  m = re.search("Connectivity limit for acv: (.+) is at degree: (\d+)", line)
  if m:
    acv = float(m.group(1))
    acv_list.append(acv)
    degree = int(m.group(2))
    degree_list.append(degree)

plt.plot(acv_list, degree_list)
plt.show()
