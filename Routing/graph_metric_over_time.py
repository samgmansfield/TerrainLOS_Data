# graph_metric_over_time.py
#
# Graphs a given metric over fifteen minute intervals
#
# Author: Sam Mansfield

import subprocess
from matplotlib import pyplot as plt
import re
import numpy as np
import os
import sys

def print_usage():
  print("Correct usage:")
  print("  python graph_metric_over_timer.py metric acv analyzed_path")
  exit() 

if len(sys.argv) != 4:
  print_usage()

# Time list in seconds
step = 240
length = 7200
time_list = np.array(range(0, length, step))
metric = sys.argv[1]
acv = sys.argv[2]
analyzed_path = sys.argv[3]
# Remove anly file extensions
analyzed_name = analyzed_path.split(".")[0]
data_path = analyzed_name + "_data/"
# Where to store or read data, create it if it doesn't exisit
if not os.path.exists(data_path):
  os.mkdir(data_path)

print("ACV: " + acv + "%")
rpl_list = []
rpl_list_std = []
orpl_list = []
orpl_list_std = []
plot_path = data_path + analyzed_name + "_" + metric[0] + "ot_acv_" + str(acv) + "_step" + str(step) + "_length_" + str(length) +".txt"
if os.path.exists(plot_path):
  print("File found with plotting data")
  plot_file = open(plot_path, "r")
  for line in plot_file:
    # Format is rpl_metric, rpl_metric_std, orpl_metric, orpl_metric_std
    split_line = line.split(",")
    rpl_list.append(float(split_line[0]))
    rpl_list_std.append(float(split_line[1]))
    orpl_list.append(float(split_line[2]))
    orpl_list_std.append(float(split_line[3]))
  plot_file.close()
else:
  for start_time in time_list:
    print(str(start_time/60) + "min-" + str((start_time + step)/60) + "min")
    output = subprocess.check_output(["python", "calc_" + metric + ".py", analyzed_path, acv, str(start_time*1000000), str((start_time + step - 1)*1000000)])
    print(output)
    m = re.search("rpl_" + metric + ": ([0-9.e-]+), rpl_" + metric + "_std: ([0-9.e-]+), orpl_" + metric + ": ([0-9.e-]+), orpl_" + metric + "_std: ([0-9.e-]+)", output)
    if m:
      rpl_list.append(float(m.group(1)))
      rpl_list_std.append(float(m.group(2)))
      orpl_list.append(float(m.group(3)))
      orpl_list_std.append(float(m.group(4)))
    else:
      print("Error in output formatting")
  # Write to a file so this doesn't have to be run every time we want to change the plot
  plot_file = open(plot_path, "w")
  for i in range(len(rpl_list)):
    plot_file.write(str(rpl_list[i]) + ", " + str(rpl_list_std[i]) + ", " + str(orpl_list[i]) + ", " + str(orpl_list_std[i]) + "\n")
  plot_file.close()

plt.xlabel("Time (min)")
plt.ylabel(metric + " (%)")
plt.errorbar(time_list/60, rpl_list, yerr=rpl_list_std, label="rpl")
plt.errorbar(time_list/60, orpl_list, yerr=orpl_list_std, label="orpl")
plt.legend()
plt.savefig(plot_path[:-4] + ".pdf")
plt.show()
