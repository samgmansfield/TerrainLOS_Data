# calc_overhead.py
#
# Author: Sam Mansfield

import networkx as nx
import sys
import os
import re
import subprocess
import shutil


def print_usage():
  print("Correct usage:")
  print("  python calc_overhead.py contiki_path starting_directory")
  exit()

def set_simulation_file(sim_path, hgt, tx_range, int_range, ew, sw, eo, so, output_dag, radiomedium):
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
    
    elif re.search("radiomediums", line):
      line = re.sub("radiomediums\..+$", ">" + str(output_dag) + "<", line)

    else:
      line = line

    new_file.append(line)
  f.close()

  os.remove(sim_path)
  f = open(sim_path, "w")
  for line in new_file:
    f.write(line)
  f.close()

if len(sys.argv) != 3:
  print_usage()

#transmission_range = np.sqrt((degree*3300.0*3300.0)/(100.0*np.pi))
#interference_range = transmission_range

contiki_path = sys.argv[3]
if contiki_path[-1] != "/":
  contiki_path += "/"

# Assuming we are in the directory this script is in
starting_directory = sys.argv[4]
if starting_directory[-1] != "/":
  starting_directory += "/"

terrain_directory = starting_directory + "../ACV/SRTM_Terrain/"

simulation_paths = [starting_directory + "one_node.csc", starting_directory + "ten_nodes.csc", starting_directory + "twenty_nodes.csc", starting_directory + "fifty_nodes.csc", starting_directory + "one_hundred_nodes.csc"]

# TODO: Switch loop order, find_acv only need to be called once per ACV
find_acv_path = starting_directory + "../ACV/find_acv.py"
acv_log_path = starting_directory + "../ACV/log_acv.txt"

# Use one ACV that is 10
output = subprocess.check_output(["python", find_acv_path, "10", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", output_lines[0])
if m:
  hgt_10 = m.group(1)
  ew_10 = m.group(2)
  sw_10 = m.group(3)
  eo_10 = m.group(4)
  so_10 = m.group(5)
  acv_10 = m.group(6)
     
# Use one ACV that is 90
output = subprocess.check_output(["python", find_acv_path, "90", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", output_lines[0])
if m:
  hgt_90 = m.group(1)
  ew_90 = m.group(2)
  sw_90 = m.group(3)
  eo_90 = m.group(4)
  so_90 = m.group(5)
  acv_90 = m.group(6)



set_simulation_file(simulation_path, terrain_directory + hgt, transmission_range, interference_range, ew, sw, eo, so, "true")

for simulation_path in simulation_paths:
    
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
