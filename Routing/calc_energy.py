# calc_energy.py
# 
# Calculates the energy of log entries in analyzed.txt that were not already analyzed. The
# calculaed energy is then appended to that entry in the log.
#
# Author: Sam Mansfield

import shutil
import re
from collections import defaultdict
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  python calc_energy.py")
  exit()

# Just in case something goes wrong
shutil.copyfile("analyzed.txt", "analyzed_backup.txt")
# In us
settle_time = 0
#stop_time = 240000000
testlog_dir = "testlogs/"
analyzed_file = open("analyzed.txt", "r")
new_analyzed_list = []

for line in analyzed_file:
  if re.search("testlog", line) and not re.search("energy", line):
    m = re.search("testlog: (.+)$", line)
    if m:
      testlog_path = m.group(1)
      testlog_file = open(testlog_dir + testlog_path, "r")
      mote_dict = defaultdict(list)
      for t_line in testlog_file:
        if re.search("Duty Cycle", t_line):
          t_m = re.search("^(\d+) ID:(\d+) .+ \((\d+) \%\)", t_line)
          if t_m:
            us = int(t_m.group(1))
            mote_id = t_m.group(2)
            energy = int(t_m.group(3))
            # Only record energy after a certain time period to avoid setup time
            #if us > settle_time and us < stop_time:
            if us > settle_time:
              mote_dict[mote_id].append(energy)
      testlog_file.close()
      max_energy = 0
      total_energy_list = []
      for mote in mote_dict:
        # Mote 1 is the sink and has its radio always on
        if mote != "1": 
          energy_list = mote_dict[mote]
          total_energy_list.extend(energy_list)
          if np.mean(energy_list) > max_energy:
            max_energy = np.mean(energy_list)
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", energy: " + str(np.mean(total_energy_list)) + ", energy_std: " + str(np.std(total_energy_list))+ ", max_energy: " + str(max_energy) + "\n"
  new_analyzed_list.append(line)
analyzed_file.close()

# Overwrite analyzed.txt with updated information
analyzed_file = open("analyzed.txt", "w")
for line in new_analyzed_list:
  analyzed_file.write(line)
analyzed_file.close()
