"""
OBS to TimeSeries Converter - Core Processing Module

This module provides core functionality to convert OBS files to TimeSeries format.
It can be used as a standalone script or imported as a module.
"""

import os
import re
import csv
import datetime
import argparse
from collections import defaultdict
from timeSeries import TimeSeries


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
                    except ValueError:
                        try:
                            # Try MM/DD/YYYY format
                            date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %H:%M:%S")
                        except ValueError:
                            try:
                                # Try YYYY-MM-DD format
                                date_obj = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # If all formats fail, log warning and skip the line
                                log(f"Warning: Could not parse date '{date_str} {time_str}' - skipping line")
                                continue
                    
                    try:
                        # Convert value to float if possible
                        value = float(value_str)
                    except ValueError:
                        log(f"Warning: Non-numeric value '{value_str}' for parameter '{current_parameter}' - using as string")
                        value = value_str
                    
                    # Store the data with parsed datetime object
                    parameter_data[current_parameter].append((current_location, date_obj, value))
    
    log(f"File parsing complete. Found {len(parameter_data)} parameters.")
    
    # Log a summary of what was found
    log("\nParameters found:")
    for param, data in parameter_data.items():
        locations = set(loc for loc, _, _ in data)
        log(f"  - {param}: {len(data)} data points from {len(locations)} locations")
    
    return parameter_data


def create_timeseries_objects(parameter_data, base_name, logger=None):
    """
    Create TimeSeries objects for each parameter.
    
    Args:
        parameter_data (dict): Dictionary where keys are parameters and values are lists of 
                              (location, date_time, value) tuples
        base_name (str): Base name for the TimeSeries objects
        logger (callable, optional): Function to log messages
    
    Returns:
        dict: Dictionary where keys are parameters and values are TimeSeries objects
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    timeseries_dict = {}
    
    for parameter, data_points in parameter_data.items():
        # Create a safe name from the parameter
        safe_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', parameter)
        ts_name = f"{base_name}_{safe_param_name}"
        
        # Create a TimeSeries object
        ts = TimeSeries(name=ts_name)
        
        # Add metadata
        ts.add_metadata("parameter", parameter)
        ts.add_metadata("creation_date", datetime.datetime.now().isoformat())
        ts.add_metadata("source_type", "OBS File")
        ts.add_metadata("num_data_points", len(data_points))
        
        # Add data points
        # First, add the parameter as a column
        ts.add_column(safe_param_name)
        
        # Add data points
        for location, timestamp, value in data_points:
            ts.add_data(timestamp, location, {safe_param_name: value})
        
        log(f"Created TimeSeries '{ts_name}' with {len(data_points)} data points")
        timeseries_dict[parameter] = ts
    
    return timeseries_dict


def save_timeseries_files(timeseries_dict, output_folder, logger=None):
    """
    Save TimeSeries objects to CSV and JSON files.
    
    Args:
        timeseries_dict (dict): Dictionary where keys are parameters and values are TimeSeries objects
        output_folder (str): Folder to save the files
        logger (callable, optional): Function to log messages
    
    Returns:
        list: List of tuples with (parameter, csv_path, json_path)
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    os.makedirs(output_folder, exist_ok=True)
    created_files = []
    
    for parameter, ts in timeseries_dict.items():
        # Create a safe filename from the parameter
        safe_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', parameter)
        output_base = os.path.join(output_folder, safe_param_name)
        
        # Save the TimeSeries
        csv_path, json_path = ts.save_to_files(output_base)
        
        log(f"Saved TimeSeries for '{parameter}':")
        log(f"  - CSV: {csv_path}")
        log(f"  - JSON: {json_path}")
        
        created_files.append((parameter, csv_path, json_path))
    
    return created_files


