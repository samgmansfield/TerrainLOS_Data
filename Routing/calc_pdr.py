# calc_pdr.py
# 
# Calculates the packet delivery ratio of log entries in analyzed_path that were not already 
# analyzed. The
# calculaed pdr is then appended to that entry in the log.
# PDR is calculated by dividing the total packets received by the total packets sent.
#
# Author: Sam Mansfield

import shutil
import re
import numpy as np
import sys

def print_usage():
  print("Correct usage:")
  print("  python calc_pdr.py analyzed_path")
  print("  or")
  print("  python calc_pdr.py analyzed_path acv start_time end_time")
  exit()

if len(sys.argv) != 2 and len(sys.argv) != 5:
  print_usage()

analyzed_path = sys.argv[1]

# In us
# Start time at 30 min as this is the time for metrics to settle
start_time = 0
# 24 hours
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

rpl_avg_pdr_list = []
orpl_avg_pdr_list = []

for line in analyzed_file:
  if re.search("testlog", line) and (not re.search("pdr", line) or interval) and re.search("acv: " + acv, line) and re.search("time: 7200000", line):
    m = re.search("routing: (\w+), .+ testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      route = m.group(1)
      testlog_path = m.group(2)
      testlog_file = open(testlog_dir + testlog_path, "r")
      packets_sent = 0.0
      packets_received = 0.0
      packet_set = set()
      for t_line in testlog_file:
        t_m = re.search("(^\d+) ", t_line)
        if t_m:
          us = int(t_m.group(1))
          if us > start_time and us < stop_time:
            if re.search("App: sending", t_line):
              t_m = re.search("\[(\w+) ", t_line)
              if t_m:
                packet = t_m.group(1)
                packet_set.add(packet)
                packets_sent += 1
            if re.search("App: received", t_line):
              t_m = re.search("\[(\w+) ", t_line)
              if t_m:
                packet = t_m.group(1)
                if packet in packet_set:
                  packet_set.remove(packet) 
                  packets_received += 1
          elif us > stop_time:
            break
      testlog_file.close()

      pdr = -1.0
      if packets_sent > 0:
        pdr = 100.0 - len(packet_set)*100.0/packets_sent  
        if route == "rpl":
          rpl_avg_pdr_list.append(pdr)
        elif route == "orpl":
          orpl_avg_pdr_list.append(pdr)
        else:
          print("Unrecognized route: " + route)
          exit()
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", pdr: " + str(pdr) + "%\n"
  new_analyzed_list.append(line)
analyzed_file.close()

if not interval:
  # Overwrite analyzed.txt with updated information
  analyzed_file = open(analyzed_path, "w")
  for line in new_analyzed_list:
    analyzed_file.write(line)
  analyzed_file.close()

print("rpl_pdr: " + str(np.mean(rpl_avg_pdr_list)) + ", rpl_pdr_std: " + str(np.std(rpl_avg_pdr_list)) + ", orpl_pdr: " + str(np.mean(orpl_avg_pdr_list)) + ", orpl_pdr_std: " + str(np.std(orpl_avg_pdr_list)))
