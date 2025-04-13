"""
OBS to CSV Converter - Core Processing Module

This module provides core functionality to convert OBS files to CSV format.
It can be used as a standalone script or imported as a module.
"""

import os
import re
import csv
import datetime
import argparse
from collections import defaultdict


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
    
    # Use the command line interface
    sys.exit(main())