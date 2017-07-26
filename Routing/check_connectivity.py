# calc_experimental_connectivity.py
#
# Tests a scenario for connectivity. If a scenario is connected returns:
#   Connected: True, degree: num, min_degree: num, max_degree: num, diameter: num
# Any other output can be assumed that the network is not connected
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
  print("  python calc_experimental_connectivity.py contiki_path sim_path")
  exit()

def count_nodes(sim_path):
  f = open(sim_path, "r")
  nodes = 0
  for line in f:
    # Count the number of nodes
    if re.search("<id>(\d+)</id>", line):
      nodes += 1
  return nodes

if len(sys.argv) != 3:
  print_usage()

contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/"

# Sim path should be a full path
sim_path = sys.argv[2]

# Assuming we are in the directory this script is in
starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/"

dag_name = "dag"
for i in range(0, 8):
  dag_name += random.choice(string.lowercase)
dag_name += ".xml"

connected = 0

nodes = count_nodes(sim_path)

# Delete existing dag files so that old dag files cannot be used
if os.path.exists(dag_name):
  os.remove(dag_name)

os.chdir(contiki_path + "tools/cooja")
if os.path.exists("build/dag.xml"):
  os.remove("build/dag.xml")

output = subprocess.check_output(["ant", "run_nogui", "-Dargs=" + sim_path], stderr=subprocess.STDOUT)

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
  print("FAILED. Simulation did not end properly. Output above.")
  exit()

if hgt_not_found:
  print("Output:")
  print(output)
  print("FAILED. Hgt file not loaded. Output above.")
  exit()

shutil.copyfile("build/dag.xml", starting_directory + dag_name)
os.chdir(starting_directory)

g = nx.Graph()
dom_tree = xdm.parse(dag_name)
collection = dom_tree.documentElement

edges = collection.getElementsByTagName("edge")

for edge in edges:
  src = edge.getElementsByTagName("source")[0].firstChild
  dest_radio = edge.getElementsByTagName("dest")[0]
  dest = dest_radio.getElementsByTagName("radio")[0].firstChild
  g.add_edge(int(src.data), int(dest.data))

if nx.is_connected(g) and nx.number_of_nodes(g) == nodes:
  degree = np.mean(g.degree().values())
  min_degree = min(g.degree().values())
  max_degree = max(g.degree().values())
  diameter = nx.diameter(g)
  print("Connected: True, degree: " + str(degree) + ", min_degree: " + str(min_degree) + ", max_degree: " +  str(max_degree) + ", diameter: " + str(diameter))
else:
  print("Network not connected") 
  print("Number of nodes in dag: " + str(nx.number_of_nodes(g)))
  stranded_nodes = []
  nodes_in_dag = g.nodes()
  for n in range(1, nodes + 1):
    if n not in nodes_in_dag:
      stranded_nodes.append(n)
  print("stranded_nodes: " + str(stranded_nodes))

# Clean up
os.remove(dag_name)
