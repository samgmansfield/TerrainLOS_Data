# install_terrainLOS_2_7.py
#
# Installs TerrainLOSMedium into contiki v2.7. This script assumes Contiki is previously
# installed. Instructions to install Contiki can be found at www.contiki-os.org/start.html.
# 
# The script places TerrainLOSMedium and TerrainLOSVisualizerSkin in the appropriate folders,
# modifies the config files to display TerrainLOSMedium as an option as a radiomedium, 
# rebuilds COOJA and tests that TerrainLOSMedium is working properly. 
# 
# Takes as arguments the path to your Contiki directory. Also assumes you are running this
# script inside this directory.
# 
# Note: To switch to the contiki-2-7 release when in your contiki directory type:
#   git checkout release-2-7
#
# Author: Sam Mansfield

import sys
import shutil
import re
import os
import subprocess

def print_usage():
  print("Correct usage:")
  print("  python install_terrainLOS_2_7.py path_to_contiki")
  exit()

if len(sys.argv) != 2:
  print_usage()

starting_directory = os.getcwd()
if starting_directory[-1] != "/":
  starting_directory += "/" 

contiki_path = sys.argv[1]
if contiki_path[-1] != "/":
  contiki_path += "/" 

print("Copying TerrainLOSMedium to radiomediums folder")
radiomedium_path = contiki_path + "tools/cooja/java/se/sics/cooja/radiomediums/TerrainLOSMedium.java"
shutil.copyfile("TerrainLOSMedium.java", radiomedium_path)

print("Copying TerrainLOSVisualizerSkin to plugins/skins folder")
skin_path = contiki_path + "tools/cooja/java/se/sics/cooja/plugins/skins/TerrainLOSVisualizerSkin.java"
shutil.copyfile("TerrainLOSVisualizerSkin.java", skin_path)

print("Modifying cooja_applet.config to include TerrainLOS")
cooja_applet_config = contiki_path + "tools/cooja/config/cooja_applet.config"
f = open(cooja_applet_config, "r")
new_file = []
for line in f:
  m = re.search("(se\.sics\.cooja\.GUI\.RADIOMEDIUMS.+)", line)
  if m:
    line = m.group(1)
    m = re.search("TerrainLOSMedium", line)
    if not m:
      line += " se.sics.cooja.radiomediums.TerrainLOSMedium\n"
  new_file.append(line)
f.close()
os.remove(cooja_applet_config)

f = open(cooja_applet_config, "w")
for line in new_file:
  f.write(line)
f.close()

print("Modifying cooja_default.config to include TerrainLOS")
cooja_default_config = contiki_path + "tools/cooja/config/cooja_default.config"
f = open(cooja_default_config, "r")
new_file = []
for line in f:
  m = re.search("(se\.sics\.cooja\.GUI\.RADIOMEDIUMS.+)", line)
  if m:
    line = m.group(1)
    m = re.search("TerrainLOSMedium", line)
    if not m:
      line += " se.sics.cooja.radiomediums.TerrainLOSMedium\n"
  new_file.append(line)
f.close()
os.remove(cooja_default_config)

f = open(cooja_default_config, "w")
for line in new_file:
  f.write(line)
f.close()

print("Modifying external_tools.config to include TerrainLOS")
external_tools_config = contiki_path + "tools/cooja/config/external_tools.config"
f = open(external_tools_config, "r")
new_file = []
add_terrainLOS = False
for line in f:
  if add_terrainLOS:
    m = re.search("TerrainLOS", line)
    if not m:
      new_file.append("se.sics.cooja.plugins.skins.TerrainLOSVisualizerSkin;\\\n")
    add_terrainLOS = False 
  
  new_file.append(line)
  
  m = re.search("VISUALIZER_DEFAULT_SKINS", line)
  if m:
    add_terrainLOS = True

f.close()
os.remove(external_tools_config)

f = open(external_tools_config, "w")
for line in new_file:
  f.write(line)
f.close()

print("Cleaning COOJA build")
os.chdir(contiki_path + "tools/cooja")
output = subprocess.check_output(["ant", "clean"])
#print(output)

# Test if successful
os.chdir(starting_directory + "../TerrainLOS_Tests/")
print("Running tests")
output = subprocess.check_output(["python", "test_terrainLOS.py", contiki_path])
m = re.search("PASSED", output)
if m:
  print("Installation SUCCESS")
else:
  print("Installation FAILED")
