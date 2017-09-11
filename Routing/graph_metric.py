# graph_metric.py
#
# Graphs the metric given of the simulations stored in analyzed_path
#
# Author: Sam Mansfield

import numpy as np
import re
from collections import defaultdict
import sys
from matplotlib import pyplot as plt

def print_usage():
  print("Correct usage:")
  print("  python graph_metric.py metric analyzed_path")
  print("  metric: energy, pdr, duplicates, latency")
  exit()

if len(sys.argv) != 3:
  print_usage()

metric = sys.argv[1]
analyzed_path = sys.argv[2]

sim_time = "3600000"
# Keys are acvs with a simulation time of sim_time, values are the metric given
measure_orpl_dict = defaultdict(list)
measure_rpl_dict = defaultdict(list)

analyzed_file = open(analyzed_path, "r")
sims_analyzed = 0
for line in analyzed_file:
  m = re.search("acv: (\d+\.\d+)%, .+ time: (\d+), routing: (\w+), degree: (\d+\.\d+), min_degree: (\d+), max_degree: (\d+), diameter: (\d+), .+ " + metric + ": (\d+\.\d+)", line) 
  if m:
    sims_analyzed += 1
    acv = float(m.group(1))
    time = m.group(2)
    route = m.group(3)
    degree = float(m.group(4))
    min_degree = int(m.group(5))
    max_degree = int(m.group(6))
    diameter = int(m.group(7))
    measure = float(m.group(8))
    if route == "orpl" and time == sim_time:
      measure_orpl_dict[acv].append([measure, degree])
    elif route == "rpl" and time == sim_time:
      measure_rpl_dict[acv].append([measure, degree])
analyzed_file.close()
print("Analyzed " + str(sims_analyzed) + " simulations")

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

plt.xlabel("ACV (%)")
plt.ylabel(metric)
plt.errorbar(orpl_acv_list, orpl_metric_list, yerr=orpl_std_list, label="orpl")
plt.errorbar(rpl_acv_list, rpl_metric_list, yerr=rpl_std_list, label="rpl")
plt.legend()
plt.savefig(metric + ".pdf")
plt.show()
