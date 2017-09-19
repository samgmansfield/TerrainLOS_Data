# graph_metric.py
#
# Graphs the metric given of the simulations stored in analyzed_path
#
# Author: Sam Mansfield

import numpy as np
import re
from collections import defaultdict
import sys
import os
from matplotlib import pyplot as plt

def print_usage():
  print("Correct usage:")
  print("  python graph_metric.py metric analyzed_path")
  print("  metric: energy, pdr, duplicates, latency")
  exit()

if len(sys.argv) != 3:
  print_usage()

metric = sys.argv[1]
# Assume it is in the same directory
analyzed_path = sys.argv[2]
# Remove anly file extensions
analyzed_name = analyzed_path.split(".")[0]
data_path = analyzed_name + "_data/"
# Where to store or read data, create it if it doesn't exisit
if not os.path.exists(data_path):
  os.mkdir(data_path)

sim_time = "7200000"
# Keys are acvs with a simulation time of sim_time, values are the metric given
measure_orpl_dict = defaultdict(list)
measure_rpl_dict = defaultdict(list)

analyzed_file = open(analyzed_path, "r")
sims_analyzed = 0
for line in analyzed_file:
  m = re.search("acv: (\d+\.\d+)%, .+ time: (\d+), routing: (\w+), degree: (\d+\.\d+), .*" + metric + ": ([0-9.e-]+)", line) 
  if m:
    sims_analyzed += 1
    acv = float(m.group(1))
    time = m.group(2)
    route = m.group(3)
    degree = float(m.group(4))
    measure = float(m.group(5))
    if route == "orpl" and time == sim_time:
      measure_orpl_dict[acv].append([measure, degree])
    elif route == "rpl" and time == sim_time:
      measure_rpl_dict[acv].append([measure, degree])
analyzed_file.close()
print("Analyzed " + str(sims_analyzed) + " simulations")
if sims_analyzed == 0:
  print("ERROR: No simulations analyzed!")
  print("Have you already run calc_" + metric + ".py?")
  exit()

orpl_acv_list = []
orpl_metric_list = []
orpl_std_list = []
print("ORPL " + metric + ":")
for key in sorted(measure_orpl_dict):
  measure_list = np.array(measure_orpl_dict[key])[:,0]
  avg_measure = np.mean(measure_list)
  std_measure = np.std(measure_list)
  orpl_acv_list.append(key)
  orpl_metric_list.append(avg_measure)
  orpl_std_list.append(std_measure)
  degree_list = np.array(measure_orpl_dict[key])[:,1]
  print(str(key) + ": " + str(avg_measure) + ", std: " + str(std_measure) + ", degree: " + str(np.mean(degree_list)) + ", std: " + str(np.std(degree_list)))

rpl_acv_list = []
rpl_metric_list = []
rpl_std_list = []
print("RPL " + metric + ":")
for key in sorted(measure_rpl_dict):
  measure_list = np.array(measure_rpl_dict[key])[:,0]
  avg_measure = np.mean(measure_list)
  std_measure = np.std(measure_list)
  rpl_acv_list.append(key)
  rpl_metric_list.append(avg_measure)
  rpl_std_list.append(std_measure)
  degree_list = np.array(measure_rpl_dict[key])[:,1]
  print(str(key) + ": " + str(np.mean(measure_list)) + ", std: " + str(np.std(measure_list)) + ", degree: " + str(np.mean(degree_list)) + ", std: " + str(np.std(degree_list)))

# Numbers from let the tree bloom paper
ltb_rpl = []
ltb_orpl = []
ltb_x = [30.0, 100.0]

if metric == "pdr":
  ltb_rpl = [96.19, 97.39]
  ltb_orpl = [98.85, 99.5]
elif metric == "latency":
  ltb_rpl = [2.17, 1.14]
  ltb_orpl = [1.22, 0.47]
elif metric == "energy":
  ltb_rpl = [1.35, 0.99]
  ltb_orpl = [0.83, 0.48]
elif metric == "duplicates":
  ltb_x = [100.0]
  ltb_rpl = [0.0]
  ltb_orpl = [10.0]
else:
  ltb_x = []
  ltb_rpl = []
  ltb_orpl = []

# Sets extremely tight layout
#plt.rcParams.update({'figure.figsize': (4.0, 3.6)})
#plt.rcParams.update({'xtick.labelsize': 'small'})
#plt.rcParams.update({'savefig.bbox' : 'tight'})
#plt.rcParams.update({'savefig.pad_inches' : 0.03})

plt.xlim(25, 105)
plt.xlabel("ACV (%)")
legend_loc = "upper right"
if metric == "pdr":
  plt.ylabel("PDR (%)")
  plt.plot([30.0, 100.0], [98.85, 99.5], label="ltb_orpl", marker="o")
  plt.plot([30.0, 100.0], [96.19, 97.39], label="ltb_rpl", marker="o")
  legend_loc = "lower right"
elif metric == "latency":
  plt.ylabel("Latency (s)")
  plt.plot([30.0, 100.0], [1.22, 0.47], label="ltb_orpl", marker="o")
  plt.plot([30.0, 100.0], [2.17, 1.14], label="ltb_rpl", marker="o")
elif metric == "energy":
  plt.ylabel("Duty Cycle (%)")
  plt.plot([30.0, 100.0], [0.83, 0.48], label="ltb_orpl", marker="o")
  plt.plot([30.0, 100.0], [1.35, 0.99], label="ltb_rpl", marker="o")
elif metric == "duplicates":
  plt.ylabel("Duty Cycle (%)")
  plt.plot([100.0], [10.0], label="ltb_orpl", marker="o")
  plt.plot([100.0], [0.0], label="ltb_rpl", marker="o")
  legend_loc = "lower right"
else:
  plt.ylabel(metric)

plt.errorbar(orpl_acv_list, orpl_metric_list, yerr=orpl_std_list, label="orpl", marker="o")
plt.errorbar(rpl_acv_list, rpl_metric_list, yerr=rpl_std_list, label="rpl", marker="o")
plt.legend(loc=legend_loc)
plt.savefig(data_path + analyzed_name + "_" + metric + ".pdf")
plt.show()
