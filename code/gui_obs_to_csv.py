"""
OBS to CSV Converter - GUI Module

This module provides a graphical user interface for the OBS to CSV converter.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import the core processing module
from obs_converter_core import convert_obs_to_csv


class ObsToCSVConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OBS to CSV Converter")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup variables
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.status_message = tk.StringVar()
        
        # Create the UI elements
        self.create_input_section()
        self.create_output_section()
        self.create_log_section()
        self.create_buttons()
        self.create_status_bar()
    
    def create_input_section(self):
        # Input file section
        input_frame = ttk.LabelFrame(self.main_frame, text="Input File", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="OBS File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        input_frame.columnconfigure(1, weight=1)
    
    def create_output_section(self):
        # Output folder section
        output_frame = ttk.LabelFrame(self.main_frame, text="Output Settings", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_folder).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        output_frame.columnconfigure(1, weight=1)
    
    def create_log_section(self):
        # Log section
        log_frame = ttk.LabelFrame(self.main_frame, text="Conversion Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create text widget with scrollbar for log
        self.log_text = tk.Text(log_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def create_buttons(self):
        # Buttons section
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Convert", command=self.run_conversion, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy, width=15).pack(side=tk.RIGHT, padx=5)
    
    def create_status_bar(self):
        # Status bar at the bottom
        status_bar = ttk.Frame(self.main_frame, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_bar, textvariable=self.status_message).pack(side=tk.LEFT, padx=5)
        
        # Set initial status
        self.status_message.set("Ready")
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select OBS file",
            filetypes=[("OBS files", "*.obs"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Set a default output folder based on the input file location
            file_dir = os.path.dirname(filename)
            self.output_folder.set(os.path.join(file_dir, "output"))
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
    
    def open_output_folder(self):
        folder = self.output_folder.get()
        if os.path.exists(folder):
            try:
                # Try to open the folder in the file explorer
                if os.name == 'nt':  # Windows
                    os.startfile(folder)
                elif os.name == 'posix':  # macOS or Linux
                    import subprocess
                    subprocess.Popen(['open', folder])  # macOS
            except:
                self.log("Could not open output folder in file explorer.")
        else:
            messagebox.showinfo("Info", "Output folder does not exist yet.")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.root.update_idletasks()  # Update the UI
    
    def run_conversion(self):
        # Get input and output values
        input_file = self.input_file.get()
        output_folder = self.output_folder.get()
        
        # Validate inputs
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return
        
        # Start conversion
        self.status_message.set("Converting...")
        
        try:
            # Use the reusable conversion function
            created_files = convert_obs_to_csv(input_file, output_folder, self.log)
            
            self.status_message.set("Conversion completed")
            
            # Show success message
            messagebox.showinfo("Success", f"Conversion completed successfully!\n{len(created_files)} CSV files were saved to: {output_folder}")
            
        except FileNotFoundError as e:
            self.log(f"Error: {str(e)}")
            self.status_message.set("Error occurred")
            messagebox.showerror("Error", str(e))
        except Exception as e:
            self.log(f"Error during conversion: {str(e)}")
            self.status_message.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")


def run_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    root.wm_iconphoto(True,tk.PhotoImage(file="incaMan.png"))
    app = ObsToCSVConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()