def convert_obs_to_timeseries(input_file, output_folder, logger=None):
    """
    Main function to convert an OBS file to TimeSeries format.
    
    Args:
        input_file (str): Path to the input OBS file
        output_folder (str): Folder to save the TimeSeries files
        logger (callable, optional): Function to log messages
    
    Returns:
        list: List of tuples with (parameter, csv_path, json_path)
    
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
    
    # Get the base name from the input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Create TimeSeries objects
    timeseries_dict = create_timeseries_objects(parameter_data, base_name, logger)
    
    # Save TimeSeries files
    created_files = save_timeseries_files(timeseries_dict, output_folder, logger)
    
    log("\nConversion completed successfully!")
    return created_files


def get_merged_timeseries(input_file, parameter=None, logger=None):
    """
    Create a single merged TimeSeries object from an OBS file, 
    optionally filtering for a specific parameter.
    
    Args:
        input_file (str): Path to the input OBS file
        parameter (str, optional): Parameter to filter for. If None, all parameters included.
        logger (callable, optional): Function to log messages
    
    Returns:
        TimeSeries: A TimeSeries object containing the data
    
    Raises:
        FileNotFoundError: If the input file doesn't exist
        Exception: For any other errors during conversion
    """
    def log(message):
        if logger:
            logger(message)
        else:
            print(message)
    
    # Parse the file
    parameter_data = parse_obs_file(input_file, logger)
    
    # Get the base name from the input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Create a merged TimeSeries object
    merged_ts = TimeSeries(name=f"{base_name}_merged")
    
    # Add metadata
    merged_ts.add_metadata("source_file", input_file)
    merged_ts.add_metadata("creation_date", datetime.datetime.now().isoformat())
    merged_ts.add_metadata("source_type", "OBS File")
    
    # Filter parameters if requested
    if parameter:
        if parameter in parameter_data:
            parameter_data = {parameter: parameter_data[parameter]}
            log(f"Filtered data for parameter: {parameter}")
        else:
            log(f"Warning: Parameter '{parameter}' not found in file")
            return merged_ts
    
    # Add parameters as columns
    for param in parameter_data.keys():
        safe_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', param)
        merged_ts.add_column(safe_param_name)
        merged_ts.add_metadata(f"parameter_{safe_param_name}", param)
    
    # Add data points
    for param, data_points in parameter_data.items():
        safe_param_name = re.sub(r'[^a-zA-Z0-9_-]', '_', param)
        for location, timestamp, value in data_points:
            merged_ts.add_data(timestamp, location, {safe_param_name: value})
    
    # Count total data points
    total_points = sum(len(data) for data in parameter_data.values())
    merged_ts.add_metadata("num_data_points", total_points)
    merged_ts.add_metadata("num_parameters", len(parameter_data))
    
    log(f"Created merged TimeSeries with {total_points} data points from {len(parameter_data)} parameters")
    return merged_ts


def main():
    """Command line interface for the converter"""
    parser = argparse.ArgumentParser(description='Convert OBS files to TimeSeries format')
    parser.add_argument('input_file', help='Path to the input OBS file')
    parser.add_argument('--output-folder', '-o', default='output', help='Folder to save TimeSeries files')
    parser.add_argument('--merge', '-m', action='store_true', help='Create a single merged TimeSeries file with all parameters')
    parser.add_argument('--parameter', '-p', help='Filter for a specific parameter (for use with --merge)')
    
    args = parser.parse_args()
    
    try:
        # Make sure output folder exists
        os.makedirs(args.output_folder, exist_ok=True)
        
        if args.merge:
            # Create a merged TimeSeries
            log_prefix = f"Merging OBS file for parameter '{args.parameter}'" if args.parameter else "Merging OBS file for all parameters"
            print(f"{log_prefix}...")
            merged_ts = get_merged_timeseries(args.input_file, args.parameter)
            
            # Save merged TimeSeries
            base_name = os.path.splitext(os.path.basename(args.input_file))[0]
            suffix = f"_{args.parameter}" if args.parameter else "_merged"
            output_base = os.path.join(args.output_folder, f"{base_name}{suffix}")
            
            csv_path, json_path = merged_ts.save_to_files(output_base)
            
            print(f"Created merged TimeSeries files:")
            print(f"  - CSV: {csv_path}")
            print(f"  - JSON: {json_path}")
        else:
            # Convert to separate TimeSeries objects for each parameter
            print(f"Converting OBS file to separate TimeSeries files...")
            created_files = convert_obs_to_timeseries(args.input_file, args.output_folder)
            
            print(f"\nCreated {len(created_files)} TimeSeries files:")
            for param, csv_path, json_path in created_files:
                print(f"  - {param}:")
                print(f"    - CSV: {csv_path}")
                print(f"    - JSON: {json_path}")
            
        print("\nConversion complete!")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    
    # Use the command line interface
    sys.exit(main())