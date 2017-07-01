# calc_overhead.py
#
# Author: Sam Mansfield

import networkx as nx
import sys
import os
import re
import subprocess
import shutil
import random
import string

def print_usage():
  print("Correct usage:")
  print("  python calc_overhead.py contiki_path log_path sim_path1 sim_path2 ...")
  exit()

def set_simulation_file(sim_path, hgt, tx_range, int_range, ew, sw, eo, so, output_dag, radiomedium, out_sim_path):
  f = open(sim_path, "r")
  new_file = []
  nodes = 0
  for line in f:
    # Count number of nodes
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
    
    elif re.search("radiomediums", line):
      line = re.sub("radiomediums\..+$", "radiomediums." + str(radiomedium), line)
    
    else:
      line = line

    new_file.append(line)
  f.close()

  f = open(out_sim_path, "w")
  for line in new_file:
    f.write(line)
  f.close()

  return nodes

if len(sys.argv) < 4:
  print_usage()

#transmission_range = np.sqrt((degree*3300.0*3300.0)/(100.0*np.pi))
#interference_range = transmission_range

# Assuming we are in the directory this script is in
starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"


contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/"

log_path = sys.argv[2]

simulation_paths = []
for i in range(3, len(sys.argv)):
  simulation_paths.append(starting_directory + sys.argv[i])

terrain_directory = starting_directory + "../ACV/SRTM_Terrain/"

# Find relevant ACV paths
find_acv_path = starting_directory + "../ACV/find_acv.py"
acv_log_path = starting_directory + "../ACV/acv_std_log.txt"

# Use one ACV that is 10
output = subprocess.check_output(["python", find_acv_path, "10", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+).hgt\', (\d+), (\d+), (\d+), (\d+).*\), (\d+\.\d+)%", output_lines[0])
if m:
  hgt_10 = m.group(1)
  ew_10 = m.group(2)
  sw_10 = m.group(3)
  eo_10 = m.group(4)
  so_10 = m.group(5)
  acv_10 = m.group(6)
  hgt_10_params = (hgt_10, ew_10, sw_10, eo_10, so_10, acv_10)
else:
  print("No ACV of 10 found")
  exit()
     
# Use one ACV that is 90
output = subprocess.check_output(["python", find_acv_path, "100", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+).hgt\', (\d+), (\d+), (\d+), (\d+).*\), (\d+\.\d+)%", output_lines[0])
if m:
  hgt_100 = m.group(1)
  ew_100 = m.group(2)
  sw_100 = m.group(3)
  eo_100 = m.group(4)
  so_100 = m.group(5)
  acv_100 = m.group(6)
  hgt_100_params = (hgt_100, ew_100, sw_100, eo_100, so_100, acv_100)
else:
  print("No ACV of 100 found")
  exit()

# Download hgt files, download will only happen if terrain files are not in directory already
print("Downloading hgt files")
download_script = starting_directory + "../ACV/download_hgt_files.py" 
output = subprocess.check_output(["python", download_script, terrain_directory, hgt_10, hgt_100])
print(output)

runs = 10
progress = 0
os.chdir(contiki_path + "tools/cooja")
trans_ranges = [0, 10000]
hgt_params = [hgt_100_params]
radiomediums = ["TerrainLOSMedium", "UDGM"]
output_dags = ["true", "false"]
for simulation_path in simulation_paths:
  for trans_range in trans_ranges:
    for hgt_param in hgt_params: 
      for radiomedium in radiomediums:
        for output_dag in output_dags:
          # Create a temporary simulation path with a randomly generated name. This avoids multiple
          # processes trying to read and write the same simulation file
          # This is not needed when only one proess is running this script, but it doesn't hurt
          temp_sim_path = starting_directory
          for i in range(0, 32):
            temp_sim_path += random.choice(string.lowercase)
          temp_sim_path += ".csc"
          
          nodes = set_simulation_file(simulation_path, terrain_directory + hgt_param[0], trans_range, trans_range, hgt_param[1], hgt_param[2], hgt_param[3], hgt_param[4], output_dag, radiomedium, temp_sim_path)
          
          for i in range(0, runs):
            # Delete the dag if it exists, we will check if it was created later
            if os.path.exists("build/dag.xml"):
              os.remove("build/dag.xml")

            output = subprocess.check_output(["/usr/bin/time", "ant", "run_nogui", "-Dargs=" + temp_sim_path], stderr = subprocess.STDOUT)
           
            # Check if using TerrainLOS if the dag was created. This signals that the
            # viewshed algorihtm was run, but this can only be checked when the
            # radiomedium is TerrainLOS and 
            # output_dag is true 
            algorithm_run = False
            if radiomedium == "TerrainLOSMedium" and os.path.exists("build/dag.xml"):
              algorithm_run = True
            elif radiomedium == "UDGM":
              algorithm_run = True
            elif output_dag == "false":
              algorithm_run = True

            if algorithm_run == False:
              print("Viewshed algorithm was not run, this is not a valid simulation")
              exit()

            u_time = 0
            s_time = 0
            test_script_finished = False
            for line in output.split("\n"):
              m = re.search("(\d+\.\d+)user (\d+\.\d+)system.+", line)
              if m:
                progress += 1
                print("Completed " + str(progress) + "/" + str(len(trans_ranges)*len(hgt_params)*len(simulation_paths)*len(radiomediums)*len(output_dags)*runs))
                u_time = float(m.group(1))
                s_time = float(m.group(2))
              elif re.search("Test script finished", line):
                test_script_finished = True 
            
            total_time = u_time + s_time
            if total_time == 0:
              print(output)
              print("Time command is not functioning properly.")
              exit()

            if not test_script_finished:
              print(output)
              print("Simulation FAILED. Simulation did not end properly, output above")
              exit()
            
            print("Writing to log")
            f = open(starting_directory + log_path, "a")
            sim_info = "Time " + str(total_time) + "s, nodes: " + str(nodes) + ", transmission: " + str(trans_range) + ", radiomedium: " + radiomedium + ", acv: " + str(hgt_param[5]) + "%, output_dag: " + output_dag + "\n"
            print(sim_info)
            f.write(sim_info)
            f.close()

          os.remove(temp_sim_path)

