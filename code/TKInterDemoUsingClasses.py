from tkinter import *
from tkinter import ttk

class demo1():
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.button1 = Button(self.frame, text = 'Exit', width = 25, command = self.exit)
        self.button1.pack()
        self.frame.pack()

    def exit(self):
        pass

        """
        menuBar = Menu(self)
        editMenu=Menu(menuBar,tearoff=0)
        editMenu.add_command(label="Land Cover",command=open_landCover)
        editMenu.add_command(label="Reach",command=open_reach)
        editMenu.add_command(label="Subcatchment",command=open_subcatchment)
        editMenu.add_separator()
        editMenu.add_command(label="Exit",command=root.quit)
        menuBar.add_cascade(label="Edit",menu=editMenu)
        self.config(menu=menuBar)

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
    root = Tk()
    root.title("INCA UI demo using classes")
    app = demo1(root)
    root.mainloop()
