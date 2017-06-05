# test_terrainLOS.py
#
# Tests TerrainLOS by running a series of tests. Takes as an argument the path
# to Contiki and returns PASSED if successful and FAILED with reason on failure.
# Dependent on the file terrainLOS_simple_well_test.csc
#
# Author: Sam Mansfield

import os
import subprocess

def print_usage():
  print("Correct usage:")
  print("  python test_terrainLOS.py path_to_contiki")
  exit()

if len(os.argv) != 2:
  print_usage()

starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/"

os.chdir(contiki + "tools/cooja")
os.remove("build/dag.xml")
output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + starting_directory + "terrainLOS_simple_well_test.csc"])
shutil.copyfile("build/dag.xml", starting_directory + "dag.xml")
os.chdir(starting_directory)
output = subprocess.check_output(["diff", "terrainLOS_simple_well_test_dag.xml", "dag.xml"])
if output == "":
  print("PASSED")
else:
  print("FALIED")
  print("  diff output: " + output)
