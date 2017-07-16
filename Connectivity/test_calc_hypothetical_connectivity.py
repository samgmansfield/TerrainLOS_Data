# test_calc_hypothetical_connectivity.py
#
# A test script for calc_hypothetical_connectivity.py. Tests for every density from 2-99
# that the degree is the respective density. Relies on the test parameter 
# for calc_hypothetical_connectivity.
#
# Author: Sam Mansfield

import subprocess

nodes = 100
passed = 0

print("Starting tests on calc_hypothetical_connectivity.py")
print "Progress:",

passed = 0
for density in range(2, 100):
  print "x",
  output = subprocess.check_output(["python", "calc_hypothetical_connectivity.py", str(nodes), str(density), "test"])
  if output != "PASSED\n":
    print("")
    print("FAILED")
    print("output: " + output)
    print("passed " + str(passed) + " tests, FAILED on degree " + str(density))
    break
  else:
    passed += 1

if passed == 98:
  print("")
  print("All tests PASSED")
