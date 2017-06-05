# calculate_multiple_tiles.py
#
# Takes in as arguments the paths to hgt files followed by the east width, south width,
# and the log filename to be used. 
# 
# The script will calculate the ACV for each hgt file entered and write the results
# to the log file provided via command line. The script is dependent on the script
# calculate_tile.py. An additional script find_acv.py can be used to find a desired
# ACV from the results recorded in a log.
# 
# Note: The paths to the hgt files can be entered through the command line using shell 
# expansion, for example SRTM_Terrain/*

# Author: Sam Mansfield

import subprocess
import sys
import re

args = len(sys.argv)
filenames = []
for i in range(1, args - 3):
  filenames.append(sys.argv[i])

i += 1
ew = sys.argv[i]
i += 1
sw = sys.argv[i]
i += 1
log_filename = sys.argv[i]

log = open(log_filename, "r")

hgt_file_dict = {}

for line in log:
  m = re.search("(^.*hgt)", line)
  key = m.group(1)
  if key not in hgt_file_dict:
    hgt_file_dict[key] = ""
  
log.close()

for filename in filenames:
  m = re.search("(.+/)*(.+)", filename)
  hgt_file = m.group(2)
  if hgt_file not in hgt_file_dict:
    print("Analyzing " + hgt_file)
    output = subprocess.check_output(["python", "calculate_tile.py", filename, ew, sw, log_filename])
  else:
    print(hgt_file + " already analyzed")
