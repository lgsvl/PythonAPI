# Python API for LGSVL Simulator

This folder contains Python API for LGSVL Simulator.

# Usage

Look into `quickstart` folder for simple usages.
To run these examples first start the simulator and leave it in main menu.
By default examples connect to Simulator on `localhost` address.
To change it, adjust first argument of `Simulator` constructor, or set up
`SIMULATOR_HOST` environment variable with hostname.

# Documentation

Documentation is available on our website: https://www.lgsvlsimulator.com/docs/python-api/

# Requirements

* Python 3.5 or higher

# Installing

    pip3 install --user .
    
    # install in development mode
    pip3 install --user -e .

# LGSVL PythonAPI Scenario Randomizer

The Scenario Randomizer is split into four components:

<h2> LGSVL Sim: </h2>

LGSVL (LG Silicon Valley Lab) Simulator is simulation software developed for the acceleration of safe autonomous vehicle development. The current version as of writing this document is 2019.10, however LG have stated that they plan on releasing a new version every month or so. LGSVL is required for the Scenario Randomizer.

<h2> LGSVL PythonAPI: </h2>

LGSVL Simulator exposes runtime functionality to a Python API which you can use to manipulate object placement and vehicle movement in a loaded scene, retreive sensor configuration and data, control weather, time state, and more. The Scenario Randomization script is written using this PythonAPI. The full documentation can be found here: https://www.lgsvlsimulator.com/docs/python-api/

<h2> ROSBridge: </h2>

ROSBridge allows for the connection between ROS and the vehicle. This means that once the ROSBridge connection is established we can view the vehicle’s sensor output, or send it commands.

<h2> Scenario Randomizer GUI: </h2>

The GUI was made in Python using the Tkinter module. The GUI allows the user to control the parameters of the scenario without needing to enter the code, such as the amount of NPC Vehicles to spawn, the runtime of the scenario, or the timescale.


To proceed, please download the latest version of the LGSVL Sim and the Scenario Randomizer:

The latest version of the LGSVL Simulator can be downloaded/cloned from here: https://www.lgsvlsimulator.com/

The Scenario Randomizer can be cloned from here: https://bitbucket.org/Bibman/pythonapi/src/master/


# Launching through the bash script

Each component (RosBridge, GUI, LGSVL sim) can be manually run on it’s own, however for ease of use I have included a bash script which launches everything simultaneously, and uses xdotool to skip the graphical settings menu of the simulator. To run it, cd into where you cloned the repository, and execute the launch script.
    
    cd ~/PythonAPI
    ./launch.sh
    
Furthermore, if you would like to change the graphical settings of the simulator from its’ default state, you can add the -r argument to the launch command.

    ./launch.sh -r

# Launching each component manually

<h2> LGSVL: </h2>

In the LGSVL folder, find the ‘simulator’ executable and run it. It should open a graphical settings menu. Select the graphics that best fit your specifications and press ‘OK’. After that you should be greeted with a menu similar to this one.

![lgsvl site](/misc/3.png)

Press the ‘Open Browser’ button, and a webpage should open. More on this webpage later.

<h2> ROSBridge: </h2>

Assuming you have ROS installed and a stable internet connection, open a new terminal and type the following.

    roslaunch rosbridge_server rosbridge_websocket.launch

<h2> GUI: </h2>

cd into PythonAPI/RS_scripts and run the following command.

    python3 GUI.py

# The LGSVL sim website

![site](/misc/6.png)

There are four tabs on the website; Maps, Vehicles, Clusters, and Simulations
The following links explain in-depth about each tab.

Maps: https://www.lgsvlsimulator.com/docs/maps-tab/

Vehicles: https://www.lgsvlsimulator.com/docs/vehicles-tab/

Clusters: https://www.lgsvlsimulator.com/docs/clusters-tab/

Simulations: https://www.lgsvlsimulator.com/docs/simulations-tab/

An important thing to note is that the Scenario Randomizer is currently only set to work when everything is running on one computer
Once you have a simulation under the simulation tab that is using the map, vehicle, and cluster of your choice, with respect to the notes above, you can select it then press the button on the bottom of the webpage to run the simulation.
The simulation is now running and waiting for the API to determine the scenario passed from the GUI.

