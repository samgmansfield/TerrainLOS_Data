# calc_energy.py
# 
# Calculates the energy of log entries in analyzed_path that were not already analyzed. The
# calculaed energy is then appended to that entry in the log.
#
# If three arguments are given indicating the start time and end time of the simulation
# simulations within that interval are analyzed within the given time frame and
# the average energy usage within this time frame accross all simulations are printed
# in the form 
# "rpl_energy: number, rpl_energy_std: number, orpl_energy: number, orpl_energy_std: number"
#
# Author: Sam Mansfield

import shutil
import re
from collections import defaultdict
import numpy as np
import sys

def print_usage():
  print("Correct usage:")
  print("  python calc_energy.py analyzed_path")
  print("  or")
  print("  python calc_energy.py analyzed_path acv start_time end_time")
  exit()

if len(sys.argv) != 2 and len(sys.argv) != 5:
  print_usage()

analyzed_path = sys.argv[1]

# In us
# Start time is 30 min as this is the time that all metrics settle (if they settle)
#start_time = 30*60*1000000
# 24 hours
#stop_time = 24*3600*1000000
start_time = 0
# One hour
stop_time = 3600*1000000 
interval = False
# Calculate for every acv
acv = ""
# ACV is a percentage
if len(sys.argv) == 5:
  interval = True
  acv = str(float(sys.argv[2]))
  start_time = int(sys.argv[3])
  stop_time = int(sys.argv[4])

# Just in case something goes wrong
# Assumes the last four characters of the analyzed path are txt
shutil.copyfile(analyzed_path, analyzed_path[:-4] + "_backup.txt")
testlog_dir = "testlogs/"
analyzed_file = open(analyzed_path, "r")
new_analyzed_list = []

# Record the average energy accross all simulations
rpl_avg_energy_list = []
orpl_avg_energy_list = []

for line in analyzed_file:
  # Analyze the log if the line has a testlog and the energy was not already analyzed or if
  # we are analyzing an interval
  if re.search("testlog", line) and (not re.search("energy", line) or interval) and re.search("acv: " + acv, line) and re.search("time: 7200000", line):
    m = re.search("routing: (\w+), .+ testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      route = m.group(1)
      testlog_path = m.group(2)
      testlog_file = open(testlog_dir + testlog_path, "r")
      mote_dict = defaultdict(list)
      for t_line in testlog_file:
        if re.search("Duty Cycle", t_line):
          t_m = re.search("^(\d+) ID:(\d+) .+ \((\d+) \%\)", t_line)
          if t_m:
            us = int(t_m.group(1))
            mote_id = t_m.group(2)
            energy = int(t_m.group(3))
            # There are some overflow bugs in the simulation logs, this will
            # catch them
            if energy > 100:
              print("Error detected on line:")
              print(t_line)
              print("In testlog:")
              print(testlog_path)
              exit()
            # Only record energy during an interval
            if us > start_time and us < stop_time:
              mote_dict[mote_id].append(energy)
            elif us > stop_time:
              break
      testlog_file.close()
      max_energy = -1
      total_energy_list = []
      for mote in mote_dict:
        # Mote 1 is the sink and has its radio always on
        #if mote != "1": 
        energy_list = mote_dict[mote]
        total_energy_list.extend(energy_list)
        if np.mean(energy_list) > max_energy:
          max_energy = np.mean(energy_list)
      
      # If the interval is out of range of a simulation there will not be any energies 
      # recorded in total_energy_list, in this case do not record it and make the default
      # value -1, which will not occur in a simulation
      avg_energy = -1
      std_energy = -1
      if len(total_energy_list) > 0:
        avg_energy = np.mean(total_energy_list)
        std_energy = np.std(total_energy_list)
        # Store the energy of the simulation
        if route == "rpl":
          rpl_avg_energy_list.append(avg_energy)
        elif route == "orpl":
          orpl_avg_energy_list.append(avg_energy)
        else:
          print("Unrecognized route: " + route)
          exit()
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", energy: " + str(avg_energy) + "%, energy_std: " + str(std_energy)+ ", max_energy: " + str(max_energy) + "%\n"
  new_analyzed_list.append(line)
analyzed_file.close()

if not interval:
  # Overwrite analyzed.txt with updated information
  analyzed_file = open(analyzed_path, "w")
  for line in new_analyzed_list:
    analyzed_file.write(line)
  analyzed_file.close()

print("rpl_energy: " + str(np.mean(rpl_avg_energy_list)) + ", rpl_energy_std: " + str(np.std(rpl_avg_energy_list)) + ", orpl_energy: " + str(np.mean(orpl_avg_energy_list)) + ", orpl_energy_std: " + str(np.std(orpl_avg_energy_list)))  
