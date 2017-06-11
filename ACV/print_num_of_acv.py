import subprocess
import re
import sys

def print_usage():
  print("Correct usage:")
  print("  python print_num_of_acv log_file")
  exit()

if len(sys.argv) < 2:
  print_usage()

log_name = sys.argv[1]

for acv in range(1, 101):
  output = subprocess.check_output(["python", "find_acv.py", str(acv), log_name])
  num_of_acv = len(output.split("\n")) - 1
  print("acv: " + str(acv) + " num_of_acv: " + str(num_of_acv))

f = open(log_name, "r")

hgt_dict = {}
for line in f:
  m = re.search("(^.+), ew", line)
  if m:
    hgt = m.group(1)
    hgt_dict[hgt] = True

print("Terrain files analyzed:")
num_of_hgts = 0
for key in sorted(hgt_dict.keys()):
  num_of_hgts += 1
  print(str(num_of_hgts) + ":" + key)