![site](/misc/7.png)

# The GUI

The GUI is split into four tabs; Run, Replay, Output, and Params. The GUI allows for running multiple scenarios using a particular LGSVL map and vehicle, replaying these randomly generated scenarios, and saving them to a file to be replayed at a later time.

<h2> The Run tab </h2>
    
![run tab](/misc/8.png)

The entry boxes are labelled and fairly self-explanatory, however I will go over them regardless.

Vehicle name – As it states in the label under the entry box, it is vital that the name is entered exactly as it is written on the LGSVL sim website

Seed – An integer between -2147483649 and 2147483647 that determines the behaviour of the NPC vehicles

NPCs – A dropdown box for selecting how many NPCs to spawn

Map – Similar to the vehicle name, it is critical the name is exactly as it appears on the LGSVL site

Runs – The amount of times to randomly generate a scenario using the selected values

Runtime – The time in seconds of each scenario generated using the selected values

Timescale – The timescale of each scenario, however be aware that it is fairly buggy

RUN – The activation button, runs the simulation with the selected variables

If a value entered raises an exception, the GUI displays it at the bottom, under the “RUN” button

<h2> The Replay tab </h2>
    
![replay tab](/misc/9.png)

This tab is used for running currently available replays of scenarios, whether they are scenarios that were just run and are therefore still saved locally, or scenarios that were saved previously and have now been loaded.

Replay key – The key of the replay you wish to run

Key list – A list of all replay keys currently available, this updates as stored scenarios get created or deleted

REPLAY – Starts the replay using the entered key

Clear Stored Replays – Clears all currently locally stored replays

Replays are either stored locally or saved to a file. Locally stored replays are saved in the temp folder, meaning they persist until the computer is shut off. Clearing the stored replays deletes all replays in the temp folder, meaning if you loaded replays from a file, and cleared stored replays, the file containing the replays still exists, however the replays are no longer in the temp folder so you will need to load them in again if you wish to replay them.

<h2> The Output tab </h2>
    
![output tab](/misc/10.png)

As its’ name suggests, the output tab has a console-like output, for each run displaying its’ result (collision or no collision), its’ seed, and its’ replay key. It also has buttons for clearing the output log, saving specific replays to a file, and loading specific replays from a file.

The “SAVE” button opens a scrollable list of checkboxes, each one referring to an available replay key.

![save](/misc/11.png)

“Save” opens another popup, this time asking under which directory you would like to save the selected scenarios. The scenarios will be saved in a file titled “LGSVL” followed by the date and time of when the scenarios were saved. Changing the name will not cause errors.

![GitHub Logo](/misc/12.png)

Back on the Output tab, the “LOAD” button allows for loading an already saved folder of scenarios. Pressing on it produces the same popup that appears when pressing “Clear Stored Replays” on the Replay tab.

![u sure?](/misc/13.png)

Upon pressing “Yes”, the same directory selection from the “SAVE” button will appear. This time, enter a folder that was created by saving scenarios. Ensure you have entered it before pressing “OK”, as shown below.

![GitHub Logo](/misc/14.png)

Pressing “OK” will load the replays from the selected folder, and they can now be used in the Replay tab.

<h2> The Params tab </h2>
    
![params tab](/misc/15.png)

The Params tab has extra functionality for creating new scenarios.

Distance between vehicles – The distance in meters that vehicles will spawn from one another. Larger vehicles, such as the School Bus and Box Truck will use double this distance. If nothing is entered the default value is 5. Using too small of a value will cause vehicles to instantiate inside each other, and fly around wildly

Spawn start and end positions – The range in meters that vehicles can spawn in relation to the EGO vehicle. For example; if start is 10 and end is 300, the closest an NPC vehicle can spawn to the EGO vehicle is 10 meters and the farthest is 300 meters. If nothing is entered the default values are 10 and 500

Vehicle list – The vehicles to be used in the next scenarios, by default all vehicles are turned on

A timeout will occur if the selected params make it impossible to run the Scenario Randomizer. For example, trying to fit 20 vehicles between 10 and 15 meters from the EGO vehicle will cause a timeout.

# Copyright and License

Copyright (c) 2018-2019 LG Electronics, Inc.

This software contains code licensed as described in LICENSE.
