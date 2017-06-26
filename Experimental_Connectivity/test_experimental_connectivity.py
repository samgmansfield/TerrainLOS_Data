# test_experimental_connectivity.py
# 
# Tests calc_experimental_connectivity.py. Uses the test argument to analyze
# a ten node network and checks the output. The density is varied from 
# 7-9 and the degree is checked to see if it increases.
#
# Author: Sam Mansfield

import subprocess
import sys
import re

def print_usage():
  print("Correct Usage")
  print("  python calc_experimental_connectivity.py contiki_path")
  exit()

if len(sys.argv) != 2:
  print_usage()

contiki_path = sys.argv[1]

prev_degree = 0
finished = 0
for i in range(7, 10):
  print("Running experimental_connectivity.py in test mode with density " + str(i))
  output = subprocess.check_output(["python", "calc_experimental_connectivity.py", str(i), "100", contiki_path, "test"], stderr=subprocess.STDOUT)
  print(output)
  for line in output.split("\n"):
    m = re.search("Connected \d+\.\d+%, nodes: (\d+), density: (\d+), acv: (\d+\.\d+)%, degree: (\d+\.\d+)", line)
    if m:
      finished += 1
      nodes = int(m.group(1))
      density = int(m.group(2))
      acv = float(m.group(3))
      degree = float(m.group(4))
      print("Result:")
      print(line)
      #print("  nodes: " + str(nodes) + " density: " + str(density) + " acv: " + str(acv) + " degree: " + str(degree))
      if nodes != 10 or density != i or acv != 100.0:
        print(output)
        print("FAILED:")
        print("  Expected output: nodes = 10, density = " + str(i) + " acv = 100.0")
        print("  Actual output: nodes = " + str(nodes) + "density = " + str(density) + " acv = " + str(acv))
        exit()
      elif degree < prev_degree:
        print(output)
        print("FAILED: degree should increase with density: " + str(degree) + " < " + str(prev_degree))
        exit()
      prev_degree = degree

if finished == 3:
  print("PASSED")
else:
  print(output)
  print("FAILED: Script did not output correctly")
