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
import re

def print_usage():
  print("Correct usage:")
  print("  python test_terrainLOS.py contiki_path")
  exit()

if len(sys.argv) != 2:
  print_usage()

starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/"

# Remove dag file if it already exists, this way we know that we are not using
# an old dag file from a previous run
if os.path.exists("dag.xml"):
  os.remove("dag.xml")
os.chdir(contiki_path + "tools/cooja")
if os.path.exists("build/dag.xml"):
  os.remove("build/dag.xml")

print("Running Simple Well Test")
output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + starting_directory + "no_compile_terrainLOS_simple_well_test_2_7.csc"], stderr=subprocess.STDOUT)

test_script_finished = False
for line in output.split("\n"):
  m = re.search("Test script finished", line)
  if m:
    test_script_finished = True 

if not test_script_finished:
  print("Output:")
  print(output)
  print("FAILED. Simulation did not end properly. Output above.")
  exit()

shutil.copyfile("build/dag.xml", starting_directory + "dag.xml")
os.chdir(starting_directory)

# Diff only exits on 0 if files match
# TODO: It would be better to actually compare the graph instead of just doing a diff.
try:
  output = subprocess.check_output(["diff", "terrainLOS_simple_well_test_dag_2_7.xml", "dag.xml"])
except subprocess.CalledProcessError as e:
  output = e.output

os.remove("dag.xml")

if output == "":
  print("PASSED")
else:
  print("FALIED")
  print("  diff output: " + output)
