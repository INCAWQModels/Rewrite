"""
Block Data to TimeSeries Processing Module

This module provides core functionality to convert block-structured data files to TimeSeries format.
It can be used as a standalone script or imported as a module.
"""

import os
import csv
import datetime
import argparse
from timeSeries import TimeSeries


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


def convert_blocks_to_timeseries(
    input_file, 
    output_base_name, 
    start_datetime,
    timestep_seconds,
    column_names,
    logger=None
):
    """
    Main function to convert a block data file to TimeSeries format.
    
    Args:
        input_file (str): Path to the input file
        output_base_name (str): Base name for output files (without extension)
        start_datetime (datetime): Starting date and time
        timestep_seconds (float): Time step in seconds
        column_names (list): List of names for the data columns
        logger (callable, optional): Function to log messages
    
    Returns:
        tuple: Paths to created CSV and JSON files
    
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
    log(f"Output base name: {output_base_name}")
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
                    column_names.append(f"value{i+1}")
                log(f"Added generic column names: {column_names}")
            else:
                # Truncate if too many were provided
                column_names = column_names[:num_data_columns]
                log(f"Using first {num_data_columns} column names: {column_names}")
    
    # Create a TimeSeries object
    ts = TimeSeries(name=output_base_name)
    
    # Add metadata about the conversion
    ts.add_metadata("source_file", input_file)
    ts.add_metadata("conversion_date", datetime.datetime.now().isoformat())
    ts.add_metadata("start_datetime", start_datetime.isoformat())
    ts.add_metadata("timestep_seconds", timestep_seconds)
    ts.add_metadata("expected_blocks", num_expected_blocks)
    ts.add_metadata("actual_blocks", len(blocks))
    
    # Add the column names to the TimeSeries
    for column_name in column_names:
        ts.add_column(column_name)
    
    # Process each block
    current_time = start_datetime
    
    for block_id, block_data in blocks:
        for data_row in block_data:
            # Create a dictionary of values with corresponding column names
            values_dict = {}
            for i, value in enumerate(data_row):
                if i < len(column_names):
                    values_dict[column_names[i]] = value
            
            # Add data point to TimeSeries using the block_id as the location
            ts.add_data(current_time, block_id, values_dict)
            
            # Increment time for next data point
            current_time += datetime.timedelta(seconds=timestep_seconds)
    
    # Save the TimeSeries to CSV and JSON files
    csv_path, json_path = ts.save_to_files(output_base_name)
    
    log(f"Created TimeSeries files: {csv_path}, {json_path}")
    return csv_path, json_path


def prompt_for_column_names(num_columns):
    """Prompt user for column names interactively"""
    column_names = []
    for i in range(num_columns):
        name = input(f"Enter name for column {i+1}: ")
        column_names.append(name.strip() if name.strip() else f"value{i+1}")
    return column_names


def main():
    """Command line interface for the converter"""
    parser = argparse.ArgumentParser(description='Convert block-structured data files to TimeSeries format')
    parser.add_argument('input_file', help='Path to the input data file')
    parser.add_argument('--output-base', '-o', help='Base name for output files (without extension)')
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
        # Set default output base name if not specified
        if not args.output_base:
            args.output_base = os.path.splitext(os.path.basename(args.input_file))[0]
        
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
        csv_path, json_path = convert_blocks_to_timeseries(
            args.input_file, 
            args.output_base, 
            start_datetime, 
            args.timestep, 
            column_names
        )
        
        print(f"Conversion complete!")
        print(f"CSV file saved to: {csv_path}")
        print(f"JSON file saved to: {json_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    
    # Use the command line interface
    sys.exit(main())