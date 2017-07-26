# run_routing.py
#
# Runs two routing simulations in COOJA one using RPL and the other using ORPL. 
# Only uses fully connected networks
# and stores the output to a designated directory.
#
# This script relies on one special file: analyzed.txt
# which stores networks that were previously analyzed.
# In order to avoid file contention this file is read only in this script and new
# lines to be added 
# are added to analyzed_randstr.txt, where randstr is a random string. This random
# string is also added to the file name of the COOJA mote logs.
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
  print("  python run_routing.py density acv contiki_path population")
  exit()

def set_simulation_file(sim_path, timeout, routing, hgt, tx_range, int_range, ew, sw, eo, so, output_dag, out_sim_path):
  f = open(sim_path, "r")
  new_file = []
  nodes = 0
  for line in f:
    # Count the number of nodes
    if re.search("<id>(\d+)</id>", line):
      nodes += 1
    
    if re.search("TIMEOUT", line):
      line = re.sub("\(\d+\)", "(" + timeout + ")", line)

    if re.search("firmware", line):
      line = re.sub("app-collect-only.+\.sky", "app-collect-only-" + route + ".sky", line)

    elif re.search("terrain_filepath", line):
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

population = int(sys.argv[4])

# Assuming we are in the directory this script is in
starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

randstr = ""
for i in range(0, 8):
  randstr += random.choice(string.lowercase)

analyzed_randstr_path = "analyzed_" + randstr + ".txt"

# Store previously analyzed scenarios into a dict
analyzed_file = open("analyzed.txt", "r")
analyzed_dict = {}
for line in analyzed_file:
  m = re.search("$(.+), ew: (\d+), sw: (\d+), eo: (\d+), so: (\d+), pop: (\d+), routing: (\w+)", line)
  if m:
    hgt_a = m.group(1)
    ew_a = int(m.group(2))
    sw_a = int(m.group(3))
    eo_a = int(m.group(4))
    so_a = int(m.group(5))
    pop_a = int(m.group(6))
    routing_a = m.group(7)
    analyzed_dict[(hgt_a, ew_a, sw_a, eo_a, so_a, pop_a, routing_a)] = True 

terrain_directory = starting_directory + "../ACV/SRTM_Terrain/"

