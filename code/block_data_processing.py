"""
Block Data Processing Module

This module provides core functionality to convert block-structured data files to CSV format.
It can be used as a standalone script or imported as a module.
"""

import os
import csv
import datetime
import argparse


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


def prompt_for_column_names(num_columns):
    """Prompt user for column names interactively"""
    column_names = []
    for i in range(num_columns):
        name = input(f"Enter name for column {i+1}: ")
        column_names.append(name.strip() if name.strip() else f"Column_{i+1}")
    return column_names


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
    
    # Use the command line interface
    sys.exit(main())