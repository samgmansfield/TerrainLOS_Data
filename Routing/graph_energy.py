# graph_energy.py
#
# Graphs the energy usage of the simulations stored in analyzed.txt
#
# Author: Sam Mansfield

import numpy as np
import re
from collections import defaultdict

sim_time = "3600000"
# Keys are acvs with a simulation time of sim_time, values are energy usage
energy_orpl_dict = defaultdict(list)
energy_rpl_dict = defaultdict(list)

analyzed_file = open("analyzed.txt", "r")
for line in analyzed_file:
  m = re.search("acv: (\d+\.\d+)%, .+ time: (\d+), routing: (\w+), degree: (\d+\.\d+), min_degree: (\d+), max_degree: (\d+), diameter: (\d+), .+ energy: (\d+\.\d+)", line) 
  if m:
    acv = float(m.group(1))
    time = m.group(2)
    route = m.group(3)
    degree = float(m.group(4))
    min_degree = int(m.group(5))
    max_degree = int(m.group(6))
    diameter = int(m.group(7))
    energy = float(m.group(8))
    if route == "orpl" and time == sim_time:
      energy_orpl_dict[acv].append([energy, degree])
    elif route == "rpl" and time == sim_time:
      energy_rpl_dict[acv].append([energy, degree])
analyzed_file.close()

print("ORPL energy usage:")
for key in sorted(energy_orpl_dict):
  energy_list = np.array(energy_orpl_dict[key])[:,0]
  degree_list = np.array(energy_orpl_dict[key])[:,1]
  print(str(key) + ": " + str(np.mean(energy_list)) + ", std: " + str(np.std(energy_list)) + ", degree: " + str(np.mean(degree_list)) + ", std: " + str(np.std(degree_list)))

print("RPL energy usage:")
for key in sorted(energy_rpl_dict):
  energy_list = np.array(energy_rpl_dict[key])[:,0]
  degree_list = np.array(energy_rpl_dict[key])[:,1]
  print(str(key) + ": " + str(np.mean(energy_list)) + ", std: " + str(np.std(energy_list)) + ", degree: " + str(np.mean(degree_list)) + ", std: " + str(np.std(degree_list)))
