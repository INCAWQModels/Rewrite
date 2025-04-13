import os
import sys
from datetime import datetime, timedelta

def convert_dat_to_csv(input_file, output_file, start_date_str, date_format, time_increment_str, column_names_str):
    """
    Convert a DAT file to CSV format with timestamp and column headers.
    
    Parameters:
    - input_file: Path to the input DAT file
    - output_file: Path to save the output CSV file
    - start_date_str: Start date/time as a string
    - date_format: Format string for parsing the start date
    - time_increment_str: Time increment in seconds between each data point
    - column_names_str: Comma-separated list of column names
    """
    try:
        # Parse parameters
        start_date = datetime.strptime(start_date_str, date_format)
        time_increment = int(time_increment_str)
        
        # Process column names
        if column_names_str.strip():
            column_headers = [name.strip() for name in column_names_str.split(',')]
        else:
            column_headers = []
        
        # Read the input DAT file
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # Clean and process the data
        data_values = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                values = [val.strip() for val in line.split()]
                if values:
                    data_values.append(values)
        
        # Write to CSV file
        with open(output_file, 'w') as f:
            # Write header row
            header = ["Timestamp"]
            if column_headers:
                header.extend(column_headers)
            else:
                # Generate column headers if not provided
                num_columns = max(len(row) for row in data_values) if data_values else 0
                header.extend([f"Column{i+1}" for i in range(num_columns)])
            
            f.write(','.join(header) + '\n')
            
            # Write data rows with timestamps
            current_time = start_date
            for i, values in enumerate(data_values):
                timestamp = current_time.strftime(date_format)
                row = [timestamp] + values
                f.write(','.join(row) + '\n')
                current_time += timedelta(seconds=time_increment)
        
        return True
        
    except Exception as e:
        raise Exception(f"Error in conversion process: {str(e)}")


# This is the compatibility function for the old module
def format_file_to_csv(input_file, output_file, start_date_str, date_format, time_increment_str, column_names_str):
    """
    Compatibility function for the original support_datTocsv.format_file_to_csv
    This ensures backward compatibility with existing code
    """
    return convert_dat_to_csv(
        input_file, 
        output_file, 
        start_date_str, 
        date_format, 
        time_increment_str, 
        column_names_str
    )