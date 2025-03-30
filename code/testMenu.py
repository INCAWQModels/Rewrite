"""First steps towards creating an INCA-type UI, could definitely still use some work"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from inputMockUps import *

def do_nothing():
    pass

def on_closing():
        if  messagebox.askokcancel("Quit", "Do you want to quit?"):
            app.destroy()

class subcatchmentWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x450')
        self.title('Subcatchment Window')
        self.makeNotebook()
        self.protocol("WM_DELETE_WINDOW", on_closing)        
        
        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)
        
    def makeNotebook(self):
        #create a notebook to hold some data to input
        frame_width=280
        frame_height=280
        n=ttk.Notebook(self)
        n.add(ttk.Frame(n, width=frame_width, height=frame_height), text="Area")
        n.add(ttk.Frame(n, width=frame_width, height=frame_height), text="Direct runoff")
        n.add(ttk.Frame(n, width=frame_width, height=frame_height), text="Land use groups")
        n.add(ttk.Frame(n, width=frame_width, height=frame_height), text="Constants")
        n.add(ttk.Frame(n, width=frame_width, height=frame_height), text="Deposition")
        n.pack(fill="both", expand=True)

class reachWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x450')
        self.title('Reach Window')

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

class landCoverWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x450')
        self.title('Land Cover Window')
        
        self.create_menu(landCoverTypes)
        self.makeNotebook(buckets)

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)
    
    def list_bucket(event):
        print("Changed ...")

    def makeNotebook(self,buckets):
        frame_width=280
        frame_height=280
        n=ttk.Notebook(self)
        n.add(ttk.Frame(n,width=frame_width, height=frame_height),text="General")
        n.add(ttk.Frame(n,width=frame_width, height=frame_height),text="Snow")
        for bucket in buckets:
            n.add(ttk.Frame(n, width=frame_width, height=frame_height),text=bucket )
        
        n.bind('<<NotebookTabChanged>>', lambda: self.list_bucket()) 
        n.pack(fill="both", expand=True)

    def create_menu(self,landCoverTypes):
        self.menubar = tk.Menu(self)
        chooseLandCoverMenu=tk.Menu(self.menubar,tearoff=0)
        for landCoverType in landCoverTypes:
            chooseLandCoverMenu.add_command(label=landCoverType, command=do_nothing)
        chooseLandCoverMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Land Cover",menu=chooseLandCoverMenu)
        self['menu'] = self.menubar

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('400x600')
        self.title('Main Window')
        self.protocol("WM_DELETE_WINDOW", on_closing)
        self.create_menu()

        
    def create_menu(self):
        self.menubar = tk.Menu(self)
        
        editMenu=tk.Menu(self.menubar,tearoff=0)
        editMenu.add_command(label="Land Cover",
                             command=lambda: self.openLandCoverWindow(landCoverTypes))
        editMenu.add_command(label="Reach",
                             command=lambda: self.openReachWindow())
        editMenu.add_command(label="Subcatchment",
                             command=lambda: self.openSubcatchmentWindow())
        editMenu.add_separator()
        editMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Edit",menu=editMenu)

        runMenu=tk.Menu(self.menubar,tearoff=0)
        runMenu.add_command(label="Calibration", command=do_nothing)
        runMenu.add_command(label="Scenario",command=do_nothing)
        self.menubar.add_cascade(label="Run", menu=runMenu)

        self['menu'] = self.menubar


    def on_closing(self):
        if  messagebox.askokcancel("Quit", "Do you want to quit?"):
            pass

    def openLandCoverWindow(self,landCoverTypes):
        lc=landCoverWindow(self)
        lc.attributes("-topmost", 1)

    def openSubcatchmentWindow(self):
        sc=subcatchmentWindow(self)
        sc.attributes("-topmost", 1)

    def openReachWindow(self):
        r=reachWindow(self)
        r.attributes("-topmost", 1)

if __name__ == "__main__":
    app = App()
    app.mainloop()