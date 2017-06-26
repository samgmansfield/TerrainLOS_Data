# print_num_of_acv.py
# 
# Prints the number of ACVs present in a given log. Takes in as a command line argument the
# name of the log.
# 
# Author: Sam Mansfield

import subprocess
import re
import sys

def print_usage():
  print("Correct usage:")
  print("  python print_num_of_acv.py log_path")
  exit()

if len(sys.argv) < 2:
  print_usage()

log_path = sys.argv[1]

# Call find_acv.py for every integer from 1 to 100, inclusive
for acv in range(1, 101):
  output = subprocess.check_output(["python", "find_acv.py", str(acv), log_path])
  num_of_acv = len(output.split("\n")) - 1
  print("acv: " + str(acv) + " num_of_acv: " + str(num_of_acv))

f = open(log_path, "r")

# Addes the hgt files that were analyzed as a key to a dict
hgt_dict = {}
for line in f:
  m = re.search("(^.+), ew", line)
  if m:
    hgt = m.group(1)
    hgt_dict[hgt] = True

# Prints and counts the hgt files analyzed
print("Terrain files analyzed:")
num_of_hgts = 0
for key in sorted(hgt_dict.keys()):
  num_of_hgts += 1
  print(str(num_of_hgts) + ":" + key)
