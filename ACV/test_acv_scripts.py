# test_acv_scripts.py
#
# This script tests each script in the ACV folder (besides itself 
# of course) and the order in which the tests are processed in the script is important as the 
# tests are dependent on each other. This script creates a test folder to store temporary
# terrain files and a temporary log to store ACV output, which are deleted on completion.
# 
# The script first tests download_hgt_files.py. It downloads the hgt files N37W122 and 
# N36W121.hgt. The two files are arbitrary and are correct names for files. 
# The terrain files are stored in the temporary terrain folder. After the
# call to download the files is complete the hgt files are checked to see if they actually exist 
# in the specified folder. If they are there the test passes.
# 
# The second test is on calculate_acv.py and find_acv.py. 
# The previous hgt files that were downloaded are 
# then passed to calculate_acv.py and the restult is written to the test log. The test
# log is then checked using find_acv.py on ten ACVs were the result is known previously.
# 
# Side effets: This script will delete the folder Test_abcdef and the file test_log_abcdef.txt
#
# Author: Sam Mansfield

import os
import subprocess
import re
import shutil

# Create a test log
test_log = "test_log_abcdef.txt"
f = open(test_log, "w")
f.close()

# Unlikely this directory exists, but if it does it will be deleted.
test_dir = "Test_abcdef"
files = os.listdir(".")
if test_dir in files:
  shutil.rmtree(test_dir)
os.mkdir(test_dir)

##################################################
# Test download_hgt_files
##################################################
print("Testing download_hgt_files.py")
output = subprocess.check_output(["python", "download_hgt_files.py", test_dir, "N37W122", "N36W121.hgt"], stderr=subprocess.STDOUT)

files = os.listdir(test_dir)
if "N37W122.hgt" in files and "N36W121.hgt" in files:
  print("PASSED: download_hgt_files.py")
else:
  print("Output:")
  print(output)
  print("FAILED: download_hgt_files.py")

##################################################
# Test calculate_acvs_of_hgts.py and find_acv.py
##################################################
print("Testing calculate_acvs_of_hgts.py and find_acv.py")

output = subprocess.check_output(["python", "calculate_acvs_of_hgts.py", "100", "100", test_log, "test", test_dir + "/N37W122.hgt", test_dir + "/N36W121.hgt"], stderr=subprocess.STDOUT)

# 3, 6, 8, 11
passed = 0
output = subprocess.check_output(["python", "find_acv.py", "3", test_log], stderr=subprocess.STDOUT)
output += subprocess.check_output(["python", "find_acv.py", "6", test_log], stderr=subprocess.STDOUT)
output += subprocess.check_output(["python", "find_acv.py", "8", test_log], stderr=subprocess.STDOUT)
output += subprocess.check_output(["python", "find_acv.py", "11", test_log], stderr=subprocess.STDOUT)
for line in output.split("\n"):
  m = re.search("\(.+\), (\d+\.\d+)%", line)
  if m:
    acv = m.group(1)
    if acv == "3.67191219122":
      passed += 1
    elif acv == "5.49799779978":
      passed += 1
    elif acv == "8.11654965497":
      passed += 1
    elif acv == "10.990450045":
      passed += 1
    else:
      print(line)
      print("Unexpected ACV")
      print("FAILED: calculate_acvs_of_hgts.py and find_acv.py")

if passed == 4:
  print("PASSED: calculate_acvs_of_hgts.py and find_acv.py")
else:
  print("Output:")
  print(output)
  print("FAILED: calculate_acvs_of_hgts.py and find_acv.py")

#output = subprocess.check_output(["python", "print_num_of_acv.py", test_log], stderr=subprocess.STDOUT)

##################################################
# Clean up
##################################################
print("Cleaning up")

# Delete test directory
shutil.rmtree(test_dir)

# Delete test log
os.remove(test_log)
