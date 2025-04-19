"""First steps towards creating an INCA-type UI, could definitely still use some work.
The code can be tested with the parameter set in test_menus.json
"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from os import path

from parameterSet import *
from createNewParameterSet import create_new_parameter_set

def do_nothing():
    messagebox.showinfo(message="This feature is not yet implemented.")

def on_closing():
        if messagebox.askokcancel(title="Quit",message= "Do you want to quit?"):
            app.destroy()

def on_tab_changed(event):
    selected_tab=event.widget.select()
    tab_text=event.widget.tab(selected_tab,"text")

def make_notebook(parent, tabNames, frame_width=280, frame_height=280):
        n=ttk.Notebook(parent)
        n.bind("<<NotebookTabChanged>>",on_tab_changed)        

        frames = {}
        for tabName in tabNames:
            frames[tabName]=ttk.Frame(n, width=frame_width, height=frame_height)
            n.add(frames[tabName],text=tabName)
        return n, frames

class subcatchmentWindow(tk.Toplevel):
    
    def __init__(self, parent):
        super().__init__(parent)

        self.selectedSubcatchment = tk.StringVar
        self.geometry('300x450')
        self.title('Subcatchment Window')

        self.create_menu(parent.subcatchments)
        
        # Create first level notebook
        self.nb, self.frames = make_notebook(self, parent.subcatchments)
        self.nb.pack(fill="both", expand=True)
        
        # Create second level notebooks for each subcatchment
        self.subcategories = parent.subcatchment_categories
        for subcatchment in parent.subcatchments:
            # Create nested notebook for each subcatchment
            nested_nb, nested_frames = make_notebook(self.frames[subcatchment], self.subcategories)
            nested_nb.pack(expand=True, fill="both")

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

        # Create first level notebook
        self.nb, self.frames = make_notebook(self, parent.reaches)
        self.nb.pack(fill="both", expand=True)
        
        # Create second level notebooks for each reach
        self.subcategories = parent.reach_categories
        for reach in parent.reaches:
            # Create nested notebook for each reach
            nested_nb, nested_frames = make_notebook(self.frames[reach], self.subcategories)
            nested_nb.pack(expand=True, fill="both")

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

        # Create first level notebook
        self.nb, self.frames = make_notebook(self, parent.landCoverTypes)
        self.nb.pack(expand=True, fill="both")
    
        # Create second level notebooks for each land cover type
        # First level: Land Cover types
        # Second level: General, Snow, buckets (DR, US, etc)
        # Third level for buckets: general, hydrology, etc.
        
        for landCoverType in parent.landCoverTypes:
            # Create nested notebook with tabs General, Snow, and each bucket
            tabs = ["general", "precipitation"] + parent.buckets
            nested_nb, nested_frames = make_notebook(self.frames[landCoverType], tabs)
            nested_nb.pack(expand=True, fill="both")
            
            # For each bucket tab, create a third level notebook
            bucket_categories = parent.bucket_categories
            for bucket in parent.buckets:
                if bucket in nested_frames:
                    bucket_nb, bucket_frames = make_notebook(nested_frames[bucket], bucket_categories)
                    bucket_nb.pack(expand=True, fill="both")

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

        # Initialize default values in case no file is selected
        self.buckets = []
        self.landCoverTypes = []
        self.reaches = []
        self.subcatchments = []
        
        # Default categories for nested notebooks
        self.subcatchment_categories = ["general", "hydrology", "soilOrSediment", "chemistry"]
        self.reach_categories = ["general", "hydrology", "soilOrSediment", "chemistry"]
        self.bucket_categories = ["general", "hydrology", "soilOrSediment", "chemistry"]
        
        # Ask user for parameter file
        self.load_parameter_file()
    
    def extract_categories(self, param_section):
        """Extract categories (keys) from a parameter section, excluding 'identifier'"""
        categories = []
        for key in param_section.keys():
            if key != 'identifier':
                categories.append(key)
        return categories
    
    def load_parameter_file(self):
        """Ask user to select a JSON parameter file and load it"""
        fileName = filedialog.askopenfilename(
            title="Select Parameter File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if fileName:  # If user selected a file (not canceled)
            try:
                p = ParameterSet(fileName)
                # Load parameters from the file
                self.buckets = p.parameters['bucket']['identifier']['name']
                self.bucket_abbreviations = p.parameters['bucket']['identifier']['abbreviation']
                self.landCoverTypes = p.parameters['landCover']['identifier']['name']
                self.landCoverType_abbreviations = p.parameters['landCover']['identifier']['abbreviation']
                self.reaches = p.parameters['reach']['identifier']['name']
                self.reach_abbreviations = p.parameters['reach']['identifier']['abbreviation']
                self.subcatchments = p.parameters['subcatchment']['identifier']['name']
                self.subcatchment_abbreviations = p.parameters['subcatchment']['identifier']['abbreviation']
                
                # Extract categories from each section of the JSON
                self.subcatchment_categories = self.extract_categories(p.parameters['subcatchment'])
                self.reach_categories = self.extract_categories(p.parameters['reach'])
                self.landcover_categories = self.extract_categories(p.parameters['landCover'])
                
                # Get bucket categories from the first bucket entry
                if 'bucket' in p.parameters['landCover'] and len(p.parameters['landCover']['bucket']) > 0:
                    self.bucket_categories = self.extract_categories(p.parameters['landCover']['bucket'][0])
                
                messagebox.showinfo("Success", f"Parameter file loaded: {fileName}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load parameter file: {str(e)}")
                # Option to try again
                if messagebox.askyesno("Retry", "Would you like to select another file?"):
                    self.load_parameter_file()
        else:
            # User cancelled - ask if they want to try again or create a new parameter set
            response = messagebox.askquestion("No File Selected", 
                                             "No parameter file was selected. Would you like to create a new parameter set?")
            if response == 'yes':
                self.createParameterSet()
            else:
                if messagebox.askyesno("Try Again", "Would you like to select a parameter file?"):
                    self.load_parameter_file()
    
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
        # After closing the load window, reload parameters
        self.load_parameter_file()

    def createParameterSet(self):
        c=createParameterSetWindow(self)
        c.attributes("-topmost", 1)

if __name__ == "__main__":
    app = App()
    app.mainloop()