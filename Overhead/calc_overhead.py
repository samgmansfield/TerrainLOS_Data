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
  print("  python calc_overhead.py contiki_path log_path sim_path1 sim_path2 ...")
  exit()

def set_simulation_file(sim_path, hgt, tx_range, int_range, ew, sw, eo, so, output_dag, radiomedium):
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

  os.remove(sim_path)
  f = open(sim_path, "w")
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

# TODO: Switch loop order, find_acv only need to be called once per ACV
find_acv_path = starting_directory + "../ACV/find_acv.py"
acv_log_path = starting_directory + "../ACV/log_acv.txt"

# Use one ACV that is 10
output = subprocess.check_output(["python", find_acv_path, "10", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+).hgt\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", output_lines[0])
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
output = subprocess.check_output(["python", find_acv_path, "90", acv_log_path])
output_lines = output.split("\n")

m = re.search("\(\'(.+).hgt\', (\d+), (\d+), (\d+), (\d+)\), (\d+\.\d+)%", output_lines[0])
if m:
  hgt_90 = m.group(1)
  ew_90 = m.group(2)
  sw_90 = m.group(3)
  eo_90 = m.group(4)
  so_90 = m.group(5)
  acv_90 = m.group(6)
  hgt_90_params = (hgt_90, ew_90, sw_90, eo_90, so_90, acv_90)
else:
  print("No ACV of 90 found")
  exit()

# Download hgt files, download will only happen if terrain files are not in directory already
print("Downloading hgt files")
download_script = starting_directory + "../ACV/download_hgt_files.py" 
output = subprocess.check_output(["python", download_script, terrain_directory, hgt_10, hgt_90])
print(output)

runs = 5
os.chdir(contiki_path + "tools/cooja")
for trans in [1, 10000]:
  for hgt_params in [hgt_10_params, hgt_90_params]:
    for simulation_path in simulation_paths:
      for radiomedium in ["TerrainLOSMedium", "UDGM"]:
        nodes = set_simulation_file(simulation_path, terrain_directory + hgt_params[0], trans, trans, hgt_params[1], hgt_params[2], hgt_params[3], hgt_params[4], "true", radiomedium)
        for i in range(0, runs):
          #print("Running simulation on " + simulation_path + " ACV " + str(i + 1))
          output = subprocess.check_output(["/usr/bin/time", "ant", "run_nogui", "-Dargs=" + simulation_path], stderr = subprocess.STDOUT)
          
          u_time = 0
          s_time = 0
          test_script_finished = False
          for line in output.split("\n"):
            m = re.search("(\d+\.\d+)user (\d+\.\d+)system.+", line)
            if m:
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
          f.write("Time " + str(total_time) + "s, nodes: " + str(nodes) + ", transmission: " + str(trans) + ", radiomedium: " + radiomedium + ", acv: " + str(hgt_params[5]) + "%\n")
          f.close()
