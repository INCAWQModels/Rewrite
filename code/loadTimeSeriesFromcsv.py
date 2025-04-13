import csv
import datetime
import re

# Import the TimeSeries class
# Assuming the TimeSeries class is defined in a file named 'time_series.py'
from timeSeries import TimeSeries

def load_timeseries_from_csv(csv_filename, timestamp_format="%Y-%m-%d %H:%M:%S", 
                           timestamp_col=0, location_col=1, header=True, 
                           metadata_rows=0):
    """
    Load data from a CSV file into a TimeSeries object.
    If hours, minutes, and seconds are not specified in the timestamp,
    they default to 00:00:00.
    
    Parameters:
    csv_filename (str): Path to the CSV file
    timestamp_format (str): Format string for parsing the timestamp column
    timestamp_col (int): Index of the timestamp column (default is 0)
    location_col (int): Index of the location column (default is 1)
    header (bool): Whether the CSV file has a header row
    metadata_rows (int): Number of rows at the beginning of the file containing metadata
                         in the format "key,value"
    
    Returns:
    TimeSeries: A populated TimeSeries object
    """
    # Create an empty TimeSeries object
    ts = TimeSeries()
    
    # Open and read the CSV file
    with open(csv_filename, 'r', newline='') as csv_file:
        # Read metadata if specified
        for _ in range(metadata_rows):
            if csv_file.readable():
                line = csv_file.readline().strip()
                if ',' in line:
                    key, value = line.split(',', 1)
                    ts.add_metadata(key.strip(), value.strip())
        
        # Create a CSV reader
        csv_reader = csv.reader(csv_file)
        
        # Process header if present
        columns = []
        if header:
            try:
                columns = next(csv_reader)
                # If we have fewer than timestamp_col + 1 or location_col + 1 columns,
                # we can't proceed
                if len(columns) <= max(timestamp_col, location_col):
                    raise ValueError("CSV header does not have enough columns for timestamp and location")
            except StopIteration:
                raise ValueError("CSV file is empty or contains only metadata")
        
        # Set columns in TimeSeries object
        if columns:
            ts.columns = ["timestamp", "location"]  # Start with required columns
            for i, col in enumerate(columns):
                if i != timestamp_col and i != location_col:
                    ts.add_column(col)
        
        # Process data rows
        for row in csv_reader:
            if len(row) <= max(timestamp_col, location_col):
                # Skip rows that don't have enough data
                continue
            
            # Parse timestamp
            timestamp_str = row[timestamp_col].strip()
            
            # Check if the timestamp has time components
            has_time = re.search(r'[0-2]?\d:[0-5]?\d(:[0-5]?\d)?', timestamp_str) is not None
            
            try:
                if has_time:
                    # Use the provided format if time components are present
                    timestamp = datetime.datetime.strptime(timestamp_str, timestamp_format)
                else:
                    # If no time components, try parsing as date only and add 00:00:00
                    # Detect the date format based on the input
                    if '-' in timestamp_str:
                        # Assuming YYYY-MM-DD or similar
                        date_parts = timestamp_str.split('-')
                        if len(date_parts) == 3:
                            if len(date_parts[0]) == 4:  # YYYY-MM-DD
                                date_format = "%Y-%m-%d"
                            else:  # DD-MM-YYYY or MM-DD-YYYY
                                date_format = "%d-%m-%Y" if int(date_parts[0]) <= 31 else "%m-%d-%Y"
                    elif '/' in timestamp_str:
                        # Assuming MM/DD/YYYY or DD/MM/YYYY or similar
                        date_parts = timestamp_str.split('/')
                        if len(date_parts) == 3:
                            if len(date_parts[2]) == 4:  # MM/DD/YYYY or DD/MM/YYYY
                                date_format = "%m/%d/%Y" if int(date_parts[0]) <= 12 else "%d/%m/%Y"
                            else:  # YYYY/MM/DD
                                date_format = "%Y/%m/%d"
                    else:
                        # Try the date part of the provided format
                        date_format = timestamp_format.split(' ')[0]
                    
                    # Parse the date and combine with default time (00:00:00)
                    date_obj = datetime.datetime.strptime(timestamp_str, date_format)
                    timestamp = datetime.datetime.combine(date_obj.date(), datetime.time(0, 0, 0))
            except ValueError:
                # Skip rows with invalid timestamps
                continue
            
            # Get location
            location = row[location_col]
            
            # Collect numeric values
            values = []
            for i, val in enumerate(row):
                if i != timestamp_col and i != location_col:
                    # Try to convert to numeric if possible
                    try:
                        values.append(float(val))
                    except ValueError:
                        values.append(None)  # Use None for non-numeric values
            
            # Add to TimeSeries
            ts.add_data(timestamp, location, values)
    
    return ts


def save_timeseries_to_csv(ts, csv_filename, timestamp_format="%Y-%m-%d %H:%M:%S", 
                         include_metadata=True):
    """
    Save a TimeSeries object to a CSV file.
    
    Parameters:
    ts (TimeSeries): The TimeSeries object to save
    csv_filename (str): Path to the output CSV file
    timestamp_format (str): Format string for formatting the timestamp column
    include_metadata (bool): Whether to include metadata at the beginning of the file
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        with open(csv_filename, 'w', newline='') as csv_file:
            # Write metadata if requested
            if include_metadata and ts.metadata:
                for key, value in ts.metadata.items():
                    csv_file.write(f"{key},{value}\n")
            
            # Create CSV writer
            csv_writer = csv.writer(csv_file)
            
            # Write header
            csv_writer.writerow(ts.columns)
            
            # Write data
            timestamp_idx = ts.get_column_index("timestamp")
            
            for row in ts.data:
                # Format timestamp
                row_copy = row.copy()
                if timestamp_idx < len(row_copy) and isinstance(row_copy[timestamp_idx], datetime.datetime):
                    row_copy[timestamp_idx] = row_copy[timestamp_idx].strftime(timestamp_format)
                
                csv_writer.writerow(row_copy)
        
        return True
    except Exception as e:
        print(f"Error saving TimeSeries to CSV: {e}")
        return False


# Example usage:
if __name__ == "__main__":
    # Example: Create a simple CSV file with both date-only and datetime formats
    with open("example_data.csv", "w", newline="") as f:
        f.write("metadata_key,metadata_value\n")
        f.write("source,sensor_network\n")
        f.write("timestamp,location,temperature,humidity,pressure\n")
        f.write("2023-01-01,site_1,22.5,45.2,1013.2\n")  # Date only - should default to 00:00:00
        f.write("2023-01-02 12:30:00,site_1,23.1,44.8,1013.0\n")  # With time specified
        f.write("2023-01-03,site_2,21.8,47.5,1012.8\n")  # Date only - should default to 00:00:00
        f.write("2023-01-04 09:15:30,site_2,22.0,48.1,1012.5\n")  # With time specified
    
    # Load the data
    ts = load_timeseries_from_csv("example_data.csv", metadata_rows=2)
    
    # Print information about the loaded TimeSeries
    print(ts)
    print("Metadata:", ts.metadata)
    
    # Print all timestamps to verify default time values
    for i, row in enumerate(ts.data):
        print(f"Row {i+1} timestamp: {row[0]} (from location: {row[1]})")
    
    # Save to a new CSV file
    save_timeseries_to_csv(ts, "output_data.csv")