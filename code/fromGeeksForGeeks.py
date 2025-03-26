from tkinter import *


# Create the root window
# with specified size and title
root = Tk() 
root.title("Root Window") 
root.geometry("450x300") 

# Create label for root window
label1 = Label(root, text = "This is the root window")

# define a function for 2nd toplevel 
# window which is not associated with 
# any parent window

def doNothing():
	pass

def open_Toplevel2(): 
	
	# Create widget
	top2 = Toplevel() 
	
	# define title for window
	top2.title("Toplevel2")
	
	# specify size
	top2.geometry("200x100")
	
	# Create label
	label = Label(top2,
				text = "This is a Toplevel2 window")
	
	# Create exit button.
	button = Button(top2, text = "Exit", 
					command = top2.destroy)
	
	menuBar = Menu(top2)
	editMenu=Menu(menuBar,tearoff=0)
	editMenu.add_command(label="Land Cover",command=doNothing)
	editMenu.add_command(label="Reach",command=doNothing)
	editMenu.add_command(label="Subcatchment",command=doNothing)
	editMenu.add_separator()
	editMenu.add_command(label="Exit",command=top2.destroy)
	menuBar.add_cascade(label="Top2Edit",menu=editMenu)
	top2.config(menu=menuBar)
	
	label.pack()
	button.pack()
	
	top2.attributes("-topmost", 1)
	# Display until closed manually.
	top2.mainloop()
	
# define a function for 1st toplevel
# which is associated with root window.
def open_Toplevel1(): 
	
	# Create widget
	top1 = Toplevel(root)
	
	# Define title for window
	top1.title("Toplevel1")
	
	# specify size
	top1.geometry("200x200")
	
	# Create label
	label = Label(top1,
				text = "This is a Toplevel1 window")
	
	# Create Exit button
	button1 = Button(top1, text = "Exit",
					command = top1.destroy)
	
	# create button to open toplevel2
	button2 = Button(top1, text = "open toplevel2",
					command = open_Toplevel2)
	
	label.pack()
	button2.pack()
	button1.pack()
	
	menuBar = Menu(top1)
	editMenu=Menu(menuBar,tearoff=0)
	editMenu.add_command(label="Land Cover",command=doNothing)
	editMenu.add_command(label="Reach",command=doNothing)
	editMenu.add_command(label="Subcatchment",command=doNothing)
	editMenu.add_separator()
	editMenu.add_command(label="Exit",command=top1.destroy)
	menuBar.add_cascade(label="Top1Edit",menu=editMenu)
	top1.config(menu=menuBar)

	# Display until closed manually
	top1.mainloop()

# Create button to open toplevel1
button = Button(root, text = "open toplevel1",
				command = open_Toplevel1)
label1.pack()

# position the button
button.place(x = 155, y = 50)

menuBar = Menu(root)
editMenu=Menu(menuBar,tearoff=0)
editMenu.add_command(label="Land Cover",command=doNothing)
editMenu.add_command(label="Reach",command=doNothing)
editMenu.add_command(label="Subcatchment",command=doNothing)
editMenu.add_separator()
editMenu.add_command(label="Exit",command=root.quit)
menuBar.add_cascade(label="RootEdit",menu=editMenu)
root.config(menu=menuBar)

# Display until closed manually
root.mainloop()