if population == 1:
  # 100 nodes, 3300m x 3300m
  transmission_range = np.sqrt((density*3300.0*3300.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_1_layout.csc"
  acv_log_path = "../ACV/acv_100_log.txt"
elif population == 10:
  # 90 nodes, 990m x 990m
  transmission_range = np.sqrt((density*990.0*990.0)/(90.0*np.pi))
  simulation_path = starting_directory + "ec_10_layout.csc"
  acv_log_path = "../ACV/acv_30_log.txt"
elif population == 20:
  # 100 nodes, 726m x 726m
  transmission_range = np.sqrt((density*726.0*726.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_20_layout.csc"
  acv_log_path = "../ACV/acv_22_log.txt"
elif population == 30:
  # 100 nodes, 594m x 594m
  transmission_range = np.sqrt((density*594.0*594.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_30_layout.csc"
  acv_log_path = "../ACV/acv_18_log.txt"
elif population == 40:
  # 100 nodes, 528m x 528m
  transmission_range = np.sqrt((density*528.0*528.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_40_layout.csc"
  acv_log_path = "../ACV/acv_16_log.txt"
elif population == 50:
  # 100 nodes, 462m x 462m
  transmission_range = np.sqrt((density*462.0*462.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_50_layout.csc"
  acv_log_path = "../ACV/acv_14_log.txt"
elif population == 80:
  # 100 nodes, 363m x 363m
  transmission_range = np.sqrt((density*363.0*363.0)/(100.0*np.pi))
  simulation_path = starting_directory + "ec_80_layout.csc"
  acv_log_path = "../ACV/acv_11_log.txt"
else:
  print("Unrecognized population: " + str(population))
  exit()

print("Transmission range: " + str(transmission_range))
interference_range = transmission_range

# The number of ACV terrains to use, make sure there are at least 10
num_acvs = 10
# The script assumes these locations
download_script = starting_directory + "../ACV/download_hgt_files.py" 
find_acv_path = starting_directory + "../ACV/find_acv.py"
output = subprocess.check_output(["python", find_acv_path, str(acv), acv_log_path], stderr=subprocess.STDOUT)
acvs_to_use = output.split("\n")
random.shuffle(acvs_to_use)
# Last entry in output_lines will be "", so this line checks for 5 lines
if len(acvs_to_use) < (num_acvs + 1):
  print(output)
  print("More data needed for ACV: " + str(acv))
  exit()

# Create a temporary simulation path with a randomly generated name. This avoids multiple
# processes trying to read and write the same simulation file
# This is not needed when only one proess is running this script, but it doesn't hurt
temp_sim_path = starting_directory
for j in range(0, 32):
  temp_sim_path += random.choice(string.lowercase)
temp_sim_path += ".csc"

i = 0
route_list = ["orpl", "rpl"]
for route in route_list:
  print "Running " + route + " simulation"
  connected = False
  while not connected:
    m = re.search("\(\'(.+)\', (\d+), (\d+), (\d+), (\d+).*\), (\d+\.\d+)%", acvs_to_use[i])
    if m:
      hgt = m.group(1)
      ew = m.group(2)
      sw = m.group(3)
      eo = m.group(4)
      so = m.group(5)
      print("Checking " + hgt + ", ew: " + ew + ", sw: " + sw + ", eo: " + eo + ", so: " + so + " for connectivity")
      
      # If the terrain files are not present, download them. The download script will
      # only download the terrain files that are not present
      print("Downloading: " + hgt)
      output = subprocess.check_output(["python", download_script, terrain_directory, hgt], stderr=subprocess.STDOUT)
      
      # Check if the network is connected
      set_simulation_file(simulation_path, "15000", route, terrain_directory + hgt, transmission_range, interference_range, ew, sw, eo, so, "true", temp_sim_path)
      output = subprocess.check_output(["python", "check_connectivity.py", contiki_path, temp_sim_path])
      for line in output.split("\n"):
        m = re.search("^Connected: True, degree: (.+), min_degree: (.+), max_degree: (.+), diameter: (.+)", line)
        if m:
          connected = True
          degree = m.group(1)
          min_degree = m.group(2)
          max_degree = m.group(3)
          diameter = m.group(4)
        else:
          print(line)

      # If connected is still false try next acv
      if not connected: 
        i += 1
   
  print(hgt + ", ew: " + ew + ", sw: " + sw + ", eo: " + eo + ", so: " + so + " is connected")
  set_simulation_file(simulation_path, "15000", route, terrain_directory + hgt, transmission_range, interference_range, ew, sw, eo, so, "true", temp_sim_path)

  os.chdir(contiki_path + "tools/cooja")
  if os.path.exists("build/dag.xml"):
    os.remove("build/dag.xml")
  if os.path.exists("build/COOJA.testlog"):
    os.remove("build/COOJA.testlog")

  output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + temp_sim_path], stderr=subprocess.STDOUT)
  
  # Error checking
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
 
  testlog = route + "_" + randstr + "_testlog.txt"
  shutil.copy("build/COOJA.testlog", starting_directory + testlog)
  
  os.chdir(starting_directory)
  analyzed_randstr_file = open(analyzed_randstr_path, "w")
  analyzed_randstr_file.write(hgt + ", " + ", ew: " + ew + ", sw: " + sw + ", eo: " + eo + ", so: " + so + ", pop: " + str(population) + ", routing: " + route + ", degree: " +  degree + ", min_degree: " + min_degree + ", max_degree: " + ", diameter: " + diameter + ", testlog: " + testlog) 
  analyzed_randstr_file.close()

  # Clean up
  os.remove(temp_sim_path)
