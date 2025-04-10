"""First steps towards creating an INCA-type UI, could definitely still use some work"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from os import path

from parameterSet import *
from createNewParameterSet import create_new_parameter_set

def do_nothing():
    messagebox.showinfo(message="This feature is not yet implemented.")

def on_closing():
        if  messagebox.askokcancel(title="Quit",message= "Do you want to quit?"):
            app.destroy()

def on_tab_changed(event):
    selected_tab=event.widget.select()
    tab_text=event.widget.tab(selected_tab,"text")
    print("Tab text: ", tab_text)

def make_notebook(parent, tabNames, frame_width=280, frame_height=280):
        n=ttk.Notebook(parent)
        n.bind("<<NotebookTabChanged>>",on_tab_changed)        

        frames = {}
        for tabName in tabNames:
            frames[tabName]=ttk.Frame(n, width=frame_width, height=frame_height)
            n.add(frames[tabName],text=tabName )
        return n

class subcatchmentWindow(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)

        self.selectedSubcatchment = tk.StringVar
        self.geometry('300x450')
        self.title('Subcatchment Window')

        self.nb=make_notebook(self,parent.subcatchments)
        self.nb.pack(fill="both", expand=True)

        self.create_menu(parent.subcatchments)

        self.protocol("WM_DELETE_WINDOW", on_closing)        
        
        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

    def create_menu(self, subcatchments):
        self.menubar = tk.Menu(self)
        chooseSubcatchmentMenu=tk.Menu(self.menubar,tearoff=0)
        for subcatchment in subcatchments:
            chooseSubcatchmentMenu.add_command(label=subcatchment, command=(lambda subcatchment=subcatchment: messagebox.askquestion(message=subcatchment)))
        chooseSubcatchmentMenu.add_separator()
        chooseSubcatchmentMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Subcatchment",menu=chooseSubcatchmentMenu)
        self['menu'] = self.menubar

class reachWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x450')
        self.title('Reach Window')

        self.create_menu(parent.reaches)

        self.nb=make_notebook(self,parent.reaches)
        self.nb.pack(fill="both", expand=True)

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)
        
    def create_menu(self, reaches):
        self.menubar = tk.Menu(self)
        chooseReachMenu=tk.Menu(self.menubar, tearoff=0)
        for reach in reaches:
            chooseReachMenu.add_command(label=reach, command=(lambda reach=reach: messagebox.askquestion(message=reach)))
        chooseReachMenu.add_separator()
        chooseReachMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Reach",menu=chooseReachMenu)
        self['menu'] = self.menubar

class landCoverWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x450')
        self.title('Land Cover Window')
        
        self.create_menu(parent.landCoverTypes)
        frames = {}

        n=ttk.Notebook(self)
        n.bind("<<NotebookTabChanged>>",on_tab_changed)
        n.pack(expand=True, fill="both")
    
        tabs=["General","Snow"] + parent.buckets

        for landCoverType   in parent.landCoverTypes:  # Creating notebooks
            frames[landCoverType] = ttk.Frame(n)
            n.add(frames[landCoverType], text=landCoverType)
        
        # Loop to add nested notebooks and sub-tabs

        for landCoverType in parent.landCoverTypes:  # Creating notebooks
            nested_n = ttk.Notebook(frames[landCoverType])
            nested_n.bind("<<NotebookTabChanged>>",on_tab_changed)
            nested_n.pack(expand=True, fill="both")
   
            #may want to add a dictionary here, too
            for tab in tabs:  # Creating sub-tabs
                nested_frame = ttk.Frame(nested_n)
                nested_n.add(nested_frame, text=tab)

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

    def create_menu(self,landCoverTypes):
        self.menubar = tk.Menu(self)
        chooseLandCoverMenu=tk.Menu(self.menubar,tearoff=0)
        for landCoverType in landCoverTypes:
            chooseLandCoverMenu.add_command(label=landCoverType, command=(lambda landCoverType=landCoverType: messagebox.askquestion(message=landCoverType)))
        chooseLandCoverMenu.add_separator()
        chooseLandCoverMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Land Cover",menu=chooseLandCoverMenu)
        self['menu'] = self.menubar

class loadParameterSetWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('200x200')
        self.title('Load Parameter Set')

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

class createParameterSetWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('200x200')
        self.title('Create Parameter Set')

        create_new_parameter_set(self)

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.wm_iconphoto(True,tk.PhotoImage(file="incaMan.png"))

        self.geometry('400x600')
        self.title('Main Window')
        self.protocol("WM_DELETE_WINDOW", on_closing)
        self.create_menu()

        #make a parameter set, hard coded for now but can fix later
        fileName='INCAFormatParSet.json'
        if (path.isfile(fileName) == True):
            p=ParameterSet(fileName)        
    
        self.buckets = p.parameters['bucket']['general']['name']
        self.landCoverTypes=p.parameters['landCover']['general']['name']
        self.reaches=p.parameters['reach']['general']['name']
        self.subcatchments=p.parameters['subcatchment']['general']['name']
    
    def create_menu(self):
        self.menubar = tk.Menu(self)
        
        editMenu=tk.Menu(self.menubar,tearoff=0)
        editMenu.add_command(label="Land Cover",
                             command=lambda: self.openLandCoverWindow(self.landCoverTypes))
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
        runMenu.add_separator()
        runMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Run", menu=runMenu)

        manageMenu=tk.Menu(self.menubar,tearoff=0)
        manageMenu.add_command(label="Create New Parameter Set", command=self.createParameterSet)
        manageMenu.add_command(label="Load Parameter Set",command=self.loadParameterSet)
        manageMenu.add_command(label="Time Series",command=do_nothing)
        manageMenu.add_separator()
        manageMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Manage", menu=manageMenu)

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

    def loadParameterSet(self):
        l=loadParameterSetWindow(self)
        l.attributes("-topmost", 1)

    def createParameterSet(self):
        c=createParameterSetWindow(self)
        c.attributes("-topmost", 1)

if __name__ == "__main__":
    app = App()
    app.mainloop()