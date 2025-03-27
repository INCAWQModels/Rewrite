from tkinter import *
from tkinter import messagebox
from tkinter import ttk

def do_nothing():
    pass

def on_closing():
        if  messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()

class mainINCAWindow(Tk):
    
    def __init__(self):
        super().__init__()

        self.title("INCA UI demo (not complete!)")
        self.a_frame = FrameWithMenu(self)
        self.create_menu()
        self.protocol("WM_DELETE_WINDOW", on_closing)
    
    def create_menu(self):
        self.menubar = Menu(self)
        editMenu=Menu(self.menubar,tearoff=0)
        editMenu.add_command(label="Land Cover",command=do_nothing)
        editMenu.add_command(label="Reach",command=do_nothing)
        editMenu.add_command(label="Subcatchment",command=do_nothing)
        editMenu.add_separator()
        editMenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="Edit",menu=editMenu)
        self['menu'] = self.menubar

    
class FrameWithMenu(Frame):
    def __init__(self, master):
        super().__init__(master)

    def replace_menu(self):
        """ Overwrite parent's menu if parent's class name is in _valid_cls_names.
        """

        _parent_cls_name = type(self.master).__name__
        _valid_cls_names = ("Tk", "Toplevel", "Root")
        if _parent_cls_name in _valid_cls_names:
            self.menubar = Menu(self)
            self.menubar.add_command(label="Frame", command=self.master.create_menu)
            self.master['menu'] = self.menubar

    
    """def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.button1 = Button(self.frame, text = 'Exit', width = 25, command = self.exit)
        self.button1.pack()
        self.frame.pack()

        self.menuBar=Menu(self.frame)
        editMenu=Menu(self.menuBar,tearoff=0)
        editMenu.add_command(label="Land Cover",command=do_nothing)
        editMenu.add_command(label="Reach",command=do_nothing)
        editMenu.add_command(label="Subcatchment",command=do_nothing)
        editMenu.add_separator()
        editMenu.add_command(label="Exit",command=root.quit)
        self.menuBar.add_cascade(label="Edit",menu=editMenu)
        self.menuBar.config(menu=self.menuBar)

        def new_window(self):
            self.newWindow = tk.Toplevel(self.master)
            self.app = Demo2(self.newWindow)
		

def doNothing():
	pass

def open_subcatchment(): 
	
	# Create widget
	subcatchment = Toplevel() 
	
	# define title for window
	subcatchment.title("Subcatchment")
	
	# specify size
	subcatchment.geometry("300x300")

	#create a notebook to hold some data to input
	n=ttk.Notebook(subcatchment)
	f1=ttk.Frame(n,width=280, height=280)
	n.add(f1,text="Area")
	f2=ttk.Frame(n,width=280, height=280)
	n.add(f2,text="Direct runoff")
	f3=ttk.Frame(n,width=280, height=280)
	n.add(f3,text="Land use groups")
	f4=ttk.Frame(n,width=280, height=280)
	n.add(f4,text="Constants")
	f5=ttk.Frame(n,width=280, height=280)
	n.add(f5,text="Depostion")
	n.pack(fill="both", expand=True)
	
	subcatchment.attributes("-topmost", 1)
	# Display until closed manually.
	subcatchment.mainloop()
	
def open_reach(): 
	
	# Create widget
	reach = Toplevel() 
	
	# define title for window
	reach.title("Reach")
	
	# specify size
	reach.geometry("200x100")
	
	reach.attributes("-topmost", 1)
	# Display until closed manually.
	reach.mainloop()

def open_landCover(): 
	
	# Create widget
	landCover = Toplevel(root)
	
	# Define title for window
	landCover.title("Land Cover")
	
	# specify size
	landCover.geometry("200x200")
	
	landCover.attributes("-topmost", 1)
	# Display until closed manually
	landCover.mainloop()
"""

if __name__ == "__main__":
    root = mainINCAWindow()
    root.mainloop()
