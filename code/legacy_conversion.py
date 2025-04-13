"""
Data File Converter - GUI Application

This application provides a graphical interface for converting various data formats:
- Block data files to CSV
- OBS files to CSV 
- DAT files to CSV

The interface uses tabs to separate the different conversion utilities.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import sys

# Import the conversion modules
import block_data_processing
import obs_converter_core
import dat_to_csv_processor


class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data File Converter")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)
        
        # Create main notebook to hold tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs for each conversion utility
        self.block_tab = ttk.Frame(self.notebook)
        self.obs_tab = ttk.Frame(self.notebook)
        self.dat_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.block_tab, text="Block Data Converter")
        self.notebook.add(self.obs_tab, text="OBS File Converter")
        self.notebook.add(self.dat_tab, text="DAT File Converter")
        
        # Setup each tab
        self.setup_block_tab()
        self.setup_obs_tab()
        self.setup_dat_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set up logging to GUI
        self.log_frame = ttk.LabelFrame(root, text="Log")
        self.log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(self.log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar to log
        log_scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Clear log button
        self.clear_log_button = ttk.Button(self.log_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def log(self, message):
        """Add message to log text widget and scroll to end"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text widget"""
        self.log_text.delete(1.0, tk.END)
    
    def setup_block_tab(self):
        """Setup the Block Data Converter tab"""
        frame = ttk.Frame(self.block_tab, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Input file selection
        ttk.Label(frame, text="Input Block File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.block_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.block_input_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_block_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output file selection
        ttk.Label(frame, text="Output CSV File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.block_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.block_output_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_block_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Start date time
        ttk.Label(frame, text="Start Date/Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.block_start_datetime_var = tk.StringVar(value=current_time)
        ttk.Entry(frame, textvariable=self.block_start_datetime_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # Timestep
        ttk.Label(frame, text="Time Step (seconds):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.block_timestep_var = tk.StringVar(value="60")
        ttk.Entry(frame, textvariable=self.block_timestep_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        
        # Column names
        ttk.Label(frame, text="Column Names (space separated):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.block_column_names_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.block_column_names_var, width=50).grid(row=4, column=1, padx=5, pady=5)
        
        # Auto-detect columns checkbox
        self.block_autodetect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Auto-detect columns", variable=self.block_autodetect_var).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Convert button
        ttk.Button(frame, text="Convert", command=self.convert_block_file).grid(row=6, column=1, pady=20)
    
    def setup_obs_tab(self):
        """Setup the OBS File Converter tab"""
        frame = ttk.Frame(self.obs_tab, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Input file selection
        ttk.Label(frame, text="Input OBS File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.obs_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.obs_input_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_obs_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output folder selection
        ttk.Label(frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.obs_output_folder_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        ttk.Entry(frame, textvariable=self.obs_output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_obs_output_folder).grid(row=1, column=2, padx=5, pady=5)
        
        # Convert button
        ttk.Button(frame, text="Convert", command=self.convert_obs_file).grid(row=2, column=1, pady=20)
    
    def setup_dat_tab(self):
        """Setup the DAT File Converter tab"""
        frame = ttk.Frame(self.dat_tab, padding="10")
        frame.pack(fill='both', expand=True)
        
        # Input file selection
        ttk.Label(frame, text="Input DAT File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dat_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dat_input_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_dat_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output file selection
        ttk.Label(frame, text="Output CSV File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dat_output_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dat_output_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Browse...", command=self.browse_dat_output).grid(row=1, column=2, padx=5, pady=5)
        
        # Start date time
        ttk.Label(frame, text="Start Date/Time:").grid(row=2, column=0, sticky=tk.W, pady=5)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.dat_start_datetime_var = tk.StringVar(value=current_time)
        ttk.Entry(frame, textvariable=self.dat_start_datetime_var, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # Date format
        ttk.Label(frame, text="Date Format:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.dat_date_format_var = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
        ttk.Entry(frame, textvariable=self.dat_date_format_var, width=50).grid(row=3, column=1, padx=5, pady=5)
        
        # Time increment
        ttk.Label(frame, text="Time Increment (seconds):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.dat_time_increment_var = tk.StringVar(value="60")
        ttk.Entry(frame, textvariable=self.dat_time_increment_var, width=50).grid(row=4, column=1, padx=5, pady=5)
        
        # Column names
        ttk.Label(frame, text="Column Names (comma separated):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.dat_column_names_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dat_column_names_var, width=50).grid(row=5, column=1, padx=5, pady=5)
        
        # Convert button
        ttk.Button(frame, text="Convert", command=self.convert_dat_file).grid(row=6, column=1, pady=20)
    
    # File browser methods
    def browse_block_input(self):
        filename = filedialog.askopenfilename(title="Select Block Data File")
        if filename:
            self.block_input_var.set(filename)
            # Set default output filename
            self.block_output_var.set(os.path.splitext(filename)[0] + ".csv")
    
    def browse_block_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save CSV File", 
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.block_output_var.set(filename)
    
    def browse_obs_input(self):
        filename = filedialog.askopenfilename(title="Select OBS File")
        if filename:
            self.obs_input_var.set(filename)
    
    def browse_obs_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.obs_output_folder_var.set(folder)
    
    def browse_dat_input(self):
        filename = filedialog.askopenfilename(title="Select DAT File")
        if filename:
            self.dat_input_var.set(filename)
            # Set default output filename
            self.dat_output_var.set(os.path.splitext(filename)[0] + ".csv")
    
    def browse_dat_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save CSV File", 
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.dat_output_var.set(filename)
    
    # Conversion methods
    def convert_block_file(self):
        try:
            input_file = self.block_input_var.get()
            if not input_file:
                messagebox.showerror("Error", "Please select an input file.")
                return
            
            output_file = self.block_output_var.get()
            if not output_file:
                messagebox.showerror("Error", "Please specify an output file.")
                return
            
            start_datetime_str = self.block_start_datetime_var.get()
            try:
                start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Error", "Invalid date/time format. Use YYYY-MM-DD HH:MM:SS.")
                return
            
            try:
                timestep = float(self.block_timestep_var.get())
            except ValueError:
                messagebox.showerror("Error", "Time step must be a number.")
                return
            
            # Get column names
            column_names = []
            if not self.block_autodetect_var.get():
                column_names_str = self.block_column_names_var.get()
                if column_names_str:
                    column_names = column_names_str.split()
            
            # Run conversion
            self.status_var.set("Converting block file...")
            
            # Create a custom logger that writes to our log widget
            def gui_logger(message):
                self.log(message)
            
            # Perform conversion
            try:
                block_data_processing.convert_blocks_to_csv(
                    input_file, 
                    output_file, 
                    start_datetime, 
                    timestep, 
                    column_names,
                    logger=gui_logger
                )
                self.status_var.set("Conversion complete!")
                messagebox.showinfo("Success", f"File converted successfully to {output_file}")
            except Exception as e:
                self.status_var.set("Error in conversion")
                messagebox.showerror("Conversion Error", str(e))
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))
    
    def convert_obs_file(self):
        try:
            input_file = self.obs_input_var.get()
            if not input_file:
                messagebox.showerror("Error", "Please select an input file.")
                return
            
            output_folder = self.obs_output_folder_var.get()
            if not output_folder:
                messagebox.showerror("Error", "Please specify an output folder.")
                return
            
            # Run conversion
            self.status_var.set("Converting OBS file...")
            
            # Create a custom logger that writes to our log widget
            def gui_logger(message):
                self.log(message)
            
            # Perform conversion
            try:
                created_files = obs_converter_core.convert_obs_to_csv(
                    input_file, 
                    output_folder, 
                    logger=gui_logger
                )
                self.status_var.set("Conversion complete!")
                messagebox.showinfo("Success", f"Created {len(created_files)} CSV files in {output_folder}")
            except Exception as e:
                self.status_var.set("Error in conversion")
                messagebox.showerror("Conversion Error", str(e))
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))
    
    def convert_dat_file(self):
        try:
            input_file = self.dat_input_var.get()
            if not input_file:
                messagebox.showerror("Error", "Please select an input file.")
                return
            
            output_file = self.dat_output_var.get()
            if not output_file:
                messagebox.showerror("Error", "Please specify an output file.")
                return
            
            start_datetime_str = self.dat_start_datetime_var.get()
            date_format = self.dat_date_format_var.get()
            
            try:
                # Validate date format by parsing the start date
                datetime.strptime(start_datetime_str, date_format)
            except ValueError:
                messagebox.showerror("Error", f"Invalid date format or date string. Format: {date_format}")
                return
            
            try:
                time_increment = self.dat_time_increment_var.get()
                int(time_increment)  # Validate that it's a number
            except ValueError:
                messagebox.showerror("Error", "Time increment must be a number.")
                return
            
            column_names_str = self.dat_column_names_var.get()
            
            # Run conversion
            self.status_var.set("Converting DAT file...")
            self.log(f"Converting DAT file: {input_file}")
            self.log(f"Output file: {output_file}")
            self.log(f"Start date: {start_datetime_str} (Format: {date_format})")
            self.log(f"Time increment: {time_increment} seconds")
            self.log(f"Column names: {column_names_str}")
            
            # Perform conversion
            try:
                dat_to_csv_processor.convert_dat_to_csv(
                    input_file,
                    output_file,
                    start_datetime_str,
                    date_format,
                    time_increment,
                    column_names_str
                )
                self.status_var.set("Conversion complete!")
                self.log("Conversion successful!")
                messagebox.showinfo("Success", f"File converted successfully to {output_file}")
            except Exception as e:
                self.status_var.set("Error in conversion")
                self.log(f"Error: {str(e)}")
                messagebox.showerror("Conversion Error", str(e))
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()