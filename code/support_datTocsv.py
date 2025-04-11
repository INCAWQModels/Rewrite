import csv
import datetime
import argparse
import json

def format_file_to_csv(input_file, output_file, start_date_value, date_format, time_increment_seconds, column_names):
    """
    Convert the input file to CSV format with a date column and subcatchment identifier.
    
    Args:
        input_file: Path to input data file
        output_file: Path for output CSV file
        start_date_value: Starting date value in format matching date_format
        date_format: Python date format string (e.g., "%Y-%m-%d %H:%M:%S")
        time_increment_seconds: Time increment in seconds
        column_names: List of column names for the data columns
    """
    # Parse the start date
    start_date = datetime.datetime.strptime(start_date_value, date_format)
    time_increment = datetime.timedelta(seconds=int(time_increment_seconds))
    
    # Read the input file
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Parse the header information
    rows_per_subcatchment = int(lines[0].strip())
    num_subcatchments = int(lines[1].strip())
    
    # If column_names is provided as a string, convert it to a list
    if isinstance(column_names, str):
        try:
            column_names = json.loads(column_names)
        except json.JSONDecodeError:
            # If not valid JSON, treat as a comma-separated string
            column_names = [name.strip() for name in column_names.split(',')]
    
    # Process data
    current_date = start_date
    output_data = []
    
    line_index = 2  # Start after the header information
    
    while line_index < len(lines):
        line = lines[line_index].strip()
        
        # Check if this is a subcatchment identifier line (like C01, C02, etc.)
        if line and line[0] == 'C':
            subcatchment_id = line
            line_index += 1
            
            # Process the rows for this subcatchment
            subcatchment_row_count = 0
            while subcatchment_row_count < rows_per_subcatchment and line_index < len(lines):
                data_line = lines[line_index].strip()
                
                # Skip if we've reached another subcatchment identifier
                if data_line and data_line[0] == 'C':
                    break
                
                # Skip empty lines
                if not data_line:
                    line_index += 1
                    continue
                
                # Parse the values (assuming tab-separated)
                values = data_line.split('\t')
                # Filter out empty strings that might come from trailing tabs
                values = [v for v in values if v]
                
                if values:  # Ensure we have data
                    # Create a row with date and subcatchment ID
                    row = [current_date.strftime(date_format), subcatchment_id]
                    
                    # Add all available values
                    row.extend(values)
                    
                    # Add to output data
                    output_data.append(row)
                    
                    # Increment the date
                    current_date += time_increment
                    subcatchment_row_count += 1
                
                line_index += 1
        else:
            line_index += 1
    
    # Determine the maximum number of columns in the data
    max_cols = max(len(row) for row in output_data) - 2  # Subtract 2 for date and subcatchment columns
    
    # Ensure we have enough column names
    while len(column_names) < max_cols:
        column_names.append(f"Value{len(column_names)+1}")
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Create header row with Date, Subcatchment, and the column names
        header = ['Date', 'Subcatchment'] + column_names[:max_cols]
        writer.writerow(header)
        
        # Write data rows
        writer.writerows(output_data)
    
    print(f"Successfully converted {input_file} to {output_file}")
    print(f"Added {len(output_data)} rows with dates starting from {start_date_value}")
    print(f"Date format: {date_format}")
    print(f"Time increment: {time_increment_seconds} seconds")
    print(f"Number of data columns detected: {max_cols}")
    print(f"Column names used: {', '.join(header)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert data file to CSV with date column')
    parser.add_argument('input_file', help='Path to the input data file')
    parser.add_argument('output_file', help='Path for the output CSV file')
    parser.add_argument('start_date_value', help='Start date value (e.g., "2025-04-11 00:00:00")')
    parser.add_argument('date_format', help='Python date format string (e.g., "%%Y-%%m-%%d %%H:%%M:%%S")')
    parser.add_argument('time_increment_seconds', type=int, help='Time increment in seconds')
    parser.add_argument('column_names', help='Comma-separated string of column names for data values')
    
    args = parser.parse_args()
    
    format_file_to_csv(
        args.input_file, 
        args.output_file, 
        args.start_date_value, 
        args.date_format, 
        args.time_increment_seconds,
        args.column_names
    )