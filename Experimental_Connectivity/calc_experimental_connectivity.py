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
import random
import string


def print_usage():
  print("Correct usage:")
  print("  python calc_experimental_connectivity.py density acv contiki_path dag_num")
  exit()

def set_simulation_file(sim_path, hgt, tx_range, int_range, ew, sw, eo, so, output_dag, out_sim_path):
  f = open(sim_path, "r")
  new_file = []
  nodes = 0
  for line in f:
    # Count the number of nodes
    if re.search("<id>(\d+)</id>", line):
      nodes += 1
    
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

  f = open(out_sim_path, "w")
  for line in new_file:
    f.write(line)
  f.close()
  
  return nodes

if len(sys.argv) != 5:
  print_usage()

# Density of the network 
density = int(sys.argv[1])

# Assumed to be a percentage in the range 0-100
acv = float(sys.argv[2])

contiki_path = sys.argv[3]
if contiki_path[-1] != "/":
  contiki_path += "/"

# Assuming we are in the directory this script is in
starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

test = False
dag_num = sys.argv[4]
if dag_num == "test":
  test = True
dag_name = "dag" + dag_num + ".xml"

if test:
  transmission_range = np.sqrt((density*3300.0*3300.0)/(10.0*np.pi))
else:
  transmission_range = np.sqrt((density*3300.0*3300.0)/(100.0*np.pi))
print("Transmission range: " + str(transmission_range))
interference_range = transmission_range

terrain_directory = starting_directory + "../ACV/SRTM_Terrain/"

if test:
  simulation_paths = [starting_directory + "test_experimental_connectivity_layout.csc"]
else:
  simulation_paths = [starting_directory + "experimental_connectivity_layout_1.csc", starting_directory + "experimental_connectivity_layout_2.csc", starting_directory + "experimental_connectivity_layout_3.csc", starting_directory + "experimental_connectivity_layout_4.csc", starting_directory + "experimental_connectivity_layout_5.csc"]
connected = 0
avg_degree = []

# The number of ACV terrains to use
if test:
  num_acvs = 2
else:
  num_acvs = 5
# The script assumes these locations
download_script = starting_directory + "../ACV/download_hgt_files.py" 
find_acv_path = starting_directory + "../ACV/find_acv.py"
#acv_log_path = starting_directory + "../ACV/acv_log.txt"
acv_log_path = starting_directory + "../ACV/acv_std_log.txt"
output = subprocess.check_output(["python", find_acv_path, str(acv), acv_log_path], stderr=subprocess.STDOUT)
acvs_to_use = output.split("\n")
# Last entry in output_lines will be "", so this line checks for 5 lines
if len(acvs_to_use) < (num_acvs + 1):
  print(output)
  print("More data needed for ACV: " + str(acv))
  exit()

for simulation_path in simulation_paths:
  for i in range(0, num_acvs):
    #m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", acvs_to_use[i])
    m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+).*\), (\d+\.\d+)%", acvs_to_use[i])
    if m:
      hgt = m.group(1)
      ew = m.group(2)
      sw = m.group(3)
      eo = m.group(4)
      so = m.group(5)
      # This would be the actual ACV, but using this will cause problems when using
      # the output
      #acv = m.group(6)
      
      # If the terrain files are not present, download them. The download script will
      # only download the terrain files that are not present
      print("Downloading: " + hgt)
      output = subprocess.check_output(["python", download_script, terrain_directory, hgt], stderr=subprocess.STDOUT)
      # Create a temporary simulation path with a randomly generated name. This avoids multiple
      # processes trying to read and write the same simulation file
      # This is not needed when only one proess is running this script, but it doesn't hurt
      temp_sim_path = starting_directory
      for i in range(0, 32):
        temp_sim_path += random.choice(string.lowercase)
      temp_sim_path += ".csc"

      nodes = set_simulation_file(simulation_path, terrain_directory + hgt, transmission_range, interference_range, ew, sw, eo, so, "true", temp_sim_path)
      
      # Delete existing dag files so that old dag files cannot be used
      if os.path.exists(dag_name):
        os.remove(dag_name)

      os.chdir(contiki_path + "tools/cooja")
      if os.path.exists("build/dag.xml"):
        os.remove("build/dag.xml")

      print("Running simulation on " + simulation_path + " ACV: " + str(acv))
      print("temp simulation path is: " + temp_sim_path)
      output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + temp_sim_path], stderr=subprocess.STDOUT)
      print("Simulation finished")

      test_script_finished  = False
      hgt_not_found = False
      for line in output.split("\n"):
        if re.search("Test script finished", line):
          test_script_finished = True 
        elif re.search("Unable to open file", line):
          hgt_not_found = True
      
      if not test_script_finished:
        print("Output:")
        print(output)
        print("FALIED. Simulation did not end properly. Output above.")
        exit()
      
      if hgt_not_found:
        print("Output:")
        print(output)
        print("FALIED. Hgt file not loaded. Output above.")
        exit()

      shutil.copyfile("build/dag.xml", starting_directory + dag_name)
      os.chdir(starting_directory)

      g = nx.Graph()
      #g.add_nodes_from(range(1, nodes + 1))
      dom_tree = xdm.parse(dag_name)
      collection = dom_tree.documentElement

      edges = collection.getElementsByTagName("edge")

      for edge in edges:
        src = edge.getElementsByTagName("source")[0].firstChild
        dest_radio = edge.getElementsByTagName("dest")[0]
        dest = dest_radio.getElementsByTagName("radio")[0].firstChild
        g.add_edge(int(src.data), int(dest.data))
   
      if nx.is_connected(g) and nx.number_of_nodes(g) == nodes:
        connected += 1
      else:
        print("Number of nodes in dag: " + str(nx.number_of_nodes(g)))
        stranded_nodes = []
        nodes_in_dag = g.nodes()
        for n in range(1, 101):
          if n not in nodes_in_dag:
            stranded_nodes.append(n)
        print("stranded_nodes: " + str(stranded_nodes))
        exit()

      avg_degree.append(np.mean(g.degree().values()))
      
      # Clean up
      os.remove(dag_name)
      os.remove(temp_sim_path)

total_runs = float(len(simulation_paths)*num_acvs)
# Example output:
# TODO: Replace example with an actual output instead of an imaginary output
# Connected 95.2%, nodes: 100, density: 60, acv: 57.2%, degree: 32
print("Connected " + str(float(connected)*100.0/total_runs) + "%, nodes: " + str(nodes) + ", density: " + str(density) + ", acv: " + str(acv) + "%, degree: " + str(np.mean(avg_degree))) 
