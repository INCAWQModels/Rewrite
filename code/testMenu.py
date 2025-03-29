"""First steps towards creating an INCA-type UI, could definitely still use some work"""
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def do_nothing():
    pass

def on_closing():
        if  messagebox.askokcancel("Quit", "Do you want to quit?"):
            app.destroy()

class subcatchmentWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x100')
        self.title('Subcatchment Window')
        self.makeNotebook()
        self.protocol("WM_DELETE_WINDOW", on_closing)        
        
        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)
        
    def makeNotebook(self):
        #create a notebook to hold some data to input
        n=ttk.Notebook(self)
        f1=ttk.Frame(n,width=280, height=280)
        n.add(f1,text="Area")
        f2=ttk.Frame(n, width=280, height=280)
        n.add(f2,text="Direct runoff")
        f3=ttk.Frame(n,width=280, height=280)
        n.add(f3,text="Land use groups")
        f4=ttk.Frame(n,width=280, height=280)
        n.add(f4,text="Constants")
        f5=ttk.Frame(n,width=280, height=280)
        n.add(f5,text="Depostion")
        n.pack(fill="both", expand=True)

class reachWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x100')
        self.title('Reach Window')

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)

class landCoverWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry('300x100')
        self.title('Land Cover Window')

        ttk.Button(self,
                text='Close',
                command=self.destroy).pack(expand=True)
        

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry('300x200')
        self.title('Main Window')
        self.protocol("WM_DELETE_WINDOW", on_closing)
        self.create_menu()

        # place a button on the root window
        ttk.Button(self,
                text='Open windows',
                command=self.open_window).pack(expand=True)
        
    def create_menu(self):
        self.menubar = tk.Menu(self)
        editMenu=tk.Menu(self.menubar,tearoff=0)
        editMenu.add_command(label="Land Cover",command=self.openLandCoverWindow)
        editMenu.add_command(label="Reach",command=do_nothing)
        editMenu.add_command(label="Subcatchment",command=do_nothing)
        editMenu.add_separator()
        editMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Edit",menu=editMenu)
        self['menu'] = self.menubar


    def on_closing(self):
        if  messagebox.askokcancel("Quit", "Do you want to quit?"):
            pass

    def openLandCoverWindow(self):
        lc=landCoverWindow(self)
        lc.attributes("-topmost", 1)

    def openSubcatchmentWindow(self):
        sc=subcatchmentWindow(self)
        sc.attributes("-topmost", 1)

    def openReachWindow(self):
        r=reachWindow(self)
        r.attributes("-topmost", 1)

    def open_window(self):
        lc=landCoverWindow(self)
        lc.attributes("-topmost", 1)
        sc=subcatchmentWindow(self)
        sc.attributes("-topmost", 1)
        r=reachWindow(self)
        r.attributes("-topmost", 1)

if __name__ == "__main__":
    app = App()
    app.mainloop()