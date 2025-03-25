"""Some code to test multiple top level windows in tkInter, will be useful for planned INCA rewrite"""
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("INCA Windowing demo")
root.geometry("600x450")

landCoverTypes=["Forest", "Arable", "Urban"]

def doNothing():
    pass

def openLandCover(landCoverTypes):

    landCover=Toplevel(root)
    landCover.title("Land Cover")
    landCover.geometry("300x300")

    Label(landCover,text="Land Cover window").pack()

    menubar=Menu(landCover)
    landCoverMenu=Menu(menubar,tearoff=0) 
    for landCoverType in landCoverTypes:
        landCoverMenu.add_command(label=landCoverType,command=doNothing)   
    menubar.add_cascade(label="Edit",menu=landCoverMenu)

    exitButton = Button(landCover,text="Exit",command=landCover.destroy)
    exitButton.place(x=20,y=20)

    landCover.config(menu=menubar)
    landCover.mainloop()
    #landCover.wm_transient(root)

def openSubcatchment():

    subCatchment=Toplevel(root)
    subCatchment.title("Subcatchment")
    subCatchment.geometry("300x300")

    subCatchmentLabel=Label(subCatchment,text="Subcatchment window")

    exitButton = Button(subCatchment,text="Exit",command=subCatchment.destroy)

    subCatchmentLabel.pack
    exitButton.pack

    subCatchment.wm_transient(root)

def openReach():

    reach=Toplevel(root)
    reach.title("Reach")
    reach.geometry("300x300")

    reachLabel=Label(reach,text="Reach window")

    exitButton = Button(reach,text="Exit",command=reach.destroy)

    reachLabel.pack
    exitButton.pack

    reach.wm_transient(root)

#create a root window

menubar=Menu(root)
editMenu=Menu(menubar,tearoff=0)
editMenu.add_command(label="Land Cover",command=openLandCover)
editMenu.add_command(label="Reach",command=openReach)
editMenu.add_command(label="Subcatchment",command=openSubcatchment)
editMenu.add_separator()
editMenu.add_command(label="Exit",command=root.quit)
menubar.add_cascade(label="Edit",menu=editMenu)

root.config(menu=menubar)
root.mainloop()