# find_hypothetical_connectivity.py
#
# Takes in as arguments the starting acv, when to stop incrementing acv, the step size, and
# the log file to write data. This script is depenent on calc_hypothetical_connectivity.py.
# 
# This script calculates the lowest degree that is 100% connected based on 
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
  print("  python find_experimental_connectivity.py acv_start acv_stop acv_step acv_log contiki_path starting_directory")
  exit()

if len(sys.argv) != 7:
  print_usage()

acv_start = float(sys.argv[1])
if acv_start > 1:
  acv_start = acv_start/100

acv_stop = float(sys.argv[2])
if acv_stop > 1:
  acv_stop = acv_stop/100

acv_step = float(sys.argv[3])
if acv_step > 1:
  acv_step = acv_step/100

filename = sys.argv[4]
f = open(filename, "r")

contiki_path = sys.argv[5]

starting_directory = sys.argv[6]
if starting_directory[-1] != "/":
  starting_directory += "/"

connectivity_dict = {}

num_of_lines = 0
for line in f:
  num_of_lines += 1
  m = re.search("Connected (\d*\.\d*)%, nodes: 100, degree: (\d*), acv: (\d*\.\d*)", line)
  if m:
    connectivity = float(m.group(1))
    degree = int(m.group(2))
    acv = m.group(3)
    tup = (degree, acv)
    if tup not in connectivity_dict:
      connectivity_dict[tup] = connectivity
  else:
    print("Improper formatting on line:")
    print(line)

f.close()
print("Read " + str(num_of_lines) + " lines")

f = open(filename, "a")

for acv in np.arange(acv_start, acv_stop, acv_step):
  lower_degree_limit = 2
  degree = 50
  upper_degree_limit = 99
  search = True

  while search == True:
    print("Searching... acv: " + str(acv) + " degree: " + str(degree) + " [" + str(lower_degree_limit) + ", " + str(upper_degree_limit) + "]")
    tup = (degree, str(acv))
    if tup in connectivity_dict:
      connectivity = connectivity_dict[tup]
    else:
      print("Tup: " + str(tup) + " not in log, adding it now")
      output = subprocess.check_output(["python", "calc_experimental_connectivity.py", str(degree), str(acv), contiki_path, starting_directory])
      m = re.search("Connected (\d*\.\d*)%, nodes: 100, degree: (\d*), acv: (\d*\.\d*)", output)
      if m:
        f.write(output)
        connectivity = float(m.group(1))
        connectivity_dict[tup] = connectivity
      else:
        print("Improper formatting for output:")
        print(output)

    if connectivity == 100.0:
      if degree == 3:
        degree = 2
      else:
        upper_degree_limit = degree
        degree = (lower_degree_limit + degree)/2

      if degree < 2:
        search = False
        print("Acv: " + str(acv) + " is ALWAYS connected")
    else:
      if degree + 1 > 99:
        search = False
        print("Acv: " + str(acv) + " is NEVER connected")
      else:
        tup_right = (degree + 1, str(acv))
        if tup_right in connectivity_dict:
          connectivity_right = connectivity_dict[tup_right]
        else:
          print("Tup: " + str(tup_right) + " not in log, adding it now")
          output = subprocess.check_output(["python", "calc_experimental_connectivity.py", "100", str(degree + 1), str(acv), starting_directory])
          m = re.search("Connected (\d*\.\d*)%, nodes: 100, degree: (\d+), acv: (\d+\.\d+)", output)
          if m:
            f.write(output)
            connectivity_right = float(m.group(1))
            connectivity_dict[tup_right] = connectivity_right
          else:
            print("Improper formatting for output:")
            print(output)
         
        if connectivity_right == 100.0:
          search = False
          print("Connectivity limit for acv: " + str(acv) + " is at degree: " + str(degree + 1))
        # Have next degree be 99 otherwise (98 + 100)/2 = 98 and the script will be stuck
        # in this loop
        elif degree == 98:
          degree = 99 
        else:
          lower_degree_limit = degree
          degree = (degree + upper_degree_limit)/2

f.close()
