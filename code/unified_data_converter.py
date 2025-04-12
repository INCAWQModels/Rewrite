"""
Unified Data Converter Application

This module provides a GUI application that combines multiple data converter tools
into a single interface with tabs. Currently includes:
1. OBS to CSV Converter
2. Block Data to CSV Converter

Each converter can be used independently within its own tab.
"""

import os
import re
import csv
import datetime
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from collections import defaultdict


#############################
# OBS to CSV Converter Code #
#############################

def parse_obs_file(file_path, logger=None):
    """
    Parse an OBS file and extract location, parameter, and data information.
    
    Args:
        file_path (str): Path to the OBS file
        logger (callable, optional): Function to log messages
    
    Returns:
        dict: Dictionary where keys are parameters and values are lists of 
              (location, date_time, value) tuples
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    parameter_data = defaultdict(list)
    current_location = None
    current_parameter = None
    
    # Regular expressions for matching headers
    location_pattern = re.compile(r'^\*+\s*(.*?)\s*\*+')
    parameter_pattern = re.compile(r'^-+\s*(.*?)\s*-+')
    
    log(f"Reading file: {file_path}")
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            if not line:
                continue
                
            # Check if this is a location header
            location_match = location_pattern.match(line)
            if location_match:
                current_location = location_match.group(1)
                log(f"Found location: {current_location}")
                continue
                
            # Check if this is a parameter header
            parameter_match = parameter_pattern.match(line)
            if parameter_match:
                current_parameter = parameter_match.group(1)
                log(f"Found parameter: {current_parameter}")
                continue
                
            # If we have both a location and parameter, process data lines
            if current_location and current_parameter:
                # Split by tab or multiple spaces
                parts = re.split(r'\t+|\s{2,}', line)
                parts = [p.strip() for p in parts if p.strip()]
                
                # Check if we have enough parts to be a data line
                if len(parts) >= 2:
                    date_str = parts[0]
                    
                    # Check if we have a time component
                    if len(parts) >= 3 and ':' in parts[1]:
                        # Format with date and time
                        time_str = parts[1]
                        value_str = parts[2]
                    else:
                        # No time component - default to midnight
                        time_str = "00:00:00"
                        # The second part is the value
                        value_str = parts[1]
                    
                    # Try different date formats
                    try:
                        # Try DD/MM/YYYY format
                        date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                        date_time_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY format
                            date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M:%S")
                            date_time_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            try:
                                # Try YYYY-MM-DD format
                                date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                                date_time_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # If all formats fail, just use the original strings with added midnight time if needed
                                if ':' in time_str:
                                    date_time_str = f"{date_str} {time_str}"
                                else:
                                    date_time_str = f"{date_str} 00:00:00"
                    
                    # Store the data
                    parameter_data[current_parameter].append((current_location, date_time_str, value_str))
    
    log(f"File parsing complete. Found {len(parameter_data)} parameters.")
    
    # Log a summary of what was found
    log("\nParameters found:")
    for param, data in parameter_data.items():
        locations = set(loc for loc, _, _ in data)
        log(f"  - {param}: {len(data)} data points from {len(locations)} locations")
    
    return parameter_data


def write_csv_files(parameter_data, output_folder, logger=None):
    """
    Write one CSV file per parameter with data from all locations.
    
    Args:
        parameter_data (dict): Dictionary where keys are parameters and values are lists of 
                              (location, date_time, value) tuples
        output_folder (str): Folder to save the CSV files
        logger (callable, optional): Function to log messages
    
    Returns:
        list: List of paths to created CSV files
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    os.makedirs(output_folder, exist_ok=True)
    created_files = []
    
    for parameter, data_points in parameter_data.items():
        # Create a safe filename from the parameter
        safe_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', parameter)
        output_file = os.path.join(output_folder, f"{safe_param_name}.csv")
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(["Location", "DateTime", "Value"])
            
            # Write data
            for location, date_time, value in data_points:
                writer.writerow([location, date_time, value])
        
        log(f"Created {output_file} with {len(data_points)} data points")
        created_files.append(output_file)
    
    return created_files


