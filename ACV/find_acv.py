# find_acv.py
#
# Takes as an argument the deired acv as a percentage and the log to search. The log data is
# assumed to be of the format:
#   file.hgt, ew: num, sw: num, (eo, so), acv%
# 
# This script then returns all log entries within one percentage of the
# desired acv.
#
# Author: Sam Mansfield

import sys
import re

def print_usage():
  print("Correct usage:")
  print("  python find_acv.py desired_acv acv_log")
  exit()

if len(sys.argv) != 3:
  print_usage()

filename = sys.argv[2]
log = open(filename, "r")

desired_acv = float(sys.argv[1])

acv_dict = {}
for line in log:
  m = re.search("(^.*hgt), ew: (\d+), sw: (\d+), \((\d+), (\d+)\), (.+)%", line)
  if m:
    hgt = m.group(1)
    ew = int(m.group(2))
    sw = int(m.group(3))
    eo = int(m.group(4))
    so = int(m.group(5))
    acv = float(m.group(6))
    
    value = (hgt, ew, sw, eo, so)
    if acv not in acv_dict:
      acv_dict[acv] = []
    
    acv_dict[acv].append(value)

log.close()

error = 1
for acv in acv_dict:
  if (acv > desired_acv - error) and (acv < desired_acv + error):
    for a in acv_dict[acv]:
      print(str(a) + ", " + str(acv) + "%") 
