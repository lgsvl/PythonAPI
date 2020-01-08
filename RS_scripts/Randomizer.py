#!/usr/bin/env python3
import errno
import math
import os
import pickle
import random
import re
import tempfile
import time
import lgsvl
import signal

# output message, will be referenced later
endMsg = 'default'

# run function, receives vehicle name, amount of NPCs, map name, runtime, seed, and timescale parameters, then creates
# a random scenario using these variables
def run(VN, NPC, MAP, RT, SD, TS, distbetween=None, spawn_start=None, spawn_end=None, cars_to_use=None,
        rain=None, fog=None, wetness=None, timeofday=None, fixed=None):
    # Main spawning script
    # Initial simulator setup
    sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)

    # timeout handler
    def handler(signum, frame):
        raise TimeoutError

    # initialize variables
    try:
        vehicleName = VN
        NPCCount = int(NPC)
        map = MAP
        runtime = float(RT)
        timescale = float(TS)
    except ValueError:
        sim.stop()
        sim.close()
        raise ValueError
    if SD == '':
        seed = random.randint(-2147483649, 2147483647)
    else:
        seed = int(SD)

    if sim.current_scene == map:
        sim.reset()
    else:
        # Seed (optional) is an Integer (-2,147,483,648 - 2,147,483,647) that determines the "random" behavior of the
        # NPC vehicles and rain effects.
        sim.load(scene=map, seed=seed)

    # Selected cars to use in the scenario
    if cars_to_use is None or cars_to_use == '':
        cars_to_use = ["Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]

    # Distance between vehicles (doubled for long vehicles)
    if distbetween is None or distbetween == '':
        distbetween = 5.0
    else:
        distbetween = float(distbetween)

    # Minimum and maximum distance for NPCs to be spawned from EGO vehicle
    if spawn_start is None or spawn_start == '':
        spawn_start = 10.0
    else:
        spawn_start = float(spawn_start)

    if spawn_end is None or spawn_end == '':
        spawn_end = 500.0
    else:
        spawn_end = float(spawn_end)

    if rain == '-0.01':
        rain = round(random.uniform(0, 1),2)
    else:
        rain = float(rain)

    if fog == '-0.01':
        fog = round(random.uniform(0, 1),2)
    else:
        fog = float(fog)

    if wetness == '-0.01':
        wetness = round(random.uniform(0, 1),2)
    else:
        wetness = float(wetness)

    if timeofday == '-0.01':
        timeofday = round(random.uniform(0, 24),2)
    else:
        timeofday = float(timeofday)

    if fixed == 1:
        fixed = True
    else:
        fixed = False

    # Handling weather and time
    sim.weather = lgsvl.WeatherState(rain=rain, fog=fog, wetness=wetness)
    sim.set_time_of_day(timeofday, fixed=fixed)

    NPCNameList = []

    # Bigger NPC vehicles (important later when spawning)
    bigLads = ["SchoolBus", "BoxTruck"]
    # List of transforms representing good spawn points
    spawns = sim.get_spawn()

    # Creates new agent state, makes it's transform equal to the first good spawn point.
    state = lgsvl.AgentState()
    state.transform = spawns[0]

    try:
        a = sim.add_agent(vehicleName, lgsvl.AgentType.EGO, state)
    except Exception:
        signal.alarm(0)
        sim.stop()
        sim.close()
        raise ZeroDivisionError
    sensors = a.get_sensors()
    # Lexus2016RXHybrid (Autoware) OR CAR [<lgsvl.sensor.GpsSensor object at 0x7ff1055e1828>, <lgsvl.sensor.ImuSensor
    # object at 0x7ff1055e1860>, <lgsvl.sensor.LidarSensor object at 0x7ff1055e1898>, <lgsvl.sensor.CameraSensor object
    # at 0x7ff1055e18d0>] An EGO will not connect to a bridge unless commanded to

    print("Bridge connected:", a.bridge_connected)

    # The EGO is now looking for a bridge at the specified IP and port
    a.connect_bridge("192.168.43.64", 9090)

    print("Waiting for connection...")
    while not a.bridge_connected:
        time.sleep(1)

    print("Bridge connected:", a.bridge_connected)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(15 + int(runtime))

    sx = spawns[0].position.x
    sy = spawns[0].position.y
    sz = spawns[0].position.z
    states = [state]
    statesToReplay = []
    AgentList = {
        a: "Ego"
    }

    collided = False

    # on collision callback, gets called when the EGO vehicle collides with another agent (NPC or pedestrian)
    # if the EGO vehicle collides with another agent, end the simulation, output the data to output.txt
    def on_collision(agent1, agent2, contact):
        global collided
        collided = True
        name1 = AgentList[agent1]
        name2 = AgentList[agent2] if agent2 is not None else "OBSTACLE"
        Pkey = addPickled()
        msg = "{} collided with {} at {} \n Seed: {}\n Replay Key: {}\n \n".format(name1, name2, contact, seed, Pkey)
        output = "{} collided with {} at {}".format(name1, name2, contact)
        print(output)
        print("Killing sim...")
        sim.stop()
        sim.close()
        global endMsg
        endMsg = msg

    # The above on_collision function needs to be added to the callback list of each vehicle
    a.on_collision(on_collision)

    # firstly checks if /tmp/or already exists (from previous runs of this script) if it doesn't, create it. the
    # pickle module can take a variable and save it to a file, in order to be read by another script at a later
    # point. the file that the pickle is saved in is unreadable by users. this function checks the next available
    # pickle file name (pickle1, pickle2...) and then dumps a list to said file, where the first element of the list
    # is a string of all the states of all the NPC vehicles in this run of the simulation, and the second element of
    # the list is their respective vehicle names(types). For ease of use, each pickled file is assigned a key,
    # going from 0001 - 9999. these keys are a sort of reference to a pickled file, and the list of keys and their
    # respective files can be seen in /tmp/or/pickleDict.txt
    def addPickled():
        i = 1
        path = tempfile.gettempdir() + "/or/pickle"
        filename = tempfile.gettempdir() + "/or/pickleDict.txt"
        is_first = False
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
                is_first = True
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        while True:
            testPath = path + str(i)
            if not os.path.isfile(testPath):
                f = open(testPath, "wb")
                break
            else:
                i = i + 1
        info = "{" + vehicleName + "} {" + map + "} {" + str(seed) + "} {" + str(runtime) + "} {" + str(timescale) + "}"
        weather = "{" + str(rain) + "} {" + str(fog) + "} {" + str(wetness) + "} {" + str(timeofday) + "} {" + str(fixed) + "}"
        stuffToPickle = [statesToReplay, NPCNameList, info, weather]
        pickle.dump(stuffToPickle, f)
        f.close()
        f = open(filename, "a")
        index = "pickle" + str(i)
        Pkey = getNextKey()
        dict = "{}: {}".format(index, Pkey) if is_first else "\n{}: {}".format(index, Pkey)
        f.write(dict)
        f.close()
        return Pkey

    # helper function for addPickled(), this function returns the next available key to use as a
    # referencer to a pickled file (0001, 0002, 0003...)
    def getNextKey():
        filename = tempfile.gettempdir() + "/or/pickleDict.txt"
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            if not lines:
                return "0001"
        nums = []
        for line in lines:
            nums.append(int(line[-4:]))
        key = int(fixNumbers(min(nums) + 1))
        while True:
            if key not in nums:
                break
            key += 1
        return fixNumbers(key)

    # python doesn't like numbers with zeros in front (0001, 0002...)
    # this helper function returns the number with the zeros in front by turning it to a string
    def fixNumbers(number):
        numbers = [char for char in str(number)]
        strFixed = str(number)
        zeros = 4 - len(numbers)
        for x in range(zeros):
            strFixed = "0" + strFixed
        return strFixed

    # Function that returns true if two given agent states are at least dist away from each other on the x axis (forward
    # axis), also specifically checks if one of them is a larger vehicle, and if so it sets the distance between them
    # accordingly to avoid clipping
    def checkValidPos(state1, state2, dist, biglad):
        if biglad:
            return abs(dot(state1.transform.position - state2.transform.position,
                           lgsvl.utils.transform_to_forward(state1))) > dist * 2.5
        else:
            return abs(
                dot(state1.transform.position - state2.transform.position,
                    lgsvl.utils.transform_to_forward(state1))) > dist

    # Dot product function
    def dot(vector1, vector2):
        return (vector1.x * vector2.x) + (vector1.y * vector2.y) + (vector1.z * vector2.z)

    # Add new car after checking it's validity by looping through all the cars that have already
    # spawned and using the checkValidPos helper function. if position is invalid, moves the car
    # back by 5 meters and tries again (position being off the map will be handled later)
    def addPos(state, states, biglad):
        restart = True
        finishCount = 0
        count = 0
        while restart:
            for i in range(len(states)):
                if NPCNameList[i] in bigLads:
                    biglad = True
                if not (checkValidPos(state, states[i], distbetween, biglad)):
                    finishCount = 0
                    state.transform.position -= distbetween * lgsvl.utils.transform_to_forward(state)
                    break
                else:
                    finishCount += 1
                if finishCount == len(states):
                    restart = False
                    return state
            count += 1
            if count == 10:
                break

    # helper function to check if a passed state is off the map, returns true if it is on the map
    # the function uses the map_point_on_lane function provided by lgsvl to create a point on the
    # road using the position passed into the function, then compares the created position and the
    # actual position to determine whether or not the position given is on a road or off the map
    def checkOffMap(stateC):
        if stateC is None:
            return False
        point = stateC.transform.position
        newState = lgsvl.AgentState
        newState.transform = sim.map_point_on_lane(point)
        return abs((newState.transform.position.x - stateC.transform.position.x)) + abs(
            (newState.transform.position.y - stateC.transform.position.y)) + abs(
            (newState.transform.position.z - stateC.transform.position.z)) < 3.0

    # Distance between two transform.positions
    def dis2Positions(pos1, pos2):
        return math.sqrt((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2 + (pos1.z - pos2.z) ** 2)

    # Function to create a new random position between spawn_start and spawn_end away from the EGO vehicle, and select a
    # random vehicle type from the list of vehicle types
    def randPos():
        name = random.choice(cars_to_use)

        # Creates a random point around the EGO
        angle = random.uniform(0.0, -1 * math.pi)
        dist = random.uniform(spawn_start, spawn_end)

        point = lgsvl.Vector(sx + dist * math.cos(angle), sy, sz + dist * math.sin(angle))

        # Creates an NPC on a lane that is closest to the random point
        stateF = lgsvl.AgentState()
        stateF.transform = sim.map_point_on_lane(point)
        return stateF, name

    # Main spawning function, uses the addPos function to create a new valid random position.
    # if the new position is off the map, it nullifies the position and adds 1 to the spawning loop indexing variable
    # if the new position is on the map, it is verified as a valid position and is spawned in the simulation
    def spawn(state, NPCsToSpawn):
        state, name = randPos()
        NPCNameList.append(name)
        if name in bigLads:
            state = addPos(state, states, True)
        else:
            state = addPos(state, states, False)
        if not checkOffMap(state):
            state = None
            NPCsToSpawn += 1
            del NPCNameList[-1]
        if state is not None:
            states.append(state)
            statesToReplay.append(state)
            npc = sim.add_agent(name, lgsvl.AgentType.NPC, state)
            AgentList[npc] = name
            npc.follow_closest_lane(True, 11.1)
        return NPCsToSpawn

    # Function to send passed npc and corresponding state off edge of map (currently useless)
    def driveOffEdge(npc, state):
        waypoints = [
            lgsvl.DriveWaypoint(state.transform.position + (lgsvl.utils.transform_to_forward(state.transform) * 3), 5,
                                lgsvl.Vector(0, 0, 0), 0, False, 0)]
        npc.follow(waypoints, loop=False)

    # true if close enough to edge to kill self, false if not (currently useless)
    def shouldDie(state):
        testPos = state.transform.position + (lgsvl.utils.transform_to_forward(state.transform) * 3)
        testState = lgsvl.AgentState
        testState.transform = state.transform
        testState.transform.position = testPos
        testState.transform = sim.map_point_on_lane(testPos)
        return dis2Positions(testPos, testState.transform.position) > 3.0

    # main function, has the spawning loop and then starts the simulation after all vehicles have been spawned, and also
    # outputs to output.txt in the case of no collisions occurring
    def start(NPCsToSpawn):
        x = 0
        while x < NPCsToSpawn:
            NPCsToSpawn = spawn(state, NPCsToSpawn)
            x += 1

        sim.run(time_limit=runtime, time_scale=timescale)
        if not collided:
            Pkey = addPickled()
            msg = "Simulation ended with no collisions \n Seed: {}\n Replay Key: {}\n \n".format(seed, Pkey)
            sim.stop()
            sim.close()
            global endMsg
            endMsg = msg

    start(NPCCount)
    signal.alarm(0)
    return endMsg
    pass


# replay function, recieves replay key as parameter
def replay(key):
    sim = lgsvl.Simulator(os.environ.get("SIMULATOR_HOST", "127.0.0.1"), 8181)

    # this script handles the replay feature. it is initialized in the same way as hagrala.py, however the spawning is
    # not done randomly and is instead done using a list of states of NPC vehicles from a given run of hagrala.py
    # this script relies on pickle and the files placed in /tmp/or by hagrala.py

    # given a key, match that key with its corresponding pickle file using the pickleDict text file,
    # and return the pickle file. if no such key exists print not found
    def getPickled(key):
        filename = tempfile.gettempdir() + "/or/pickleDict.txt"
        try:
            f = open(filename, "r")
        except FileNotFoundError:
            return FileNotFoundError
        stringList = f.read()
        f.close()
        pickleList = stringList.splitlines()
        for i in pickleList:
            Ckey = i[-4:]
            if Ckey == key:
                return i.split(":")[0]
        return 0 / 0

    # helper function; given a string, return the bit between firstShit and secondShit
    # for example given the string "abcd1234", if firstShit is abc and secondShit is 34, return is "d12"
    def spliceBetween(str, firstShit, secondShit):
        try:
            found = re.search(firstShit + '(.+?)' + secondShit, str).group(1)
        except AttributeError:
            return None
        return found

    # function that splits the simulators settings into ints and strings respectively
    def splitInfo(info):
        info = info[1:-1].split('} {')
        vn, map, seed, runtime, timescale = info
        return str(vn), str(map), int(seed), float(runtime), float(timescale)

    # function that splits the simulators weather settings into floats
    def splitWeather(weather):
        weather = weather[1:-1].split('} {')
        rain, fog, wetness, timeofday, fixed = weather
        return float(rain), float(fog), float(wetness), float(timeofday), bool(fixed)

    # gets the string of states, the list of names, and the replay info from the pickle file using the key inputted
    # by the user
    PickleToUnpickle = getPickled(key)
    if PickleToUnpickle == FileNotFoundError:
        return 0 / 0
    unpickled = pickle.load(open(tempfile.gettempdir() + "/or/" + PickleToUnpickle, "rb"))
    transformString = str(unpickled[0])
    names = unpickled[1]
    info = unpickled[2]
    weather = unpickled[3]
    vehicleName, map, seed, runtime, timescale = splitInfo(info)
    rain, fog, wetness, timeofday, fixed = splitWeather(weather)

    if sim.current_scene == map:
        sim.reset()
    else:
        # Seed (optional) is an Integer (-2,147,483,648 - 2,147,483,647) that determines the "random" behavior of the
        # NPC vehicles and rain effects.
        sim.load(scene=map, seed=seed)

    # Handling weather and time
    sim.weather = lgsvl.WeatherState(rain=rain, fog=fog, wetness=wetness)
    sim.set_time_of_day(timeofday, fixed=fixed)

    # List of transforms representing good spawn points
    spawns = sim.get_spawn()
    # Creates new agent state, makes it's transform equal to the first good spawn point.
    state = lgsvl.AgentState()
    state.transform = spawns[0]
    a = sim.add_agent(vehicleName, lgsvl.AgentType.EGO, state)
    sensors = a.get_sensors()
    # Lexus2016RXHybrid (Autoware) OR CAR [<lgsvl.sensor.GpsSensor object at 0x7ff1055e1828>, <lgsvl.sensor.ImuSensor
    # object at 0x7ff1055e1860>, <lgsvl.sensor.LidarSensor object at 0x7ff1055e1898>, <lgsvl.sensor.CameraSensor object
    # at 0x7ff1055e18d0>] An EGO will not connect to a bridge unless commanded to

    print("Bridge connected:", a.bridge_connected)

    # The EGO is now looking for a bridge at the specified IP and port
    a.connect_bridge("192.168.43.64", 9090)

    print("Waiting for connection...")
    sensors = a.get_sensors()
    while not a.bridge_connected:
        time.sleep(1)

    print("Bridge connected: ", a.bridge_connected)

    AgentList = {
        a: "Ego"
    }

    # on_collision is still used in this script, however it is not output to a text file and instead printed in the
    # terminal
    def on_collision(agent1, agent2, contact):
        global collided
        collided = True
        name1 = AgentList[agent1]
        name2 = AgentList[agent2] if agent2 is not None else "OBSTACLE"
        print("{} collided with {} at {} \n".format(name1, name2, contact))
        sim.stop()
        sim.close()

    collided = False

    # The above on_collision function needs to be added to the callback list of each vehicle
    a.on_collision(on_collision)

    # this function receives the state string and splits it into position and rotation, and creates and returns a new
    # state with these position and rotation values. it essentially turns the big string of states into actual state
    # objects. it is very hardcoded and i am sorry, but jesus will judge me when it is my time
    def strToTransform(str):
        state = lgsvl.AgentState()
        initialSplice = spliceBetween(str, '', 'Vector')
        str = str.replace(initialSplice, '')
        posString = spliceBetween(str, '', ', rotation')
        str = str.replace(posString, '')
        splice = spliceBetween(str, '', 'Vector')
        str = str.replace(splice, '')
        rotString = spliceBetween(str, '', 'velocity')
        rotString = rotString[:-5]
        px, py, pz = strToVector(posString)
        rx, ry, rz = strToVector(rotString)
        position = lgsvl.Vector(px, py, pz)
        rotation = lgsvl.Vector(rx, ry, rz)
        state.transform.position = position
        state.transform.rotation = rotation
        return state

    # helper function for strToTransform, given a Vector as a string, return the actual x y and z as floats
    def strToVector(str):
        str = str.replace('Vector', '')
        str = str.replace('(', '')
        str = str.replace(')', '')
        str = '[' + str + ']'
        list = str.strip('][').split(', ')
        x = float(list[0])
        y = float(list[1])
        z = float(list[2])
        return x, y, z

    # helper function to return the first state as a string from the list of states as a string
    def getFirstState(str):
        try:
            found = spliceBetween(str, '{', '}')
        except AttributeError:
            return None
        if found is None:
            return None
        found = "{" + found + "}"
        return found

    # main looping function
    def start(transformString):
        i = 0
        # spawning loop
        while True:
            stateStr = getFirstState(transformString)
            if stateStr is None:
                break
            transformString = transformString.replace(stateStr, '')
            state = strToTransform(stateStr)
            name = names[i]
            npc = sim.add_agent(name, lgsvl.AgentType.NPC, state)
            npc.follow_closest_lane(True, 11.1)
            i += 1
        sim.run(time_limit=runtime, time_scale=timescale)
        if not collided:
            print("Simulation ended with no collisions")
            sim.stop()
            sim.close()

    start(transformString)
    pass


# if this function is not called from the GUI for the purpose of debugging
if __name__ == "__main__":
    ans = input("run or replay\n")
    if not ans == "run" and not ans == "replay":
        print("invalid command")
    if ans is "run":
        run("OR CAR", 20, "BorregasAve", 3, '', 1)
    elif ans == 'replay':
        try:
            replay('0001')
        except ZeroDivisionError:
            print('no scenarios exist')
