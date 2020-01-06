import os
import shutil
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import Randomizer

# general GUI setup
root = tk.Tk()
root.title("LGSVL PythonAPI Scenario Randomizer")
root.resizable(width=False, height=False)
root.geometry('700x350')
program_directory = sys.path[0]
program_directory = program_directory.replace('RS_scripts', 'misc')
root.iconphoto(True, tk.PhotoImage(file=os.path.join(program_directory, "yoinkPY.png")))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TAB SETUP
tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Run")

tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text="Replay")

tab3 = ttk.Frame(tabControl)
tabControl.add(tab3, text="Output")

tab4 = ttk.Frame(tabControl)
tabControl.add(tab4, text='Params')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# These functions are mostly helper functions, which are called by various buttons and entry boxes

# validate only ints are entered in entry box, negatives not allowed
# noinspection PyUnusedLocal
def validate_int(action, index, value_if_allowed,
                 prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789':
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


# validate only ints are entered in entry box, negatives allowed
# noinspection PyUnusedLocal
def validate_int_negatives(action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        if text in '-' and value_if_allowed == '-':
            return True
        else:
            return False
    else:
        return True


# validate only ints or floats are entered in entry box, negatives not allowed
# noinspection PyUnusedLocal
def validate_float(action, index, value_if_allowed,
                   prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if action == '1':
        if text in '0123456789.':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


# add passed argument text to the output tab's scrolledtext
def addEntryContentToScrolledText(text, textwidget):
    entryValue = text
    textwidget.configure(state='normal')
    if entryValue != "":
        textwidget.insert("insert", (entryValue + "\n"))
    textwidget.configure(state='disabled')
    textwidget.see('end')


# helper function to return all the keys of all the current existing scenarios
def getKeys(file):
    if file == '':
        filename = tempfile.gettempdir() + '/or/pickleDict.txt'
    else:
        filename = file
    keys = []
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        if not lines:
            return None
        for line in lines:
            keys.append(line[-4:])
    return keys


# python doesn't like numbers with zeros in front (0001, 0002...)
# this helper function returns the number with the zeros in front by turning it to a string
def fixNumbers(number):
    numbers = [char for char in str(number)]
    strFixed = str(number)
    zeros = 4 - len(numbers)
    for x in range(zeros):
        strFixed = "0" + strFixed
    return strFixed


# helper function, allows you to pass functions to be called together, each with respective parameters
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)

    return combined_func


# the popup that appears when pressing the save button, places all existing scenarios as checkboxes, allowing you to
# select an arbitrary amount to be saved. the save button kills the popup and calls save_selected_scenarios with the
# selected checkboxes
def popup_select_scenarios(keys):
    win = tk.Toplevel()
    win.resizable(width=False, height=False)
    win.geometry('200x225')
    win.wm_title("Select scenarios to be saved")

    canvas = tk.Canvas(win, width=200, height=175)

    x = 0
    y = 0
    var_list = []
    for key in keys:
        var = tk.IntVar()
        var_list.append(var)
        cb = tk.Checkbutton(canvas, text=key, variable=var)
        canvas.create_window(y * 75, x * 25, anchor='nw', window=cb)
        if x == 6:
            y += 1
            x = 0
        else:
            x += 1

    canvas.grid(row=0, column=0)
    if len(keys) > 14:
        scroll_x = tk.Scrollbar(win, orient="horizontal", command=canvas.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")

        canvas.configure(xscrollcommand=scroll_x.set)
        canvas.configure(scrollregion=canvas.bbox("all"))

    save_button = ttk.Button(win, text="Save",
                             command=combine_funcs(win.destroy, lambda: save_selected_scenarios(var_list, keys)))
    save_button.grid(row=3, column=0, columnspan=2)


# given the list of checkboxes, check if any are selected. if none are create error popup and close the first popup. if
# any are selected, open a directory selector popup, and in the chosen directory copy the selected scenarios to the
# directory, in a file titled "LGSVL" followed by today's date and the current time. also create a new pickleDict which
# is a subset of the current pickleDict, however it only contains the relevant scenarios and not the unselected ones
def save_selected_scenarios(var_list, keys):
    values = []
    keysToBeSaved = []
    for var in var_list:
        values.append(var.get())
    if all(i == 0 for i in values):
        error_popup('Error: No scenarios selected')
    else:
        indices = [i for i, e in enumerate(values) if e == 1]
        x = 0
        for key in keys:
            if x in indices:
                keysToBeSaved.append(key)
            x += 1
        # print(keysToBeSaved)
        homedir = os.environ['HOME']
        root.directory = tk.filedialog.askdirectory(initialdir=homedir)
        if root.directory == ():
            return
        pfiles, dict_lines = get_picklefiles(keysToBeSaved, '')
        path = root.directory + '/LGSVL ' + str(
            datetime.strptime(str(datetime.now().replace(microsecond=0)), '%Y-%m-%d %H:%M:%S').strftime(
                '%d-%m-%Y %H:%M:%S'))
        try:
            os.mkdir(path)
        except OSError:
            addEntryContentToScrolledText("Creation of the directory %s failed" % path, tab3_output_scrolledtext)
        else:
            addEntryContentToScrolledText("Successfully created the directory %s " % path, tab3_output_scrolledtext)
        copy_pfiles(pfiles, '', path)
        write_pickledict(dict_lines, path)


# given a list of names of pickle files to be copied and a path for them to be copied to, copy the pickle files to the
# directory at the given path
def copy_pfiles(pfiles, fromPath, toPath):
    if fromPath == '':
        fromPath = tempfile.gettempdir() + '/or'
    if toPath == '':
        if not os.path.isdir(tempfile.gettempdir() + '/or'):
            try:
                os.mkdir(tempfile.gettempdir() + '/or')
            except OSError:
                print("Creation of the directory %s failed" % tempfile.gettempdir() + '/or')
                return
            else:
                print("Successfully created the directory %s " % tempfile.gettempdir() + '/or')
        toPath = tempfile.gettempdir() + '/or'
    directory = os.fsencode(fromPath)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        # str_filename = str(filename)
        if filename in pfiles:
            shutil.copy(fromPath + '/' + filename, toPath)
            continue
        else:
            continue


# given lines to be written in the pickleDict, and the path of where the pickle files will be stored, write a new
# pickleDict file
def write_pickledict(lines, path):
    file = path + '/pickleDict.txt'
    f = open(file, 'w')
    f.write('\n'.join(lines))
    f.close()


# given the keys of the selected scenarios, return a list of corresponding file names, and corresponding lines
# in pickleDict
def get_picklefiles(keys, path):
    if path == '':
        path = tempfile.gettempdir() + '/or/pickleDict.txt'
    else:
        path = path + '/pickleDict.txt'
    files = []
    lines_with_file = []
    with open(path, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line[-4:] in keys:
                lines_with_file.append(line)
                files.append(line.replace(line[-6:], ''))
    return files, lines_with_file


# clear the output tab
def clear_output():
    tab3_output_scrolledtext.configure(state='normal')
    tab3_output_scrolledtext.delete('1.0', 'end')
    tab3_output_scrolledtext.configure(state='disabled')


# check if any pickle files exist. if they do forward them to them select scenarios popup
def save_to_file():
    try:
        keys = getKeys('')
    except FileNotFoundError:
        error_popup('Error: no scenarios exist')
    else:
        popup_select_scenarios(keys)


# generic error message popup, print passed message with okay button to close popup
def error_popup(msg):
    pop = tk.Toplevel()
    pop.wm_title("ERROR")
    label = tk.Label(pop, text=msg)
    label.grid(row=0, column=0)
    btn = ttk.Button(pop, text="Okay", command=pop.destroy)
    btn.grid(row=1, column=0)


# are you sure popup, msg is the are you sure question, command is the function to call if yes is pressed
def are_you_sure_popup(msg, command):
    pop = tk.Toplevel()
    label = tk.Label(pop, text=msg)
    label.grid(columnspan=2)
    btn_y = tk.Button(pop, text='Yes', bg='green', command=combine_funcs(command, pop.destroy))
    btn_n = tk.Button(pop, text='No', command=pop.destroy, bg='red')
    btn_y.grid(row=1)
    btn_n.grid(row=1, column=1)
    root.wait_window(pop)


# check that all the pickle files that are stored in the pickleDict file actually exist. this is to ensure no
# shenanigans and/or tomfoolery have taken place in the files
def validate_pickles(path):
    try:
        keys = getKeys(path + '/pickleDict.txt')
    except FileNotFoundError:
        return False
    except TypeError:
        return True, None

    files, lines = get_picklefiles(keys, path)

    directory = os.fsencode(path)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename not in files:
            if filename == 'pickleDict.txt':
                continue
            else:
                return False

    return True, files
    # print(keys)


# show and format nicely the existing pickle files in the temp folder, as checkboxes
def update_available_replays(canvas):
    try:
        keys = getKeys('')
        if keys == '':
            canvas.place_forget()
        x = 0
        y = 0
        lbs = []
        for key in keys:
            lb = tk.Label(canvas, text=key)
            lbs.append(lb)
            canvas.create_window(y * 55, x * 15, anchor='nw', window=lb)
            if x == 6:
                y += 1
                x = 0
            else:
                x += 1

        canvas.place(relx=0.5, rely=0.4, anchor='center')
        if len(keys) > 14:
            scroll_x = tk.Scrollbar(tab2, orient="horizontal", command=canvas.xview)
            scroll_x.place(relx=0.5, rely=0.60, anchor='center', width=200)

            canvas.configure(xscrollcommand=scroll_x.set)
            canvas.configure(scrollregion=canvas.bbox("all"))
    except FileNotFoundError:
        canvas.place_forget()


# checks if the port that has been passed to the function as an integer is currently at this very moment being used by
# some program that is currently running on the computer on which this function is being run and returns true if the
# passed port is being used by a program on this computer and returns false if the port is not being used, you fool
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# create an array of strings of names of selected vehicles to be used in the scenario
def array_vehiclenames():
    names = ["Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]
    vars = [var_sedan.get(), var_suv.get(), var_jeep.get(), var_hatchback.get(), var_schoolbus.get(),
            var_boxtruck.get()]
    indices = [i for i, x in enumerate(vars) if x == 1]
    return [names[i] for i in indices]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# These functions are ones that are called from different buttons, and rely on the helper functions
# in the code section above

# run button function, first checks if LGSVL is running, if not it exits the function and displays an error
# otherwise, it attempts to run an instance of the Randomizer run function using the parameters input by the user
# If the vehicle doesn't exist, or there is some sort of error in the entries, an error is displayed. If the run was
# successful, run it again however many times are left according to the runs entry box
def run():
    tab1_error_label.grid_forget()
    tab1_nameerror_label.grid_forget()
    tab1_serveroffline_label.grid_forget()
    tab1_unabletospawn_label.grid_forget()

    if not is_port_in_use(8181):
        tab1_serveroffline_label.grid(columnspan=2, column=1)
        return
    try:
        msg = Randomizer.run(tab1_vehicle_name_entry.get(), variable_NPCs.get(), tab1_map_entry.get(),
                             tab1_runtime_entry.get(), tab1_seed_entry.get(), tab1_timescale_entry.get(),
                             distbetween=tab4_distbetweencars_entry.get(), cars_to_use=array_vehiclenames(),
                             spawn_start=tab4_spawnstart_entry.get(), spawn_end=tab4_spawnend_entry.get())
        addEntryContentToScrolledText(msg, tab3_output_scrolledtext)
    except ZeroDivisionError:
        tab1_nameerror_label.grid(columnspan=2, column=1)
    except ValueError:
        tab1_error_label.grid(columnspan=2, column=1)
    except TimeoutError:
        tab1_unabletospawn_label.grid(columnspan=2, column=1)
    else:
        for x in range(int(tab1_runs_entry.get()) - 1):
            msg = Randomizer.run(tab1_vehicle_name_entry.get(), variable_NPCs.get(), tab1_map_entry.get(),
                                 tab1_runtime_entry.get(), tab1_seed_entry.get(), tab1_timescale_entry.get(),
                                 distbetween=tab4_distbetweencars_entry.get(), cars_to_use=array_vehiclenames(),
                                 spawn_start=tab4_spawnstart_entry.get(), spawn_end=tab4_spawnend_entry.get())
            addEntryContentToScrolledText(msg, tab3_output_scrolledtext)
    update_available_replays(tab2_replays_canvas)


# replay button function, attempts to run an instance of Randomizer replay function with the key entered by the user
# as the passed key. if the key is invalid, an error is displayed
def Replay():
    tab2_error_label.pack_forget()
    try:
        Randomizer.replay(tab2_replaykey_entry.get())
    except ZeroDivisionError:
        tab2_error_label.pack()


# clear button function, calls are_you_sure_popup helper function with the warning and a reference to the do_Clear func
def Clear():
    are_you_sure_popup("Doing this will delete all stored scenarios\n Scenarios can be saved in the output tab\n "
                       "Continue?", do_Clear)


# clear (delete) the /or temp file, clear the output in the output tab, and update the available replays in tab2
def do_Clear():
    shutil.rmtree(tempfile.gettempdir() + '/or', ignore_errors=True)
    clear_output()
    update_available_replays(tab2_replays_canvas)


# ask user for replays file location, confirm no shenanigans in the saved replays file, then copy the files from
# folder to temp folder, which is where the other functions search for replays
def load_from_file():
    Clear()
    # True if NO was pressed on popup
    if os.path.isdir(tempfile.gettempdir() + '/or'):
        return
    homedir = os.environ['HOME']
    root.directory = tk.filedialog.askdirectory(initialdir=homedir)
    try:
        validate, files = validate_pickles(root.directory)
    except TypeError:
        return
    if not validate:
        error_popup('Error: Can not load file, something has been deleted, renamed, or moved')
    else:
        if files is None:
            return
        else:
            source = root.directory
            if not os.path.isdir(tempfile.gettempdir() + '/or'):
                try:
                    os.mkdir(tempfile.gettempdir() + '/or')
                except OSError:
                    return
            dest = tempfile.gettempdir() + '/or'
            all_files = os.listdir(source)
            for f in all_files:
                src = source + '/' + str(f)
                shutil.copy(src, dest)
            addEntryContentToScrolledText("Successfully loaded from %s " % source, tab3_output_scrolledtext)
            update_available_replays(tab2_replays_canvas)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run tab widgets
tab1_vehicle_name_label = tk.Label(tab1, text="Vehicle name")
tab1_vehicle_name_note_label = tk.Label(tab1,
                                        text="Important: Enter vehicle name exactly as it appears on LGSVL "
                                             "control site", wraplength=275)
tab1_seed_label = tk.Label(tab1, text="Seed (leave blank for random)")
tab1_NPCs_label = tk.Label(tab1, text="NPCs")
tab1_map_label = tk.Label(tab1, text="Map")
tab1_runs_label = tk.Label(tab1, text="Runs")
tab1_runtime_label = tk.Label(tab1, text="Runtime")
tab1_timescale_label = tk.Label(tab1, text="Timescale")
tab1_nameerror_label = tk.Label(tab1, text="Error: Vehicle name does not exist")
tab1_error_label = tk.Label(tab1, text="Error: Illegal value entered")
tab1_serveroffline_label = tk.Label(tab1, text='Unable to connect to LGSVL')
tab1_unabletospawn_label = tk.Label(tab1, text='Spawning timed out')
tab1_vehicle_name_entry = tk.Entry(tab1)
OPTIONS_NPCs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                29, 30]
variable_NPCs = tk.StringVar(root)
variable_NPCs.set(OPTIONS_NPCs[19])
tab1_NPCs_entry = tk.OptionMenu(tab1, variable_NPCs, *OPTIONS_NPCs)
tab1_map_entry = tk.Entry(tab1)
tab1_map_entry.insert(0, "BorregasAve")
vcmd = (root.register(validate_int),
        '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
vcmd2 = (root.register(validate_int_negatives),
         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
vcmd3 = (root.register(validate_float),
         '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
tab1_seed_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd2)
tab1_runs_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd)
tab1_runtime_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd3)
tab1_timescale_entry = tk.Entry(tab1, validate='key', validatecommand=vcmd3)
tab1_timescale_entry.insert(0, "1")
tab1_run_button = tk.Button(tab1, text="RUN", command=run)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run tab widget placement
tab1_vehicle_name_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
tab1_vehicle_name_entry.grid(row=0, column=1, pady=15, sticky="w")

tab1_vehicle_name_note_label.grid(row=1, columnspan=2, padx=15, pady=15)

tab1_seed_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")
tab1_seed_entry.grid(row=2, column=1, pady=15, sticky="w")

tab1_NPCs_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")
tab1_NPCs_entry.grid(row=3, column=1, pady=15, sticky="w")

tab1_map_label.grid(row=0, column=2, padx=15, pady=15, sticky="e")
tab1_map_entry.grid(row=0, column=3, padx=15, pady=15, sticky="w")

tab1_runs_label.grid(row=1, column=2, padx=15, pady=15, sticky="e")
tab1_runs_entry.grid(row=1, column=3, padx=15, pady=15, sticky="w")

tab1_runtime_label.grid(row=2, column=2, padx=15, pady=15, sticky="e")
tab1_runtime_entry.grid(row=2, column=3, padx=15, pady=15, sticky="w")

tab1_timescale_label.grid(row=3, column=2, padx=15, pady=15, sticky="e")
tab1_timescale_entry.grid(row=3, column=3, padx=15, pady=15, sticky="w")

tab1_run_button.grid(row=4, columnspan=2, column=1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Replay tab widgets + placement
tab2_replaykey_label = tk.Label(tab2, text="Replay key")
tab2_replaykey_entry = tk.Entry(tab2, validate='key', validatecommand=vcmd, justify='center')
tab2_error_label = tk.Label(tab2, text="Error: Replay key not found")
tab2_replaykey_button = tk.Button(tab2, text="REPLAY", command=Replay)
tab2_clearreplays_button = tk.Button(tab2, text="Clear Stored Replays", command=Clear)

tab2_replaykey_label.config(anchor='center')
tab2_error_label.config(anchor='n')
tab2_replaykey_label.pack()
tab2_replaykey_entry.pack()
tab2_replaykey_button.place(relx=0.5, rely=0.75, anchor='center')
tab2_clearreplays_button.place(relx=0.5, rely=0.95, anchor='s')

tab2_replays_canvas = tk.Canvas(tab2, width=175, height=125)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Output tab widgets + placement
tab3_output_frame = tk.Frame(tab3)
tab3_output_scrolledtext = ScrolledText(tab3_output_frame, font=("Helvetica", 11), width=70, height=20,
                                        state='disabled')
tab3_clear_button = tk.Button(tab3, text="CLEAR", command=clear_output)
tab3_save_button = tk.Button(tab3, text="SAVE", padx=15, command=save_to_file)
tab3_load_button = tk.Button(tab3, text="LOAD", padx=15, command=load_from_file)
tab3_output_frame.pack(side='right')
tab3_output_scrolledtext.pack()
tab3_clear_button.place(relx=0.135, rely=0.10, anchor='e')
tab3_save_button.place(relx=0.135, rely=0.20, anchor='e')
tab3_load_button.place(relx=0.135, rely=0.30, anchor='e')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Param tab widgets + placement
tab4_distbetweencars_label = tk.Label(tab4, text='Distance between vehicles')
tab4_distbetweencars_entry = tk.Entry(tab4, validate='key', validatecommand=vcmd3)
tab4_spawnstart_label = tk.Label(tab4, text='Spawn start position')
tab4_spawnstart_entry = tk.Entry(tab4, validate='key', validatecommand=vcmd3)
tab4_spawnend_label = tk.Label(tab4, text='Spawn end position')
tab4_spawnend_entry = tk.Entry(tab4, validate='key', validatecommand=vcmd3)

tab4_distbetweencars_label.grid(row=1, padx=5, pady=15)
tab4_distbetweencars_entry.grid(row=1, column=1, padx=5, pady=15)
tab4_spawnstart_label.grid(row=2, padx=5, pady=15)
tab4_spawnstart_entry.grid(row=2, column=1, padx=5, pady=15)
tab4_spawnend_label.grid(row=3, padx=5, pady=15)
tab4_spawnend_entry.grid(row=3, column=1, padx=5, pady=15)

# Car checkboxes:
# names = ["Sedan", "SUV", "Jeep", "Hatchback", "SchoolBus", "BoxTruck"]
var_sedan = tk.IntVar(value=1)
var_suv = tk.IntVar(value=1)
var_jeep = tk.IntVar(value=1)
var_hatchback = tk.IntVar(value=1)
var_schoolbus = tk.IntVar(value=1)
var_boxtruck = tk.IntVar(value=1)
tab4_cb_frame = tk.Frame(tab4)
tab4_cb_frame.grid(rowspan=3, row=1, column=2)
tab4_sedan_cb = tk.Checkbutton(tab4_cb_frame, text="Sedan", variable=var_sedan).grid(row=1, column=3, sticky='W',
                                                                                     padx=50)
tab4_suv_cb = tk.Checkbutton(tab4_cb_frame, text="SUV", variable=var_suv).grid(row=2, column=3, sticky='W', padx=50)
tab4_jeep_cb = tk.Checkbutton(tab4_cb_frame, text="Jeep", variable=var_jeep).grid(row=3, column=3, sticky='W', padx=50)
tab4_hatchback_cb = tk.Checkbutton(tab4_cb_frame, text="Hatchback", variable=var_hatchback).grid(row=4, column=3,
                                                                                                 sticky='W', padx=50)
tab4_schoolbus_cb = tk.Checkbutton(tab4_cb_frame, text="School Bus", variable=var_schoolbus).grid(row=5, column=3,
                                                                                                  sticky='W', padx=50)
tab4_boxtruck_cb = tk.Checkbutton(tab4_cb_frame, text="Box Truck", variable=var_boxtruck).grid(row=6, column=3,
                                                                                               sticky='W', padx=50)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# set tabs, update the displayed available replays (in the temp folder), and then run the GUI
tabControl.pack(expan=1, fill="both")
update_available_replays(tab2_replays_canvas)
root.mainloop()