def convert_obs_to_csv(input_file, output_folder, logger=None):
    """
    Main function to convert an OBS file to CSV files.
    
    Args:
        input_file (str): Path to the input OBS file
        output_folder (str): Folder to save the CSV files
        logger (callable, optional): Function to log messages
    
    Returns:
        list: List of paths to created CSV files
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: For any other errors during conversion
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    log(f"Starting conversion of {input_file}")
    log(f"Output folder: {output_folder}")
    
    # Parse the file
    parameter_data = parse_obs_file(input_file, logger)
    
    # Write CSV files
    created_files = write_csv_files(parameter_data, output_folder, logger)
    
    log("\nConversion completed successfully!")
    return created_files


#################################
# Block Data to CSV Converter Code #
#################################

def parse_block_file(file_path, logger=None):
    """
    Parse a block-structured file and extract block IDs and data rows.
    
    Args:
        file_path (str): Path to the input file
        logger (callable, optional): Function to log messages
    
    Returns:
        tuple: (num_blocks, block_data) where block_data is a list of tuples (block_id, data_rows)
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    log(f"Reading file: {file_path}")
    
    with open(file_path, 'r') as f:
        # Read first line to get number of blocks
        num_blocks = int(f.readline().strip())
        log(f"Found {num_blocks} blocks defined in file")
        
        blocks = []
        current_block_id = None
        current_block_data = []
        
        for line in f:
            line = line.strip()
            
            if not line:
                continue
                
            # Split the line by tabs or spaces
            parts = line.split()
            
            # If we have a block ID (only one column) and we've already seen a block before,
            # store the previous block and start a new one
            if len(parts) == 1 and current_block_id is not None:
                blocks.append((current_block_id, current_block_data))
                current_block_data = []
                current_block_id = parts[0]
                log(f"Found block ID: {current_block_id}")
            # If we have a block ID and this is the first block
            elif len(parts) == 1:
                current_block_id = parts[0]
                log(f"Found block ID: {current_block_id}")
            # Otherwise it's a data row
            else:
                # Convert all parts to float if possible
                try:
                    data_row = [float(part) for part in parts]
                    current_block_data.append(data_row)
                except ValueError:
                    log(f"Warning: Could not parse line as data: {line}")
        
        # Don't forget to add the last block
        if current_block_id is not None:
            blocks.append((current_block_id, current_block_data))
    
    log(f"File parsing complete. Found {len(blocks)} blocks.")
    
    # Verify all blocks have the same number of columns in their data rows
    if blocks:
        first_block_cols = len(blocks[0][1][0]) if blocks[0][1] else 0
        
        for block_id, block_data in blocks:
            for i, row in enumerate(block_data):
                if len(row) != first_block_cols:
                    log(f"Warning: Block {block_id}, row {i+1} has {len(row)} columns, expected {first_block_cols}")
    
    return num_blocks, blocks


def generate_timestamps(start_datetime, timestep_seconds, num_rows):
    """
    Generate timestamps based on start datetime and timestep
    
    Args:
        start_datetime (datetime): Starting date and time
        timestep_seconds (float): Time step in seconds
        num_rows (int): Number of timestamps to generate
    
    Returns:
        list: List of datetime strings in format 'YYYY-MM-DD HH:MM:SS'
    """
    timestamps = []
    current_time = start_datetime
    
    for _ in range(num_rows):
        timestamps.append(current_time.strftime('%Y-%m-%d %H:%M:%S'))
        current_time += datetime.timedelta(seconds=timestep_seconds)
    
    return timestamps


