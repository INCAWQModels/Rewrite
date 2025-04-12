"""
OBS to CSV Converter

This module provides functionality to convert OBS files to CSV format.
It can be used as a standalone script, imported as a module,
or accessed through a GUI interface.
"""

import os
import re
import csv
import datetime
import argparse
from collections import defaultdict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


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
    app = ObsToCSVConverterGUI(root)
    root.mainloop()


def main():
    """Command line interface for the converter"""
    parser = argparse.ArgumentParser(description='Convert OBS files to CSV files by parameter')
    parser.add_argument('input_file', help='Path to the input OBS file')
    parser.add_argument('--output-folder', '-o', default='output', help='Folder to save CSV files')
    
    args = parser.parse_args()
    
    try:
        convert_obs_to_csv(args.input_file, args.output_folder)
        print("Conversion complete!")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    
    # If no arguments are provided, launch the GUI
    if len(sys.argv) == 1:
        run_gui()
    else:
        # Otherwise, use the command line interface
        sys.exit(main())