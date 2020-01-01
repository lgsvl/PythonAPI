# import datetime
# import queue
# import logging
# import signal
# import time
# import threading
# import tkinter as tk
# from tkinter.scrolledtext import ScrolledText
# from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W
#
#
# logger = logging.getLogger(__name__)
#
# class QueueHandler(logging.Handler): """Class to send logging records to a queue It can be used from different
# threads The ConsoleUi class polls this queue to display records in a ScrolledText widget """ # Example from Moshe
# Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06 # (
# https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget) is not thread safe! # See
# https://stackoverflow.com/questions/43909849/tkinter-python-crashes-on-new-thread-trying-to-log-on-main-thread
#
#     def __init__(self, log_queue):
#         super().__init__()
#         self.log_queue = log_queue
#
#     def emit(self, record):
#         self.log_queue.put(record)
#
#
# class ConsoleUi:
#     """Poll messages from a logging queue and display them in a scrolled text widget"""
#
#     def __init__(self, frame):
#         self.frame = frame
#         # Create a ScrolledText wdiget
#         self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
#         self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
#         self.scrolled_text.configure(font='TkFixedFont')
#         self.scrolled_text.tag_config('INFO', foreground='black')
#         self.scrolled_text.tag_config('DEBUG', foreground='gray')
#         self.scrolled_text.tag_config('WARNING', foreground='orange')
#         self.scrolled_text.tag_config('ERROR', foreground='red')
#         self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
#         # Create a logging handler using a queue
#         self.log_queue = queue.Queue()
#         self.queue_handler = QueueHandler(self.log_queue)
#         formatter = logging.Formatter('%(asctime)s: %(message)s')
#         self.queue_handler.setFormatter(formatter)
#         logger.addHandler(self.queue_handler)
#         # Start polling messages from the queue
#         self.frame.after(100, self.poll_log_queue)
#
#     def display(self, record):
#         msg = self.queue_handler.format(record)
#         self.scrolled_text.configure(state='normal')
#         self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
#         self.scrolled_text.configure(state='disabled')
#         # Autoscroll to the bottom
#         self.scrolled_text.yview(tk.END)
#
#     def poll_log_queue(self):
#         # Check every 100ms if there is a new message in the queue to display
#         while True:
#             try:
#                 record = self.log_queue.get(block=False)
#             except queue.Empty:
#                 break
#             else:
#                 self.display(record)
#         self.frame.after(100, self.poll_log_queue)
#
# class App:
#
#     def __init__(self, root):
#         self.root = root
#         root.title('Logging Handler')
#         root.columnconfigure(0, weight=1)
#         root.rowconfigure(0, weight=1)
#         # Create the panes and frames
#         vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
#         vertical_pane.grid(row=0, column=0, sticky="nsew")
#         horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
#         vertical_pane.add(horizontal_pane)
#         console_frame = ttk.Labelframe(horizontal_pane, text="Console")
#         console_frame.columnconfigure(0, weight=1)
#         console_frame.rowconfigure(0, weight=1)
#         horizontal_pane.add(console_frame, weight=1)
#         # Initialize all frames
#         self.console = ConsoleUi(console_frame)
#         self.root.protocol('WM_DELETE_WINDOW', self.quit)
#         self.root.bind('<Control-q>', self.quit)
#         signal.signal(signal.SIGINT, self.quit)
#
#     def quit(self, *args):
#         self.root.destroy()
#
#
# def main():
#     logging.basicConfig(level=logging.DEBUG)
#     root = tk.Tk()
#     app = App(root)
#     app.root.mainloop()
#
#
# if __name__ == '__main__':
#     main()

