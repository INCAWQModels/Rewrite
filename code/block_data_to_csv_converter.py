"""
Block Data to CSV Converter

This module provides functionality to convert block-structured data files to CSV format.
It can be used as a standalone script, imported as a module,
or accessed through a GUI interface.
"""

import os
import csv
import datetime
import argparse
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog


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


class BlockDataConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Data to CSV Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Setup variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
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
        output_frame = ttk.LabelFrame(self.main_frame, text="Output File", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_frame, text="CSV File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_file, width=50).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_file).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
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
        ttk.Entry(datetime_frame, textvariable=self.timestep, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
    
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
    
    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Scroll to the end
        self.root.update_idletasks()  # Update the UI
    
    def validate_inputs(self):
        """Validate all user inputs"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input file.")
            return False
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output CSV file.")
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
        output_file = self.output_file.get()
        
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
        self.log(f"Output file: {output_file}")
        self.log(f"Start datetime: {start_datetime}")
        self.log(f"Timestep: {timestep_seconds} seconds")
        self.log(f"Column names: {column_names}")
        
        try:
            convert_blocks_to_csv(
                input_file, 
                output_file, 
                start_datetime, 
                timestep_seconds, 
                column_names,
                self.log
            )
            
            self.status_message.set("Conversion completed")
            self.log("Conversion completed successfully!")
            
            messagebox.showinfo("Success", f"Conversion completed successfully!\nCSV file saved to: {output_file}")
            
        except Exception as e:
            self.log(f"Error during conversion: {str(e)}")
            self.status_message.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred during conversion:\n{str(e)}")


def prompt_for_column_names(num_columns):
    """Prompt user for column names interactively"""
    column_names = []
    for i in range(num_columns):
        name = input(f"Enter name for column {i+1}: ")
        column_names.append(name.strip() if name.strip() else f"Column_{i+1}")
    return column_names


def run_gui():
    """Launch the GUI application"""
    root = tk.Tk()
    app = BlockDataConverterGUI(root)
    root.mainloop()


def main():
    """Command line interface for the converter"""
    parser = argparse.ArgumentParser(description='Convert block-structured data files to CSV')
    parser.add_argument('input_file', help='Path to the input data file')
    parser.add_argument('--output-file', '-o', help='Path to the output CSV file')
    parser.add_argument('--start-datetime', '-d', default=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        help='Start date and time in format "YYYY-MM-DD HH:MM:SS"')
    parser.add_argument('--timestep', '-t', type=float, default=60, 
                        help='Time step in seconds between data points')
    parser.add_argument('--column-names', '-c', nargs='+', 
                        help='Names for the data columns (space-separated)')
    parser.add_argument('--interactive', '-i', action='store_true', 
                        help='Prompt for column names interactively')
    
    args = parser.parse_args()
    
    try:
        # Set default output file if not specified
        if not args.output_file:
            args.output_file = os.path.splitext(args.input_file)[0] + ".csv"
        
        # Parse the start datetime
        start_datetime = datetime.datetime.strptime(args.start_datetime, "%Y-%m-%d %H:%M:%S")
        
        # Get column names
        if args.interactive:
            # First, peek at the file to determine number of columns
            num_blocks, blocks = parse_block_file(args.input_file)
            if blocks and blocks[0][1]:
                num_columns = len(blocks[0][1][0])
                column_names = prompt_for_column_names(num_columns)
            else:
                print("Error: Could not determine number of columns from file.")
                return 1
        else:
            column_names = args.column_names if args.column_names else []
        
        # Run the conversion
        convert_blocks_to_csv(
            args.input_file, 
            args.output_file, 
            start_datetime, 
            args.timestep, 
            column_names
        )
        
        print(f"Conversion complete! CSV file saved to: {args.output_file}")
        
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