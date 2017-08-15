This directory contains scripts and data collected from running RPL and ORPL simulations. 
The simulations are based on the Let The Tree Bloom publication in SenSys 13.

Files:
  analyzed_backup.txt:
    This is a backup of the analyzed.txt file, which is created everytime the calc_energy.py
    script is run.
  analyzed.txt:
    Contains analyzed simulations using the ec_30_layout.csc simulation.
  app-collect-only-orpl.sky:
    Sky object that runs orpl during the simulation.
  app-collect-only-rpl.sky:
    Sky object that runs rpl during the simulation.
  calc_energy.py:
    A script that calculates the energy usage based on the output of the simulation.
  check_connectivity.py:
    Checks whether a simulation has a connected network.
  ec_30_layout_corner.csc:
    A simulation of population 30 that has the sink in the top left corener (NW corner).
  ec_30_layout.csc:
    A simulation of population 30 that has the sink at some random location.
  graph_energy.py:
    Graphs the energy usage using the analyzed.txt file.
  run_routing.py:
    Runs routing simulations.
  testlogs/
    Holds simulation logs, which are mentioned in the analyzed.txt file

Workflow: 
  Typically the way I will run simulation is to run multiple simulations using run_routing.py.
  This will result in group of testlogs and analyzed_randstr files. I place the testlogs in
  the testlogs folder and append the anlayzed_randstr files to the appropriate analyzed text
  file. I then run the appropriate scripts, such as calc_energy.py and then look at the 
  output using graph_energy.py