# import tkinter as tk
#
# def cbc(id, tex):
#     return lambda : callback(id, tex)
#
# def callback(id, tex):
#     s = 'At {} f is {}\n'.format(id, id**id/0.987)
#     tex.insert(tk.END, s)
#     tex.see(tk.END)             # Scroll if necessary
#
# top = tk.Tk()
# tex = tk.Text(master=top)
# tex.pack(side=tk.RIGHT)
# bop = tk.Frame()
# bop.pack(side=tk.LEFT)
# for k in range(1,10):
#     tv = 'Say {}'.format(k)
#     b = tk.Button(bop, text=tv, command=cbc(k, tex))
#     b.pack()
#
# tk.Button(bop, text='Exit', command=top.destroy).pack()
# top.mainloop()
#
# ''' tk_scrolledtext101.py
# explore Tkinter's ScrolledText widget
# inside the edit_space use
# ctrl+c to copy, ctrl+x to cut selected text,
# ctrl+v to paste, and ctrl+a to select all
# uses the same methods as the Text() widget
# '''
# try:
#     # for Python2
#     import Tkinter as tk
#     import ScrolledText as tkst
# except ImportError:
#     # for Python3
#     import tkinter as tk
#     import tkinter.scrolledtext as tkst
# root = tk.Tk()
# root.title("ScrolledText")
# frame = tk.Frame(root, bg='brown')
# frame.pack(fill='both', expand='yes')
# edit_space = tkst.ScrolledText(
#     master = frame,
#     wrap   = 'word',  # wrap text at full words only
#     width  = 25,      # characters
#     height = 10,      # text lines
#     bg='beige'        # background color of edit area
# )
# # the padx/pady space will form a frame
# edit_space.pack(fill='both', expand=True, padx=8, pady=8)
# mytext = '''\
# Man who drive like hell, bound to get there.
# Man who run in front of car, get tired.
# Man who run behind car, get exhausted.
# The Internet: where men are men, women are men, and children are FBI agents.
# '''
# edit_space.insert('insert', mytext)
# root.mainloop()
# # optiona info
# #help(tkst.ScrolledText)

# from tkinter import filedialog
# from tkinter import *
#
# root = Tk() root.filename =  filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = ((
# "text files","*.txt"),("all files","*.*"))) print (root.filename)

# import tkinter as tk
# from tkinter import ttk
# from tkinter.messagebox import showinfo
# #
# #
# # def popup_bonus():
# #     win = tk.Toplevel()
# #     win.wm_title("Window")
# #
# #     l = tk.Label(win, text="Input")
# #     l.grid(row=0, column=0)
# #
# #     b = ttk.Button(win, text="Okay", command=win.destroy)
# #     b.grid(row=1, column=0)
# #
# #
# # def popup_showinfo():
# #     showinfo("Window", "Hello World!")
# #
# #
# # class Application(ttk.Frame):
# #
# #     def __init__(self, master):
# #         ttk.Frame.__init__(self, master)
# #         self.pack()
# #
# #         self.button_bonus = ttk.Button(self, text="Bonuses", command=popup_bonus)
# #         self.button_bonus.pack()
# #
# #         self.button_showinfo = ttk.Button(self, text="Show Info", command=popup_showinfo)
# #         self.button_showinfo.pack()
# #
# #
# # root = tk.Tk()
# #
# # app = Application(root)
# #
# # root.mainloop()
#
# def checkboxes_container(self):
#     # Checkboxes frame
#     self.checkboxes_frame = \
#         tk.Frame(self,
#                  height=450,
#                  bg='red', bd=0,
#                  highlightthickness=0)
#     # Canvas widget to add scroll to the checkboxes holder
#     self.canvas = \
#         tk.Canvas(self.checkboxes_frame,
#                   bg='blue', bd=0,
#                   highlightthickness=0)
#     # Canvas sizer
#     canvas_sizer = tk.Frame(self.canvas, height=350,
#                             bg='#444444', bd=0,
#                             highlightthickness=0)
#     canvas_sizer.pack(side=tk.LEFT)
#     # Checkboxes holder
#     self.checkbox_pane = \
#         tk.Frame(self.canvas,
#                  bg='#444444', bd=0,
#                  highlightthickness=0)
#     self.checkbox_pane.grid_propagate(False)
#     # Scrollbar for checkbox pane
#     self.scrollbar = tk.Scrollbar(self.checkboxes_frame,
#                                   bg='grey', bd=0,
#                                   activebackground='#A3A3A3',
#                                   troughcolor='#444444',
#                                   width=16,
#                                   orient=tk.VERTICAL)
#
#     self.canvas.create_window(0, 0, window=self.checkbox_pane)
#     # Grid holder
#     self.checkboxes_frame.grid(row=1, column=0, sticky=tk.W+tk.E)
#     # Grid widgets to the holder
#     self.canvas.pack(expand=True, side=tk.LEFT, fill=tk.BOTH)
#     self.checkbox_pane.pack(expand=True, fill=tk.BOTH)
#     self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#     self.scrollbar.config(command=self.canvas.yview)
#     self.canvas.config(yscrollcommand=self.scrollbar.set,
#                        scrollregion=
#                        self.canvas.bbox('all'))
#
# class ScrollableFrame(tk.Frame):
#     def __init__(self, master, **kwargs):
#         tk.Frame.__init__(self, master, kwargs)
#
#         # create a canvas object and a vertical scrollbar for scrolling it
#         self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
#         self.vscrollbar.pack(side='right', fill="y",  expand="false")
#         self.canvas = tk.Canvas(self,
#                                 bg='#444444', bd=0,
#                                 height=350,
#                                 highlightthickness=0,
#                                 yscrollcommand=self.vscrollbar.set)
#         self.canvas.pack(side="left", fill="both", expand="true")
#         self.vscrollbar.config(command=self.canvas.yview)
#
#         # reset the view
#         self.canvas.xview_moveto(0)
#         self.canvas.yview_moveto(0)
#
#         # create a frame inside the canvas which will be scrolled with it
#         self.interior = tk.Frame(self.canvas, kwargs)
#         self.canvas.create_window(0, 0, window=self.interior, anchor="nw")
#
#
# class Application(tk.Frame):
#     # ...
#
#     def checkboxes_container(self):
#         self.checkbox_pane = ScrollableFrame(self,
#                                              bg='#444444')
#         self.checkbox_pane.grid(row=1, column=0,
#                                 columnspan=3,
#                                 sticky='nwes')
#
# if __name__ == '__main__':
#     root = tk.Tk()
#     checkbox_pane = ScrollableFrame(root, bg='#444444')
#     checkbox_pane.pack(expand="true", fill="both")
#
#     def button_callback():
#         for x in range(1,20):
#             tk.Checkbutton(checkbox_pane.interior, text="hello world! %s" % x).grid(row=x, column=0)
#
#     btn_checkbox = tk.Button(checkbox_pane.interior, text="Click Me!", command=button_callback)
#     btn_checkbox.grid(row=0, column=0)
#     root.mainloop()