def convert_blocks_to_csv(
    input_file, 
    output_file, 
    start_datetime,
    timestep_seconds,
    column_names,
    logger=None
):
    """
    Main function to convert a block data file to CSV format.
    
    Args:
        input_file (str): Path to the input file
        output_file (str): Path to save the CSV file
        start_datetime (datetime): Starting date and time
        timestep_seconds (float): Time step in seconds
        column_names (list): List of names for the data columns
        logger (callable, optional): Function to log messages
    
    Returns:
        str: Path to created CSV file
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: For any other errors during conversion
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    log(f"Starting conversion of {input_file}")
    log(f"Output file: {output_file}")
    log(f"Start datetime: {start_datetime}")
    log(f"Timestep: {timestep_seconds} seconds")
    log(f"Column names: {column_names}")
    
    # Parse the block file
    num_expected_blocks, blocks = parse_block_file(input_file, logger)
    
    # Verify that we found the expected number of blocks
    if len(blocks) != num_expected_blocks:
        log(f"Warning: Found {len(blocks)} blocks, but file header specified {num_expected_blocks}")
    
    # Determine number of data columns from the first block
    if blocks and blocks[0][1]:
        num_data_columns = len(blocks[0][1][0])
        
        # Check if the provided column names match
        if len(column_names) != num_data_columns:
            log(f"Warning: {len(column_names)} column names provided, but data has {num_data_columns} columns")
            
            # Adjust column names if necessary
            if len(column_names) < num_data_columns:
                # Add generic column names if too few were provided
                for i in range(len(column_names), num_data_columns):
                    column_names.append(f"Column_{i+1}")
                log(f"Added generic column names: {column_names}")
            else:
                # Truncate if too many were provided
                column_names = column_names[:num_data_columns]
                log(f"Using first {num_data_columns} column names: {column_names}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ['DateTime', 'BlockID'] + column_names
        writer.writerow(header)
        
        # Process each block
        for block_id, block_data in blocks:
            # Generate timestamps for this block
            timestamps = generate_timestamps(
                start_datetime, timestep_seconds, len(block_data)
            )
            
            # Write each data row with its timestamp and block ID
            for i, data_row in enumerate(block_data):
                row = [timestamps[i], block_id] + data_row
                writer.writerow(row)
            
            # Update start_datetime for the next block
            start_datetime += datetime.timedelta(seconds=timestep_seconds * len(block_data))
        
    log(f"Created CSV file: {output_file}")
    return output_file


#######################
# Unified GUI Classes #
#######################

class ObsToCSVTab:
    """Tab for OBS to CSV Converter"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        
        # Setup variables
        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        self.status_message = tk.StringVar(value="Ready")
        
        # Create the UI elements
        self.create_input_section()
        self.create_output_section()
        self.create_log_section()
        self.create_buttons()
        self.create_status_bar()
    
    def create_input_section(self):
        # Input file section
        input_frame = ttk.LabelFrame(self.frame, text="Input File", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="OBS File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        input_frame.columnconfigure(1, weight=1)
    
    def create_output_section(self):
        # Output folder section
        output_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="Output Folder:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_folder).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        output_frame.columnconfigure(1, weight=1)
    
    def create_log_section(self):
        # Log section
        log_frame = ttk.LabelFrame(self.frame, text="Conversion Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create text widget with scrollbar for log
        self.log_text = tk.Text(log_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def create_buttons(self):
        # Buttons section
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Convert", command=self.run_conversion, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        # Status bar at the bottom
        status_bar = ttk.Frame(self.frame, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_bar, textvariable=self.status_message).pack(side=tk.LEFT, padx=5)
    
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
        self.parent.update_idletasks()  # Update the UI
    
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


class BlockDataToCSVTab:
    """Tab for Block Data to CSV Converter"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent, padding="20")
        
        # Setup variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.start_date = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        self.start_time = tk.StringVar(value="00:00:00")
        self.timestep = tk.StringVar(value="60")
        self.column_names = tk.StringVar()
        self.status_message = tk.StringVar(value="Ready")
        
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
        input_frame = ttk.LabelFrame(self.frame, text="Input File", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Block Data File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(input_frame, text="Browse...", command=self.browse_input_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        input_frame.columnconfigure(1, weight=1)
    
    def create_output_section(self):
        # Output file section
        output_frame = ttk.LabelFrame(self.frame, text="Output File", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="CSV File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Make the entry column expandable
        output_frame.columnconfigure(1, weight=1)
    
    def create_datetime_section(self):
        # Date and time settings
        datetime_frame = ttk.LabelFrame(self.frame, text="Date and Time Settings", padding="10")
        datetime_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start date
        ttk.Label(datetime_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(datetime_frame, textvariable=self.start_date, width=15).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Start time
        ttk.Label(datetime_frame, text="Start Time (HH:MM:SS):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Entry(datetime_frame, textvariable=self.start_time, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Timestep
        ttk.Label(datetime_frame, text="Timestep (seconds):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(datetime_frame, textvariable=self.timestep, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
    def create_columns_section(self):
        # Column names section
        columns_frame = ttk.LabelFrame(self.frame, text="Column Names", padding="10")
        columns_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(columns_frame, text="Column Names (comma-separated):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(columns_frame, textvariable=self.column_names, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        # Example
        ttk.Label(columns_frame, text="Example: Temperature,Pressure,Humidity").grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Make the entry column expandable
        columns_frame.columnconfigure(1, weight=1)
    
    def create_log_section(self):
        # Log section
        log_frame = ttk.LabelFrame(self.frame, text="Conversion Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create text widget with scrollbar for log
        self.log_text = tk.Text(log_frame, height=10, width=80, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def create_buttons(self):
        # Buttons section
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="Convert", command=self.run_conversion, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self):
        # Status bar at the bottom
        status_bar = ttk.Frame(self.frame, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(status_bar, textvariable=self.status_message).pack(side=tk.LEFT, padx=5)
    
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select Block Data file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Set a default output file based on the input file
            base = os.path.splitext(filename)[0]
            self.output_file.set(base + ".csv")
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save CSV file as",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def clear_log(self):
        self.log_text.delete("1.0", tk.END)
    
    def open_output_folder(self):
        output_file = self.output_file.get()
        if output_file:
            folder = os.path.dirname(output_file)
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
            messagebox.showinfo("Info", "Please select an output file first.")
    
    def log(self