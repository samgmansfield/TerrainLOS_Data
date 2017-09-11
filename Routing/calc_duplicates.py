# calc_duplicates.py
# 
# This script calculates the percentage of duplicate packets sent based on the
# corresponding logs. The analyzed text file is read and any line that does not have an entry
# for the duplicate percentage is examined and calculated.
#
# To calculate the duplicate percentage each packet is tracked, using the packet's unique identifier,
# at each hop and the amount of hops until the packet reaches its destination.
# Each time a hop is recorded that amount of transmissions is stored and if an additional log
# entry has the same amount of hops for the same packet those transmissions are stored as duplicates.
# Additionally all hops that are above the total amount of hops to reach the destination are
# counted as ducplicate transmissions. 
#
# The result is written back to the analyzed file in the form 
# "duplicates: (float)%
#
# Sam Mansfield

import sys
from collections import defaultdict
import re
import shutil
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  calc_duplicates.py analyzed_path")
  print("  or")
  print("  python calc_duplicates.py analyzed_path acv start_time end_time")
  exit()

# Parse command line arguments
if len(sys.argv) != 2 and len(sys.argv) != 5:
  print_usage()

analyzed_path = sys.argv[1]

# In us
# Start time at 30 min as this is the time for metrics to settle
start_time = 30*60*1000000
# 24 hours
stop_time = 24*3600*1000000
interval = False
# Calculate for every acv
acv = ""
# ACV is a percentage
if len(sys.argv) == 5:
  interval = True
  acv = str(float(sys.argv[2]))
  start_time = int(sys.argv[3])
  stop_time = int(sys.argv[4])

# Just in case something goes wrong make a backup
# Assumes the last four characters of the analyzed path are txt
shutil.copyfile(analyzed_path, analyzed_path[:-4] + "_backup.txt")

# Open analyzed file, setup paths and bookeeping variables
analyzed_file = open(analyzed_path, "r")
testlog_dir = "testlogs/"
# Contains the lines that will be written back to the analyzed file
new_analyzed_list = []

# Record the average duplicates accross all simulations
rpl_avg_dup_list = []
orpl_avg_dup_list = []

# Go through every line of analyzed file and analyze lines that do not inlucde duplicate
# analysis
for line in analyzed_file:
  # If the line has a testlog (if not it signals that the network was not connected,
  # so a simulation was not run) and does not contain duplicate analysis perform the
  # analysis
  if re.search("testlog", line) and (not re.search("duplicates", line) or interval) and re.search("acv: " + acv, line):
    # Find the name of the testlog
    m = re.search("routing: (\w+), .+ testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      route = m.group(1)
      testlog_path = m.group(2)
      print("Analyzing testlog: " + testlog_path)
      # Testlogs are placed in the testlog_dir
      testlog_file = open(testlog_dir + testlog_path, "r")

      # Setup duplicate dict
      # Format of duplicate dict:
      #   (string) packet_identifiers: dict
      #     Format of packet dict:   
      #       "transmissions": (int) transmissions + collisions 
      #       "duplicates": (int) duplicates
      #       "last_hop": (int) last hop
      #       (int) 0: (int) transmissions + collisions
      #       (int) 1: (int) transmissions + collisions
      #       ...:
      # Transmissions is the total number of transmissions per packet. Duplicates is only the
      # duplicate transmissions. Last hop is to account for additional hops past the last hop,
      # which are obiously duplicate transmissions as the packet already arrived at the 
      # destination.
      duplicate_dict = defaultdict(dict)

      for t_line in testlog_file:
        t_m = re.search("(^\d+) ", t_line)
        if t_m:
          us = int(t_m.group(1))
          if us > start_time and us < stop_time:
            # If a packet is sent initialize transmissions and duplicates
            m_send = re.search("App: sending \[(\w+)", t_line)
            if m_send:
              packet_id = m_send.group(1)
              duplicate_dict[packet_id]["transmissions"] = 0
              duplicate_dict[packet_id]["duplicates"] = 0

            # If a packet is successful deterimine if it is duplicate traffic and keep track
            # of the transmissions
            m_success = re.search("Csma: success .+ (\d+) tx, (\d+) collisions \[(\w+) (\d+)_", t_line)
            if m_success:
              tx = int(m_success.group(1))
              collisions = int(m_success.group(2))
              packet_id = m_success.group(3)
              hops = int(m_success.group(4))
             
              # Only store information for flows that have a recorded App: sending
              if packet_id in duplicate_dict:
                # Store the transmissions as long the packet was not already transmitted 
                # with the same amount of hops
                if hops not in duplicate_dict[packet_id]:
                  duplicate_dict[packet_id][hops] = tx + collisions 
                  duplicate_dict[packet_id]["transmissions"] += tx + collisions

                # If the packet was previously sent with the same number of hops add
                # the transmissions to the duplicate entries as well as the transmissions
                else:
                  duplicate_dict[packet_id]["duplicates"] += tx + collisions 
                  duplicate_dict[packet_id]["transmissions"] += tx + collisions

            # If a packet is received by the sink store the number of hops
            m_recv = re.search("App: received \[(\w+) (\d+)_", t_line)
            if m_recv:
              packet_id = m_recv.group(1)
              hops = int(m_recv.group(2))
              # Only store information for flows that have a recorded App: sending
              if packet_id in duplicate_dict:
                duplicate_dict[packet_id]["last_hop"] = hops
          elif us > stop_time:
            break
    
      # Count the total transmissions and duplicates
      transmissions = 0
      duplicates = 0
      for p in duplicate_dict:
        # Find the last hop and add all hops greater than or equal to the last hop
        # to duplicates as those transmissions must be duplicates
        if "last_hop" in duplicate_dict[p]:
          last_hop = duplicate_dict[p]["last_hop"] 
          i = last_hop
          while i in duplicate_dict[p]:
            duplicate_dict[p]["duplicates"] += duplicate_dict[p][i]
            i += 1
          # Only record tranmssions and duplicates for flows that have a start and end
          transmissions += duplicate_dict[p]["transmissions"]
          duplicates += duplicate_dict[p]["duplicates"]
        else:
          print("No last hop for packet: " + p)
      
      dup_percentage = -1.0 
      if transmissions > 0:
        dup_percentage = float(duplicates)*100.0/float(transmissions)
        if route == "rpl":
          rpl_avg_dup_list.append(dup_percentage)
        elif route == "orpl":
          orpl_avg_dup_list.append(dup_percentage)
        else:
          print("unrecognized route: " + route)
          exit()
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", duplicates: " + str(dup_percentage) + "%, transmissions: " + str(float(transmissions)) + "\n"
  
  new_analyzed_list.append(line)
analyzed_file.close()

if not interval:
  # Overwrite analyzed.txt with updated information
  analyzed_file = open(analyzed_path, "w")
  for line in new_analyzed_list:
    analyzed_file.write(line)
  analyzed_file.close()

print("rpl_duplicates: " + str(np.mean(rpl_avg_dup_list)) + ", rpl_duplicates_std: " + str(np.std(rpl_avg_dup_list)) + ", orpl_duplicates: " + str(np.mean(orpl_avg_dup_list)) + ", orpl_duplicates_std: " + str(np.std(orpl_avg_dup_list)))
