import os
import sys
from datetime import datetime, timedelta
from timeSeries import TimeSeries

def convert_dat_to_timeseries(input_file, output_base_name, start_date_str, date_format, time_increment_str, column_names_str, location_id="default"):
    """
    Convert a DAT file to TimeSeries format and save it as CSV and JSON.
    
    Parameters:
    - input_file: Path to the input DAT file
    - output_base_name: Base name for output files (without extension)
    - start_date_str: Start date/time as a string
    - date_format: Format string for parsing the start date
    - time_increment_str: Time increment in seconds between each data point
    - column_names_str: Comma-separated list of column names
    - location_id: Location identifier for the time series (default: "default")
    
    Returns:
    - tuple: Paths to the created CSV and JSON files
    """
    try:
        # Parse parameters
        start_date = datetime.strptime(start_date_str, date_format)
        time_increment = int(time_increment_str)
        
        # Process column names
        if column_names_str.strip():
            column_names = [name.strip() for name in column_names_str.split(',')]
        else:
            column_names = []
        
        # Read the input DAT file
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # Clean and process the data
        data_values = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                values = [float(val.strip()) for val in line.split()]
                if values:
                    data_values.append(values)
        
        # Create a TimeSeries object
        ts = TimeSeries(name=output_base_name)
        
        # Add metadata about the conversion
        ts.add_metadata("source_file", input_file)
        ts.add_metadata("conversion_date", datetime.now().isoformat())
        ts.add_metadata("start_date", start_date.isoformat())
        ts.add_metadata("time_increment_seconds", time_increment)
        
        # Generate column headers if not provided
        if not column_names:
            num_columns = max(len(row) for row in data_values) if data_values else 0
            column_names = [f"value{i+1}" for i in range(num_columns)]
        
        # Add columns to TimeSeries
        for col_name in column_names:
            ts.add_column(col_name)
        
        # Add data to TimeSeries
        current_time = start_date
        for values in data_values:
            # Create a dictionary of values with corresponding column names
            values_dict = {}
            for i, value in enumerate(values):
                if i < len(column_names):
                    values_dict[column_names[i]] = value
            
            # Add data point to TimeSeries
            ts.add_data(current_time, location_id, values_dict)
            
            # Increment time for next data point
            current_time += timedelta(seconds=time_increment)
        
        # Save the TimeSeries to CSV and JSON files
        csv_path, json_path = ts.save_to_files(output_base_name)
        
        return csv_path, json_path
        
    except Exception as e:
        raise Exception(f"Error in conversion process: {str(e)}")


# This is the compatibility function for the old module
def format_file_to_csv(input_file, output_file, start_date_str, date_format, time_increment_str, column_names_str):
    """
    Compatibility function for the original support_datTocsv.format_file_to_csv
    This ensures backward compatibility with existing code
    
    Now uses the TimeSeries class internally, but maintains the original interface
    """
    # Extract base name from output_file (remove extension)
    output_base_name = os.path.splitext(output_file)[0]
    
    # Use the new conversion function
    csv_path, _ = convert_dat_to_timeseries(
        input_file, 
        output_base_name, 
        start_date_str, 
        date_format, 
        time_increment_str, 
        column_names_str
    )
    
    # For compatibility, we should ensure the output file has the exact name requested
    if csv_path != output_file:
        os.rename(csv_path, output_file)
        
    return True


if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) < 5:
        print("Usage: python dat_to_timeseries_processor.py input.dat output_base_name start_date date_format [time_increment] [column_names] [location_id]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_base_name = sys.argv[2]
    start_date_str = sys.argv[3]
    date_format = sys.argv[4]
    
    # Optional parameters
    time_increment_str = sys.argv[5] if len(sys.argv) > 5 else "1"
    column_names_str = sys.argv[6] if len(sys.argv) > 6 else ""
    location_id = sys.argv[7] if len(sys.argv) > 7 else "default"
    
    try:
        csv_path, json_path = convert_dat_to_timeseries(
            input_file,
            output_base_name,
            start_date_str,
            date_format,
            time_increment_str,
            column_names_str,
            location_id
        )
        print(f"Conversion successful!")
        print(f"CSV file created: {csv_path}")
        print(f"JSON file created: {json_path}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
