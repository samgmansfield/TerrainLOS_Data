TerrainLOS is a propagation model that uses real terrain maps from the Shuttle 
Radar Topogrophy Mission (SRTM) to determine if nodes can communicate. It is
currently implemented in COOJA, a simulator for the Contiki OS.

Included in this repository is source code and instructions on how to install
TerrainLOS as well as tools used to analyze TerrainLOS.

Directories:
  2_7: Contains the source code for the TerrainLOS radiomedium for Contiki v2.7 and how
    to install.
    install_terrainLOS_2_7.py: 
      Installs TerrainLOSMedium into contiki v2.7. This script assumes Contiki is previously
      installed. Instructions to install Contiki can be found at www.contiki-os.org/start.html.
      
      The script places TerrainLOSMedium and TerrainLOSVisualizerSkin in the appropriate folders,
      modifies the config files to display TerrainLOSMedium as an option as a radiomedium, 
      rebuilds COOJA and tests that TerrainLOSMedium is working properly.

      Takes as arguments the path to your Contiki directory.

      Note: To switch to the contiki-2-7 release when in your contiki directory type:
        git checkout release-2-7
    
    TerrainLOSMedium.java:
      Source code for the radiomedium for TerrainLOS.
    
    TerrainLOSVisualizerSkin.java:
      Source code for the visualizer for TerrainLOS.
      
  3_0: Contains the source code for the TerrainLOS radiomedium for Contiki v3.0 and how
    to install.

  ACV:
    calculate_multiple_tiles.py:
      Takes in as arguments the paths to hgt files followed by the east width, south width,
      and the log filename to be used. 
      
      The script will calculate the ACV for each hgt file entered and write the results
      to the log file provided via command line. The script is dependent on the script
      calculate_tile.py. An additional script find_acv.py can be used to find a desired
      ACV from the results recorded in a log.
      
      Note: The paths to the hgt files can be entered through the command line using shell 
      expansion, for example SRTM_Terrain/*
   
    calculate_tile.py:
      Takes in the path to an hgt file the east width, south width, and path to a log file
      and then calculates the ACV for every non-overlapping (ew x sw) chunk of the hgt file. 
      The results are written to the log file provided.

      This script is depenent on the java file CalculateACV.java.
    
    CalculateACV.java:
      Calculates  and outputs the Average Cumulative Visibility (ACV) 
      of an SRTM tile to standard out.
      
      How to use:
       javac CalcuateACV.java 
       java CalculateACV SRTM_Terrain/N37W122.hgt 100 100 0 0
         Calculates ACV for SRTM tile N37W122.hgt (assuming it is in the SRTM_Terrain folder),
         sets the east width to 100, the south width to 100, the east offset to 0, and
         the south offset to 0.

    find_acv.py: 
      Takes as an argument the deired acv as a percentage and the log to search. The log data is
      assumed to be of the format:
        file.hgt, ew: num, sw: num, (eo, so), acv%

      This script then returns all log entries within one percentage of the desired acv.
      
  Hypothetical_Connectivity:
    calc_hypothetical_connectivity:
      Takes as arguments the number of nodes, the degree, and ACV. Based on these inputs
      creates a network and examines if the network is connected using the networkx python
      library. This script uses the variable loops to set the choose the number of 
      scenarios to average and outputs the percentage of those scenarios where the 
      network is connected.
      
      Note: if "test" is passed via the command line instead of an ACV the script is in 
      test mode and examines whether with an ACV of 100% is the degree equal the desired 
      degree. The script test_calc_hypothetical_connectivity.py uses this feature to
      test this script.

    find_hypothetical_connectivity:
      Takes in as arguments the starting acv, when to stop incrementing acv, the step size, and
      the log file to write data. This script is depenent on calc_hypothetical_connectivity.py.
      
      This script calculates the lowest degree that is 100% connected based on 
      calc_hypothetical_connectivity.py. This is found based on a binary search and each data point
      that is not stored in the provided log is written to it.

    graph_hypothetical_connectivity:
      Takes as input acv_start, acv_stop, acv_step, and acv_log. This script is dependent
      on the python script find_hypothetical_connectivity_limit.py.
      
      This script uses the outpt of find_hypothetical_connectivity_limit.py to graph the
      connecvitvity limit at each acv.
    
    test_calc_hypothetical_connectivity:
      A test script for calc_hypothetical_connectivity.py.

  Experimental_Connectivity:
    calc_experimental_connectivity:
      Takes as arguments the degree, ACV, and Contiki path. 
      Based on these inputs runs COOJA simulations
      and examines if the network is connected using the networkx python
      library. 
      
      Note: if "test" is passed via the command line instead of an ACV the script is in 
      test mode and examines whether with an ACV of 100% is the degree equal the desired 
      degree. The script test_calc_hypothetical_connectivity.py uses this feature to
      test this script.

    find_experimental_connectivity: 
      Takes in as arguments the starting acv, when to stop incrementing acv, the step size, and
      the log file to write data. This script is depenent on calc_hypothetical_connectivity.py.
      
      This script calculates the lowest degree that is 100% connected based on 
      calc_hypothetical_connectivity.py. This is found based on a binary search and each data point
      that is not stored in the provided log is written to it.

    log_experimental_connectivity:
      Contains the data when calculating experimental connectivity.
  orpl:
    A git sumbodule taken from github.com/simonduq/orpl

  Overhead:
    calc_overhead:
      Calculated the time it takes to run TerrainLOS and UDGM. Takes as arguments the path
      to Contiki, the path to the log file, and however many simulatons files to time.
      
    log_overhead: 
      The log that stores the timing information.

  TerrainLOS_Test:
    terrainLOS_simple_well_test.csc: 
      Simulation file to test TerrainLOS
    test_terrainLOS.py:
      Tests TerrainLOS by running a series of tests. Takes as an argument the path
      to Contiki and returns PASSED if successful and FAILED with reason on failure.
      Dependent on the file terrainLOS_simple_well_test.csc

    
