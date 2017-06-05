# calculate_tile.py
#
# Takes in the path to an hgt file the east width, south width, and path to a log file
# and then calculates the ACV for every non-overlapping (ew x sw) chunk of the hgt file. 
# The results are writting to the log file provided.
#
# This script is depenent on the java file CalculateACV.java.
#
# Author: Sam Mansfield

import subprocess
import sys
import re

def print_usage():
  print("Correct usage:")
  print("  python calculate_tile.py hgt_file ew sw log_file")
  exit()

if len(sys.argv) != 5):
  print_usage()

HGT_WIDTH = 3600

filename = sys.argv[1]
ew = sys.argv[2]
sw = sys.argv[3]

log_filename = sys.argv[4]
log = open(log_filename, "a")

output = subprocess.check_output(["javac", "CalculateACV.java"])

for eo in range(0, HGT_WIDTH, 100):
  print(str(float(eo*100)/HGT_WIDTH) + "% Complete")
  for so in range(0, HGT_WIDTH, 100):
    output = subprocess.check_output(["java", "CalculateACV", filename, ew, sw, str(eo), str(so)])
    m = re.search("(.+/)*(.+)", output)
    if m:
      output = m.group(2) + "\n"
    else:
      print("Format error for output: " + output)
      exit()
    log.write(output)

log.close()
