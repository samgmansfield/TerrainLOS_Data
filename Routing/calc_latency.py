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
  print("  calc_latency.py analyzed_path")
  exit()

# Parse command line arguments
if len(sys.argv) != 2:
  print_usage()

analyzed_path = sys.argv[1]

# Just in case something goes wrong make a backup
# Assumes the last four characters of the analyzed path are txt
shutil.copyfile(analyzed_path, analyzed_path[:-4] + "_backup.txt")

# Open analyzed file, setup paths and bookeeping variables
analyzed_file = open(analyzed_path, "r")
testlog_dir = "testlogs/"
# Contains the lines that will be written back to the analyzed file
new_analyzed_list = []

# Go through every line of the analyzed file and analyze lines that do not include latency
for line in analyzed_file:
  # If the line has a testlog (if not it signals that the network was not connected,
  # so a simulation was not run) and does not contain latency analysis perform the
  # analysis
  if re.search("testlog", line) and not re.search("latency", line):
    # Find the name of the testlog
    m = re.search("testlog: ([a-zA-Z0-9_.]+)", line)
    if m:
      testlog_path = m.group(1)
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
          #print("Packet received: " + packet_id + " hops: " + str(hops))
    
      # Stores latencies 
      latency_list = []
      # Stores latencies divided by total hops
      hop_latency_list = []

      for p in latency_dict:
        if "end" in latency_dict[p]:
          # Latency will be in seconds
          latency = latency_dict[p]["end"] - latency_dict[p]["start"]
          # Convert to seconds
          latency = float(latency)/1000000.0
          hop_latency = latency/float(latency_dict[p]["hops"])
          latency_list.append(latency)
          hop_latency_list.append(hop_latency)
          #print("Packet received: " + p)
        else:
          print("Packet never received: " + p)

      # Remove newline, will be added back later
      line = line[:-1]
      line += ", latency: " + str(np.mean(latency_list)) + ", latency_std: " + str(np.std(latency_list)) + ", hop_latency: " + str(np.mean(hop_latency_list)) + ", hop_latency_std: " + str(np.std(hop_latency_list)) + "\n"

  new_analyzed_list.append(line)
analyzed_file.close()

# Overwrite analyzed.txt with updated information
analyzed_file = open(analyzed_path, "w")
for line in new_analyzed_list:
  analyzed_file.write(line)
analyzed_file.close()
