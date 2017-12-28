# calc_latency.py
#
# Calculates the latency based on the testlogs of a simulation. Uses the analyzed_path
# file to find testlogs and appends the analysis back to the analyzed_path.
#
# Latency is calculated by taking the difference in time from when the packet is sent to when
# it arrives at the sink. Because latency will obviously be longer the further the distance
# I also analyze the hop_latency which is the latency based on the number of hops.
#
# Author: Sam Mansfield

import sys
import shutil
import re
from collections import defaultdict
import numpy as np

def print_usage():
  print("Correct usage:")
  print("  python calc_latency.py analyzed_path")
  print("  or")
  print("  python calc_latency.py analyzed_path acv start_time end_time")
  exit()

# Parse command line arguments
if len(sys.argv) != 2 and len(sys.argv) != 5:
  print_usage()

analyzed_path = sys.argv[1]

# In us
# Start time at 30 min as this is the time the metrics settle
#start_time = 30*60*1000000
# 24 hours
#stop_time = 24*3600*1000000
start_time = 0
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

# Just in case something goes wrong make a backup
# Assumes the last four characters of the analyzed path are txt
shutil.copyfile(analyzed_path, analyzed_path[:-4] + "_backup.txt")

# Open analyzed file, setup paths and bookeeping variables
analyzed_file = open(analyzed_path, "r")
testlog_dir = "testlogs/"
# Contains the lines that will be written back to the analyzed file
new_analyzed_list = []

# Record the average energy accross all simulations
rpl_avg_latency_list = []
orpl_avg_latency_list = []

# Go through every line of the analyzed file and analyze lines that do not include latency
for line in analyzed_file:
  # If the line has a testlog (if not it signals that the network was not connected,
  # so a simulation was not run) and does not contain latency analysis perform the
  # analysis or if we are analyzing an interval analyze even if already recorded
  if re.search("testlog", line) and (not re.search("latency", line) or interval) and re.search("acv: " + acv, line) and re.search("time: 7200000", line):
    # Find the name of the testlog
    m = re.search("routing: (\w+), .+ testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      route = m.group(1)
      testlog_path = m.group(2)
      print("Analyzing testlog: " + testlog_path)
      # Testlogs are placed in the testlog_dir
      testlog_file = open(testlog_dir + testlog_path, "r")
   
      # Latency dict stores packet start time, end time, and the number of hops
      # Format:
      #   (string) packet_id: packet dict
      #     packet dict format:
      #       "start": (int) start time (us)
      #       "end": (int) end time (us)
      #       "hops": (int) hops
      latency_dict = defaultdict(dict)

      # Search for lines that either send a packet or receive a packet and 
      # record the time and the number of hops
      for t_line in testlog_file:
        # If a packet is sent record the start time
        t_m = re.search("(^\d+) ", t_line)
        if t_m:
          us = int(t_m.group(1))
          if us > start_time and us < stop_time:
            m_start = re.search("(^\d+) .+ App: sending \[(\w+) ", t_line)
            if m_start:
              time = int(m_start.group(1))
              packet_id = m_start.group(2)
              latency_dict[packet_id]["start"] = time
              #print("Packet sent: " + packet_id)

            # If a packet is received record the stop time and the number of hops
            m_end = re.search("(^\d+) .+ App: received \[(\w+) (\d+)_", t_line)
            if m_end:
              time = int(m_end.group(1))
              packet_id = m_end.group(2)
              hops = int(m_end.group(3))
              latency_dict[packet_id]["end"] = time
              latency_dict[packet_id]["hops"] = hops
              #print("Packet received: " + packet_id + " hops: " + str(hops) + " in " + str((latency_dict[packet_id]["end"] - latency_dict[packet_id]["start"])/1000000.0) + "s")
          elif us > stop_time:
            break
    
      # Stores latencies 
      latency_list = []
      # Stores hops
      hop_list = []
      # Stores latencies divided by total hops
      hop_latency_list = []

      for p in latency_dict:
        if "start" in latency_dict[p] and "end" in latency_dict[p]:
          # Latency will be in seconds
          latency = latency_dict[p]["end"] - latency_dict[p]["start"]
          # Convert to seconds
          latency = float(latency)/1000000.0
          packet_hops = float(latency_dict[p]["hops"])
          hop_latency = latency/packet_hops
          hop_list.append(packet_hops)
          latency_list.append(latency)
          hop_latency_list.append(hop_latency)
          #print("Packet received: " + p)
        else:
          print("Packet never received or sent in interval: " + p)
      
      # If the interval is out of range of a simulation there will not be any latencies
      # recorded in latency_list, in this case do not record it and make the default
      # value -1, which will not occur in a simulation 
      avg_latency = -1
      std_latency = -1
      hop_latency = -1
      hop_std = -1
      avg_hops = -1
      std_hops = -1
      if len(latency_list) > 0:
        avg_latency = np.mean(latency_list)
        std_latency = np.std(latency_list)
        hop_latency = np.mean(hop_latency_list)
        hop_std = np.mean(hop_latency_list)
        avg_hops = np.mean(hop_list)
        std_hops = np.std(hop_list)
        if route == "rpl":
          rpl_avg_latency_list.append(avg_latency)
        elif route == "orpl":
          orpl_avg_latency_list.append(avg_latency)
        else:
          print("Unrecognized route: " + route)
          exit()
      # Remove newline, will be added back later
      line = line[:-1]
      line += ", latency: " + str(avg_latency) + ", latency_std: " + str(std_latency) + ", hop_latency: " + str(hop_latency) + ", hop_latency_std: " + str(hop_std) + ", hops: " + str(avg_hops) + ", hops_std: " + str(std_hops) + "\n"

  new_analyzed_list.append(line)
analyzed_file.close()

if not interval:
  # Overwrite analyzed.txt with updated information
  analyzed_file = open(analyzed_path, "w")
  for line in new_analyzed_list:
    analyzed_file.write(line)
  analyzed_file.close()

print("rpl_latency: " + str(np.mean(rpl_avg_latency_list)) + ", rpl_latency_std: " + str(np.std(rpl_avg_latency_list)) + ", orpl_latency: " + str(np.mean(orpl_avg_latency_list)) + ", orpl_latency_std: " + str(np.std(orpl_avg_latency_list)))