import tkinter as tk

# root=tk.Tk()
#
# vscrollbar = tk.Scrollbar(root, orient='horizontal')
#
# c= tk.Canvas(root,background = "#D2D2D2",xscrollcommand=vscrollbar.set)
#
# vscrollbar.config(command=c.yview)
# vscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
#
# f=tk.Frame(c) #Create the frame which will hold the widgets
#
# c.pack(side="top", fill="both", expand=True)
#
# #Updated the window creation
# c.create_window(0,0,window=f, anchor='nw')
#
# #Added more content here to activate the scroll
# for i in range(50):
#     tk.Label(f,wraplength=350 ,text=r"Det er en kendsgerning, at man bliver distraheret af læsbart indhold på en side, når man betragter dens websider, som stadig er på udviklingsstadiet. Der har været et utal af websider, som stadig er på udviklingsstadiet. Der har været et utal af variationer, som er opstået enten på grund af fejl og andre gange med vilje (som blandt andet et resultat af humor).").pack()
#     tk.Button(f,text="anytext").pack()
#
# #Removed the frame packing
# #f.pack()
#
# #Updated the screen before calculating the scrollregion
# root.update()
# c.config(scrollregion=c.bbox("all"))
#
# root.mainloop()

root = tk.Tk()
canvas = tk.Canvas(root, width=150, height=150)
canvas.create_oval(10, 10, 20, 20, fill="red")
canvas.create_oval(200, 200, 220, 220, fill="blue")
canvas.grid(row=0, column=0)
button1 = tk.Button(canvas, text = "Quit", anchor = 'w')
button1.configure(width = 10, activebackground = "#33B5E5", relief = 'flat')
button1_window = canvas.create_window(10, 10, anchor='nw', window=button1)
scroll_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scroll_x.grid(row=1, column=0, sticky="ew")

canvas.configure(xscrollcommand=scroll_x.set)
canvas.configure(scrollregion=canvas.bbox("all"))
root.mainloop()