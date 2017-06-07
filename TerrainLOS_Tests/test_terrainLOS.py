# test_terrainLOS.py
#
# Tests TerrainLOS by running a series of tests. Takes as an argument the path
# to Contiki and returns PASSED if successful and FAILED with reason on failure.
# Dependent on the file terrainLOS_simple_well_test.csc
#
# Author: Sam Mansfield

import sys
import os
import subprocess
import shutil

def print_usage():
  print("Correct usage:")
  print("  python test_terrainLOS.py path_to_contiki starting_directory")
  exit()

if len(sys.argv) != 3:
  print_usage()

starting_directory = sys.argv[2]
if starting_directory[-1] != "/":
  starting_directory += "/"

contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/"

os.chdir(contiki_path + "tools/cooja")
if os.path.exists("build/dag.xml"):
  os.remove("build/dag.xml")

print("Running Simple Well Test")
output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + starting_directory + "terrainLOS_simple_well_test_2_7.csc"])
##print(output)

shutil.copyfile("build/dag.xml", starting_directory + "dag.xml")
os.chdir(starting_directory)

# Diff only exits on 0 if files match
try:
  output = subprocess.check_output(["diff", "terrainLOS_simple_well_test_dag_2_7.xml", "dag.xml"])
except subprocess.CalledProcessError as e:
  output = e.output
   
if output == "":
  print("PASSED")
else:
  print("FALIED")
  print("  diff output: " + output)
