# calculate_acvs_of_hgts.py
#
# Takes in the path to an hgt file, the east width, south width, and path to a log file
# and then calculates the ACV for every non-overlapping (ew x sw) chunk of the hgt file. 
# The results are written to the log file provided.
#
# This script is depenent on the java file CalculateACV.java.
#
# Author: Sam Mansfield

import subprocess
import sys
import re

def print_usage():
  print("Correct usage:")
  print("  python calculate_acvs_of_hgts.py ew sw log_path hgt_path1 hgt_path2 ...")
  exit()

if len(sys.argv) < 5:
  print_usage()

HGT_WIDTH = 3600

# These should be multiples of 3600
ew = int(sys.argv[1])
sw = int(sys.argv[2])

log_path = sys.argv[3]

hgt_paths = []
test = False
if sys.argv[4] == "test":
  test = True
  for i in range(5, len(sys.argv)):
    hgt_paths.append(sys.argv[i])
else:
  for i in range(4, len(sys.argv)):
    hgt_paths.append(sys.argv[i])

log = open(log_path, "r")
hgts_in_log = []

# Add hgt files already analyzed to the hgts_in_log list so that they are not analyzed twice
for line in log:
  m = re.search("(^.*hgt)", line)
  hgt_in_log = m.group(1)
  if hgt_in_log not in hgts_in_log:
    hgts_in_log.append(hgt_in_log)
log.close()

output = subprocess.check_output(["javac", "-classpath", "commons-math3-3.6.1.jar:.", "CalculateACV.java"])

log = open(log_path, "a")
for hgt_path in hgt_paths:
  m = re.search("(.+/)*(.+)", hgt_path)
  hgt = m.group(2)
  if hgt not in hgts_in_log:
    print("Analyzing " + hgt)
    stop_range = HGT_WIDTH
    if test:
      stop_range = ew*2
    for eo in range(0, stop_range, ew):
      print(str(float(eo*100)/HGT_WIDTH) + "% Complete")
      for so in range(0, stop_range, sw):
        output = subprocess.check_output(["java", "-classpath", "commons-math3-3.6.1.jar:.", "CalculateACV", hgt_path, str(ew), str(sw), str(eo), str(so)])
        m = re.search("(.+/)*(.+)", output)
        if m:
          output = m.group(2) + "\n"
        # CalculateACV will not output if a node is stranded
        #else:
        #  print("Format error for output: " + output)
        #  exit()
        log.write(output)
  else:
    print(hgt + " already analyzed")

log.close()
