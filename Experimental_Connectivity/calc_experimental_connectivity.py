# calc_experimental_connectivity.py
#
# Takes as arguments the degree, ACV, and Contiki path. 
# Based on these inputs runs COOJA simulations
# and examines if the network is connected using the networkx python
# library. 
# 
# Note: if "test" is passed via the command line instead of an ACV the script is in 
# test mode and examines whether with an ACV of 100% is the degree equal the desired 
# degree. The script test_calc_hypothetical_connectivity.py uses this feature to
# test this script.
#
# Author: Sam Mansfield

import networkx as nx
import sys
import os
import re
import subprocess
import shutil
import numpy as np
from xml.dom.minidom import parse
import xml.dom.minidom as xdm


def print_usage():
  print("Correct usage:")
  print("  python calc_experimental_connectivity.py degree acv contiki_path starting_directory")
  exit()

def set_simulation_file(sim_path, hgt, tx_range, int_range, ew, sw, eo, so, output_dag):
  f = open(sim_path, "r")
  new_file = []
  for line in f:
    if re.search("terrain_filepath", line):
      if re.search("<terrain_filepath />", line):
        line = re.sub("path \/\>", "path>" + str(hgt) + "</terrain_filepath>", line)
      else:
        line = re.sub("\>.+\<", ">" + str(hgt) + "<", line)

    elif re.search("transmitting_range", line):
      line = re.sub("\d+\.\d+", str(float(tx_range)), line)

    elif re.search("interference_range", line):
      line = re.sub("\d+\.\d+", str(float(int_range)), line)
    
    elif re.search("east_width", line):
      line = re.sub("\d+", str(int(ew)), line)
    
    elif re.search("south_width", line):
      line = re.sub("\d+", str(int(sw)), line)
    
    elif re.search("east_offset", line):
      line = re.sub("\d+", str(int(eo)), line)
    
    elif re.search("south_offset", line):
      line = re.sub("\d+", str(int(so)), line)
    
    elif re.search("south_offset", line):
      line = re.sub("\d+", str(int(so)), line)
    
    elif re.search("output_dag", line):
      line = re.sub("\>.+\<", ">" + str(output_dag) + "<", line)

    else:
      line = line

    new_file.append(line)
  f.close()

  os.remove(sim_path)
  f = open(sim_path, "w")
  for line in new_file:
    f.write(line)
  f.close()

if len(sys.argv) != 5:
  print_usage()

# Density of the network, must be less than the number of nodes, which is always 100
#degree = 10
degree = int(sys.argv[1])
if degree > 99:
  degree = 99

transmission_range = np.sqrt((degree*3300.0*3300.0)/(100.0*np.pi))
interference_range = transmission_range

# Percentage a link is established
#acv = 0.5
acv = float(sys.argv[2])
if acv <= 1:
  acv = acv*100.0

contiki_path = sys.argv[3]
if contiki_path[-1] != "/":
  contiki_path += "/"

# Assuming we are in the directory this script is in
starting_directory = sys.argv[4]
if starting_directory[-1] != "/":
  starting_directory += "/"

terrain_directory = starting_directory + "../ACV/SRTM_Terrain/"

simulation_paths = [starting_directory + "experimental_connectivity_layout_1.csc", starting_directory + "experimental_connectivity_layout_2.csc", starting_directory + "experimental_connectivity_layout_3.csc", starting_directory + "experimental_connectivity_layout_4.csc", starting_directory + "experimental_connectivity_layout_5.csc"]
connected = 0
num_acvs = 5
for simulation_path in simulation_paths:
  # TODO: Switch loop order, find_acv only need to be called once per ACV
  find_acv_path = starting_directory + "../ACV/find_acv.py"
  acv_log_path = starting_directory + "../ACV/log_acv.txt"
  output = subprocess.check_output(["python", find_acv_path, str(acv), acv_log_path])
  output_lines = output.split("\n")
  # Last entry in output_lines will be "", so this line checks for 5 lines
  if len(output_lines) < (num_acvs + 1):
    print("More data needed for ACV: " + str(acv))
  else:
    for i in range(0, num_acvs):
      m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", output_lines[i])
      if m:
        hgt = m.group(1)
        ew = m.group(2)
        sw = m.group(3)
        eo = m.group(4)
        so = m.group(5)
        #acv = m.group(6)
           
        set_simulation_file(simulation_path, terrain_directory + hgt, transmission_range, interference_range, ew, sw, eo, so, "true")
    
        os.chdir(contiki_path + "tools/cooja")
        if os.path.exists("build/dag.xml"):
          os.remove("build/dag.xml")

        #print("Running simulation on " + simulation_path + " ACV " + str(i + 1))
        output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + simulation_path])

        shutil.copyfile("build/dag.xml", starting_directory + "dag.xml")
        os.chdir(starting_directory)

        g = nx.Graph()
        g.add_nodes_from(range(1, 101))
        dom_tree = xdm.parse("dag.xml")
        collection = dom_tree.documentElement

        edges = collection.getElementsByTagName("edge")

        for edge in edges:
          src = edge.getElementsByTagName("source")[0].firstChild
          dest_radio = edge.getElementsByTagName("dest")[0]
          dest = dest_radio.getElementsByTagName("radio")[0].firstChild
          g.add_edge(int(src.data), int(dest.data))
    
        if nx.is_connected(g):
          connected += 1

total_runs = float(len(simulation_paths)*num_acvs)
print("Connected " + str(float(connected)*100.0/total_runs) + "%, nodes: " + str(100) + ", degree: " + str(degree) + ", acv: " + str(acv)) 
