# find_hypothetical_connectivity.py
#
# Takes in as arguments the starting acv, when to stop incrementing acv, the step size, and
# the log file to write data. This script is depenent on calc_hypothetical_connectivity.py.
# 
# This script calculates the lowest density that is 100% connected based on 
# calc_hypothetical_connectivity.py. This is found based on a binary search and each data point
# that is not stored in the provided log is written to it.
#
# Author: Sam Mansfield

import subprocess
import re
import sys
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  python find_hypothetical_connectivity.py acv_start acv_stop acv_step hc_log_path desired_connectivity")
  exit()

if len(sys.argv) != 6:
  print_usage()

# Assumed to be 0-100
acv_start = float(sys.argv[1])

# Assumed to be 0-100
acv_stop = float(sys.argv[2])

acv_step = float(sys.argv[3])

hc_log_path = sys.argv[4]
log = open(hc_log_path, "r")

desired_connectivity = int(sys.argv[5])

connectivity_dict = {}

num_of_lines = 0
for line in log:
  num_of_lines += 1
  m = re.search("Connected (\d*\.\d*)%, nodes: 100, density: (\d*), acv: (\d*\.\d*), degree: (\d+\.\d+)", line)
  if m:
    connectivity = float(m.group(1))
    density = int(m.group(2))
    acv = m.group(3)
    degree = float(m.group(4))
    tup = (density, acv)
    if tup not in connectivity_dict:
      connectivity_dict[tup] = (connectivity, degree)
  else:
    print("Improper formatting on line:")
    print(line)

log.close()
print("Read " + str(num_of_lines) + " lines")

log = open(hc_log_path, "a")

for acv in np.arange(acv_start, acv_stop, acv_step):
  lower_density_limit = 2
  density = 50
  upper_density_limit = 99
  search = True

  while search == True:
    print("Searching... acv: " + str(acv) + " density: " + str(density) + " [" + str(lower_density_limit) + ", " + str(upper_density_limit) + "]")
    tup = (density, str(acv))
    if tup in connectivity_dict:
      connectivity = connectivity_dict[tup][0]
      degree = connectivity_dict[tup][1]
    else:
      print("Tup: " + str(tup) + " not in log, adding it now")
      output = subprocess.check_output(["python", "calc_hypothetical_connectivity.py", "100", str(density), str(acv)])
      m = re.search("Connected (\d*\.\d*)%, nodes: 100, density: (\d*), acv: (\d*\.\d*), degree: (\d+\.\d+)", output)
      if m:
        log.write(output)
        connectivity = float(m.group(1))
        degree = float(m.group(4))
        connectivity_dict[tup] = (connectivity, degree)
      else:
        print("Improper formatting for output:")
        print(output)

    if connectivity >= desired_connectivity:
      if density == 2:
        density = 1
      elif density == 3:
        density = 2
      else:
        upper_density_limit = density
        density = (lower_density_limit + density)/2

      if density < 2:
        search = False
        print("Acv: " + str(acv) + " is ALWAYS connected")
    else:
      if density + 1 > 99:
        search = False
        print("Acv: " + str(acv) + " is NEVER connected")
      else:
        tup_right = (density + 1, str(acv))
        if tup_right in connectivity_dict:
          connectivity_right = connectivity_dict[tup_right][0]
          degree_right = connectivity_dict[tup_right][1]
        else:
          print("Tup: " + str(tup_right) + " not in log, adding it now")
          output = subprocess.check_output(["python", "calc_hypothetical_connectivity.py", "100", str(density + 1), str(acv)])
          m = re.search("Connected (\d*\.\d*)%, nodes: 100, density: (\d*), acv: (\d*\.\d*), degree: (\d+\.\d+)", output)
          if m:
            log.write(output)
            connectivity_right = float(m.group(1))
            degree_right = float(m.group(4))
            connectivity_dict[tup_right] = (connectivity_right, degree_right)
          else:
            print("Improper formatting for output:")
            print(output)
         
        if connectivity_right >= desired_connectivity:
          search = False
          print("Connectivity limit for acv: " + str(acv) + " is at density: " + str(density + 1) + ", degree: " + str(degree_right))
        # Have next density be 99 otherwise (98 + 100)/2 = 98 and the script will be stuck
        # in this loop
        elif density == 98:
          density = 99 
        else:
          lower_density_limit = density
          density = (density + upper_density_limit)/2

log.close()
