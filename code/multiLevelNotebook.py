import tkinter as tk
from tkinter import ttk

# Create main application window
root = tk.Tk()
root.title("TTK Notebook with Frames")
root.geometry("500x400")

# Create a Notebook (tab container)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Dictionary to store frames
frames = {}

# Create 5 tabs, each with a frame
for i in range(1, 6):  # Creating 5 tabs
    frames[i] = ttk.Frame(notebook)
    notebook.add(frames[i], text=f"Tab {i}")

# Loop to add nested notebooks and sub-tabs
for i in range(1, 6):
    nested_notebook = ttk.Notebook(frames[i])
    nested_notebook.pack(expand=True, fill="both")
   
    for j in range(1, 4):  # Creating 3 sub-tabs
        nested_frame = ttk.Frame(nested_notebook)
        nested_notebook.add(nested_frame, text=f"Sub-tab {j}")

# Run the main event loop
root.mainloop()
