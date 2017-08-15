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
  exit()

if len(sys.argv) != 2:
  print_usage()

analyzed_path = sys.argv[1]

# Just in case something goes wrong
# Assumes the last four characters of the analyzed path are txt
shutil.copyfile(analyzed_path, analyzed_path[:-4] + "_backup.txt")
testlog_dir = "testlogs/"
analyzed_file = open(analyzed_path, "r")
new_analyzed_list = []

for line in analyzed_file:
  if re.search("testlog", line) and not re.search("pdr", line):
    m = re.search("testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      testlog_path = m.group(1)
      testlog_file = open(testlog_dir + testlog_path, "r")
      packets_sent = 0.0
      packets_received = 0.0
      packet_set = set()
      for t_line in testlog_file:
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
      testlog_file.close()
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", pdr: " + str(100.0 - len(packet_set)*100/packets_sent) + "%\n"
  new_analyzed_list.append(line)
analyzed_file.close()

# Overwrite analyzed.txt with updated information
analyzed_file = open(analyzed_path, "w")
for line in new_analyzed_list:
  analyzed_file.write(line)
analyzed_file.close()
