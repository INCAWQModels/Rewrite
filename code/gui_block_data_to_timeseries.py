"""
Block Data to TimeSeries Converter GUI

This module provides a graphical user interface for the block data to TimeSeries converter.
It uses Tkinter to create the interface and calls functions from the processing module.
"""

import os
import sys
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import the processing functions
from block_data_to_timeseries import convert_blocks_to_timeseries, parse_block_file


class BlockDataToTimeSeriesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Data to TimeSeries Converter")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup variables
        self.input_file = tk.StringVar()
        self.output_base_name = tk.StringVar()
        self.start_date = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.start_time = tk.StringVar(value="00:00:00")
        self.timestep = tk.StringVar(value="60")
        self.column_names = tk.StringVar()
        
        # Create the UI elements
        self.create_input_section()
        self.create_output_section()
        self.create_datetime_section()
        self.create_columns_section()
        self.create_log_section()
        self.create_buttons()
        self.create_status_bar()
    
    def create_input_section(self):
        # Input file section
        input_frame = ttk.LabelFrame(self.main_frame, text="Input File", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Block Data File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        input_frame.columnconfigure(1, weight=1)
    
    def create_output_section(self):
        # Output file section
        output_frame = ttk.LabelFrame(self.main_frame, text="Output Files", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Base Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_base_name, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_base).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Add help text
        ttk.Label(output_frame, text="The system will generate [base_name].csv and [base_name].json files", 
                 font=("Arial", 8)).grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=2)
        
        # Make the entry column expandable
        output_frame.columnconfigure(1, weight=1)
    
    def create_datetime_section(self):
        # Date and time settings
        datetime_frame = ttk.LabelFrame(self.main_frame, text="Date and Time Settings", padding="10")
        datetime_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start date
        ttk.Label(datetime_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(datetime_frame, textvariable=self.start_date, width=15).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Start time
        ttk.Label(datetime_frame, text="Start Time (HH:MM:SS):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(datetime_frame, textvariable=self.start_time, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Timestep
        ttk.Label(datetime_frame, text="Timestep (seconds):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        timestep_frame = ttk.Frame(datetime_frame)
        timestep_frame.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Entry(timestep_frame, textvariable=self.timestep, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(timestep_frame, text="1 min", command=lambda: self.timestep.set("60")).pack(side=tk.LEFT, padx=2)
        ttk.Button(timestep_frame, text="1 hour", command=lambda: self.timestep.set("3600")).pack(side=tk.LEFT, padx=2)
        ttk.Button(timestep_frame, text="1 day", command=lambda: self.timestep.set("86400")).pack(side=tk.LEFT, padx=2)
    
    def create_columns_section(self):
        # Column names section
        columns_frame = ttk.LabelFrame(self.main_frame, text="Column Names", padding="10")
        columns_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(columns_frame, text="Column Names (comma-separated):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(columns_frame, textvariable=self.column_names, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        # Example
        ttk.Label(columns_frame, text="Example: Temperature,Pressure,Humidity").grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Make the entry column expandable
        columns_frame.columnconfigure(1, weight=1)
    
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
        
        self.status_message = tk.StringVar(value="Ready")
        ttk.Label(status_bar, textvariable=self.status_message).pack(side=tk.LEFT, padx=5)
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Block Data file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Set a default output base name based on the input file
            base = os.path.splitext(os.path.basename(filename))[0]
            self.output_base_name.set(base)
    
    def browse_output_base(self):
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            if self.input_file.get():
                # Get the input file name without extension
                base_name = os.path.splitext(os.path.basename(self.input_file.get()))[0]
                self.output_base_name.set(os.path.join(folder, base_name))
            else:
                # If no input file is selected, prompt for a base name
                base_name = filedialog.asksaveasfilename(
                    title="Enter Base Name",
                    initialdir=folder,
                    initialfile="output"
                )
                if base_name:
                    # Remove any extension the user might have added
                    base_name = os.path.splitext(base_name)[0]
                    self.output_base_name.set(base_name)
    
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
    
    def open_output_folder(self):
        output_base = self.output_base_name.get()
        if output_base:
            folder = os.path.dirname(output_base)
            if not folder:  # If only a base name was provided without a path
                folder = os.getcwd()
                
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
        else:
            messagebox.showinfo("Info", "Please select an output base name first.")
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.root.update_idletasks()  # Update the UI
    
    def validate_inputs(self):
        """Validate all user inputs"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return False
        
        if not self.output_base_name.get():
            messagebox.showerror("Error", "Please specify an output base name.")
            return False
        
        # Validate date format
        try:
            datetime.datetime.strptime(self.start_date.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
            return False
        
        # Validate time format
        try:
            datetime.datetime.strptime(self.start_time.get(), "%H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Please use HH:MM:SS.")
            return False
        
        # Validate timestep
        try:
            timestep = float(self.timestep.get())
            if timestep <= 0:
                raise ValueError("Timestep must be positive")
        except ValueError:
            messagebox.showerror("Error", "Timestep must be a positive number.")
            return False
        
        return True
    
    def run_conversion(self):
        if not self.validate_inputs():
            return
        
        # Parse the inputs
        input_file = self.input_file.get()
        output_base_name = self.output_base_name.get()
        
        # Combine date and time into a datetime object
        start_datetime_str = f"{self.start_date.get()} {self.start_time.get()}"
        start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
        
        timestep_seconds = float(self.timestep.get())
        
        # Parse column names
        column_names_str = self.column_names.get().strip()
        if column_names_str:
            column_names = [name.strip() for name in column_names_str.split(',')]
        else:
            column_names = []
            self.log("No column names provided. Using default column names.")
        
        # Update status
        self.status_message.set("Converting...")
        self.log(f"Starting conversion with the following parameters:")
        self.log(f"Input file: {input_file}")
        self.log(f"Output base name: {output_base_name}")
        self.log(f"Start datetime: {start_datetime}")
        self.log(f"Timestep: {timestep_seconds} seconds")
        self.log(f"Column names: {column_names}")
        
        try:
            csv_path, json_path = convert_blocks_to_timeseries(
                input_file, 
                output_base_name, 
                start_datetime, 
                timestep_seconds, 
                column_names,
                self.log
            )
            
            self.status_message.set("Conversion completed")
            self.log("Conversion completed successfully!")
            self.log(f"CSV file saved to: {csv_path}")
            self.log(f"JSON file saved to: {json_path}")
            
            success_message = (
                f"Conversion completed successfully!\n"
                f"CSV file saved to: {csv_path}\n"
                f"JSON file saved to: {json_path}"
            )
            
            messagebox.showinfo("Success", success_message)
            
        except Exception as e:
            self.log(f"Error during conversion: {str(e)}")
            self.status_message.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")


def run_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    
    try:
        root.wm_iconphoto(True, tk.PhotoImage(file="incaMan.png"))
    except:
        # If the icon file is not found, just continue without it
        pass
    
    app = BlockDataToTimeSeriesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()