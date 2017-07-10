# find_hypothetical_connectivity.py
#
# Takes in as arguments the starting acv, when to stop incrementing acv, the step size, and
# the log file to write data. This script is depenent on calc_hypothetical_connectivity.py.
# 
# This script calculates the lowest density that is 100% connected based on 
# calc_experimental_connectivity.py. This is found based on a binary search and each data point
# that is not stored in the provided log is written to it.
#
# Author: Sam Mansfield

import subprocess
import re
import sys
import numpy as np
import os

def print_usage():
  print("Correct usage:")
  print("  python find_experimental_connectivity.py acv_start acv_stop acv_step ec_log_path contiki_dir population desired_connectivity")
  exit()

if len(sys.argv) != 8:
  print_usage()

# All ACV inputs are assumed to be a percentage from 0-100 
acv_start = float(sys.argv[1])
acv_stop = float(sys.argv[2])
acv_step = float(sys.argv[3])

ec_log_path = sys.argv[4]

contiki_dir = sys.argv[5]

starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

population = sys.argv[6]

desired_connectivity = float(sys.argv[7])

connectivity_dict = {}

log = open(ec_log_path, "r")
num_of_lines = 0
for line in log:
  num_of_lines += 1
  m = re.search("Connected (\d*\.\d*)%, nodes: \d+, density: (\d*), acv: (\d*\.\d*)%, degree: (\d+\.\d+)", line)
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

log = open(ec_log_path, "a")

for acv in np.arange(acv_start, acv_stop, acv_step):
  lower_density_limit = 2
  # Make upper density so that the transmission distance is the length of the diagonal of the 
  # simulation area. This works out to be:
  # d = 2*n*pi
  n = 100
  # Population of 10 has 90 nodes, all others have 100
  if population == "10":
    n = 90
  MAX_DENSITY = int(2*n*np.pi)
  upper_density_limit = MAX_DENSITY
  
  density = (lower_density_limit + upper_density_limit)/2
  
  search = True

  while search == True:
    print("Searching... acv: " + str(acv) + " density: " + str(density) + " [" + str(lower_density_limit) + ", " + str(upper_density_limit) + "]")
    tup = (density, str(acv))
    if tup in connectivity_dict:
      connectivity = connectivity_dict[tup][0]
    else:
      print("Tup: " + str(tup) + " not in log, adding it now")
      output = subprocess.check_output(["python", "calc_experimental_connectivity.py", str(density), str(acv), contiki_dir, population])
      for line in output.split("\n"):
        m = re.search("Connected (\d*\.\d*)%, nodes: \d+, density: (\d*), acv: (\d*\.\d*)%, degree: (\d+\.\d+)", output)
        if m:
          log.write(line + "\n")
          connectivity = float(m.group(1))
          degree = float(m.group(4))
          connectivity_dict[tup] = (connectivity, degree)
        #else:
        #  print("Improper formatting for output:")
        #  print(output)

    # Search for the density that is less than thedesired connectedness, 
    # but when increased by one is greater than or equal to the desired 
    # connectedness.
    if connectivity >= desired_connectivity:
      # Corner cases
      if density == 2:
        density = 1
      elif density == 3:
        density = 2
      else:
        upper_density_limit = density
        density = (lower_density_limit + density)/2

      if density < 2:
        search = False
        print("Acv: " + str(acv) + " is ALWAYS " + str(desired_connectivity) + "% connected")
    else:
      if density + 1 > MAX_DENSITY:
        search = False
        print("Acv: " + str(acv) + " is NEVER " + str(desired_connectivity) + "% connected")
      else:
        tup_right = (density + 1, str(acv))
        if tup_right in connectivity_dict:
          connectivity_right = connectivity_dict[tup_right][0]
          degree_right = connectivity_dict[tup_right][1]
        else:
          print("Tup: " + str(tup_right) + " not in log, adding it now")
          output = subprocess.check_output(["python", "calc_experimental_connectivity.py", str(density + 1), str(acv), contiki_dir, population])
          for line in output.split("\n"):
            m = re.search("Connected (\d*\.\d*)%, nodes: \d+, density: (\d*), acv: (\d*\.\d*)%, degree: (\d+\.\d+)", output)
            if m:
              log.write(line + "\n")
              connectivity_right = float(m.group(1))
              degree_right = float(m.group(4))
              connectivity_dict[tup_right] = (connectivity_right, degree_right)
            #else:
            #  print("Improper formatting for output:")
            #  print(output)
         
        if connectivity_right >= desired_connectivity:
          search = False
          print("Connectivity limit for acv: " + str(acv) + " is at density: " + str(density + 1) + ", degree: " + str(degree_right))
        # The example given is if MAX_DENSITY = 99
        # Have next density be 99 otherwise (98 + 99)/2 = 98 and the script will be stuck
        # in this loop
        elif density == MAX_DENSITY - 1:
          density = MAX_DENSITY 
        else:
          lower_density_limit = density
          density = (density + upper_density_limit)/2

log.close()
