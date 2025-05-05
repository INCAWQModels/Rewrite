import datetime
import csv
import json
import uuid
from collections import defaultdict

class TimeSeries:
    """
    A class to represent time series data with associated metadata.
    
    The class contains two main data structures:
    1. A two-dimensional data table where:
       - First column: Python datetime (year, month, day, hour, minute, second)
       - Second column: Location identifier
       - Third+ columns: Numeric data values
    2. A dictionary for storing metadata about the time series
    """
    
    def __init__(self, name=None):
        """
        Initialize an empty TimeSeries object.
        
        Parameters:
        name (str, optional): Name of the TimeSeries object
        """
        # Create an empty list for data rows
        self.data = []
        # Generate a UUID and store it in metadata
        self.uuid = str(uuid.uuid4())
        # Store column names - use UUID as the header for timestamp column
        self.columns = [self.uuid, "location"]
        # Create an empty dictionary for metadata
        self.metadata = {}
        # Store the UUID in metadata
        self.metadata["uuid"] = self.uuid
        # Set the name of the TimeSeries object
        self.name = name
    
    def add_column(self, column_name):
        """
        Add a new column to the data structure.
        
        Parameters:
        column_name (str): The name of the new column
        """
        if column_name not in self.columns:
            self.columns.append(column_name)
            # Fill existing rows with None for the new column
            for row in self.data:
                if len(row) < len(self.columns):
                    row.extend([None] * (len(self.columns) - len(row)))
    
    def add_data(self, timestamp, location, values):
        """
        Add a new row of data to the time series.
        
        Parameters:
        timestamp (datetime): The timestamp for the data point
        location (str): The location identifier
        values (list or dict): The numeric values to add
        """
        if not isinstance(timestamp, datetime.datetime):
            raise TypeError("timestamp must be a datetime object")
        
        # Create a new row with timestamp and location
        new_row = [timestamp, location]
        
        # Add the values
        if isinstance(values, dict):
            # Ensure all columns exist
            for col_name in values.keys():
                if col_name not in self.columns:
                    self.add_column(col_name)
            
            # Fill the row with values in the correct positions
            new_row = [None] * len(self.columns)
            new_row[0] = timestamp
            new_row[1] = location
            
            for col_name, value in values.items():
                col_index = self.columns.index(col_name)
                new_row[col_index] = value
                
        elif isinstance(values, list):
            # Add new columns if needed
            for i in range(len(values)):
                col_name = f"value{i+1}"
                if col_name not in self.columns:
                    self.add_column(col_name)
            
            # Extend new_row with values
            new_row.extend(values)
            
            # Pad with None if needed
            if len(new_row) < len(self.columns):
                new_row.extend([None] * (len(self.columns) - len(new_row)))
        else:
            raise TypeError("values must be a list or dictionary")
        
        # Append the new row to the data
        self.data.append(new_row)
    
    def add_metadata(self, key, value):
        """
        Add a metadata key-value pair.
        
        Parameters:
        key: The metadata key
        value: The metadata value
        """
        self.metadata[key] = value
    
    def get_data_by_location(self, location):
        """
        Filter data by location.
        
        Parameters:
        location: The location identifier to filter by
        
        Returns:
        list: Filtered data rows for the specified location
        """
        location_idx = self.columns.index("location")
        return [row for row in self.data if row[location_idx] == location]
    
    def get_data_by_timerange(self, start_time, end_time):
        """
        Filter data by time range.
        
        Parameters:
        start_time (datetime): The start time of the range
        end_time (datetime): The end time of the range
        
        Returns:
        list: Filtered data rows for the specified time range
        """
        timestamp_idx = 0  # First column is always timestamp
        return [row for row in self.data 
                if start_time <= row[timestamp_idx] <= end_time]
    
    def get_column_index(self, column_name):
        """
        Get the index of a column by name.
        
        Parameters:
        column_name (str): The name of the column
        
        Returns:
        int: The index of the column
        """
        try:
            return self.columns.index(column_name)
        except ValueError:
            raise ValueError(f"Column '{column_name}' not found")
    
    def to_dict(self):
        """
        Convert the data to a dictionary format.
        
        Returns:
        dict: A dictionary where keys are column names and values are lists of column values
        """
        result = defaultdict(list)
        
        for row in self.data:
            for i, col_name in enumerate(self.columns):
                if i < len(row):
                    result[col_name].append(row[i])
                else:
                    result[col_name].append(None)
                    
        return dict(result)
    
    def save_to_files(self, name=None):
        """
        Save the TimeSeries data to CSV and metadata to JSON files.
        
        Parameters:
        name (str, optional): Base name for the output files. If not provided, 
                             uses the TimeSeries object's name attribute.
                             
        Returns:
        tuple: Paths to the created CSV and JSON files
        
        Raises:
        ValueError: If no name is provided and the TimeSeries object has no name
        """
        # Determine the base name for files
        base_name = name or self.name
        if not base_name:
            raise ValueError("No name provided for output files and TimeSeries object has no name")
        
        # Create filenames
        csv_filename = f"{base_name}.csv"
        json_filename = f"{base_name}.json"
        
        # Save data to CSV
        with open(csv_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(self.columns)
            # Write data rows with datetime objects converted to ISO format strings
            for row in self.data:
                formatted_row = []
                for i, value in enumerate(row):
                    if i == 0 and isinstance(value, datetime.datetime):  # Convert timestamp
                        formatted_row.append(value.isoformat())
                    else:
                        formatted_row.append(value)
                writer.writerow(formatted_row)
        
        # Save metadata to JSON
        with open(json_filename, 'w') as jsonfile:
            json.dump(self.metadata, jsonfile, indent=4)
        
        return csv_filename, json_filename
    
    def __str__(self):
        """Return a string representation of the TimeSeries object."""
        name_info = f"TimeSeries '{self.name}'" if self.name else "Unnamed TimeSeries"
        data_info = f"with {len(self.data)} rows and {len(self.columns)} columns"
        meta_info = f"Metadata: {len(self.metadata)} entries"
        column_info = f"Columns: {', '.join(self.columns)}"
        return f"{name_info} {data_info}\n{column_info}\n{meta_info}"
    
    @staticmethod
    def merge(ts1, ts2, name=None):
        """
        Merge two TimeSeries objects into a new one.
        
        This function creates a "backbone" of all timestamp/location combinations
        from both input TimeSeries, and merges their data columns and metadata.
        
        Parameters:
        ts1 (TimeSeries): First TimeSeries object
        ts2 (TimeSeries): Second TimeSeries object
        name (str, optional): Name for the merged TimeSeries
        
        Returns:
        TimeSeries: A new TimeSeries object containing merged data
        """
        if not isinstance(ts1, TimeSeries) or not isinstance(ts2, TimeSeries):
            raise TypeError("Both arguments must be TimeSeries objects")
        
        # Create a new TimeSeries object (with a new UUID)
        merged_ts = TimeSeries(name)
        
        # Store original UUIDs in metadata with source prefix keys
        if "uuid" in ts1.metadata:
            merged_ts.add_metadata("source_uuid_1", ts1.metadata["uuid"])
        if "uuid" in ts2.metadata:
            merged_ts.add_metadata("source_uuid_2", ts2.metadata["uuid"])
        
        # Merge metadata (skip "uuid" keys from original datasets as they're already stored)
        for key, value in ts1.metadata.items():
            if key != "uuid":
                merged_ts.add_metadata(key, value)
        for key, value in ts2.metadata.items():
            if key != "uuid":
                merged_ts.add_metadata(key, value)
        
        # Create a set of all column names (excluding timestamp and location)
        data_columns = set()
        for col in ts1.columns[2:]:  # Skip timestamp and location
            data_columns.add(col)
        for col in ts2.columns[2:]:  # Skip timestamp and location
            data_columns.add(col)
        
        # Add all columns to the merged TimeSeries
        for col in data_columns:
            merged_ts.add_column(col)
        
        # Create a dictionary to store data points by (timestamp, location) tuple
        data_points = {}
        
        # Process data from ts1
        timestamp_idx1 = 0  # First column is always timestamp
        location_idx1 = ts1.columns.index("location")
        
        for row in ts1.data:
            timestamp = row[timestamp_idx1]
            location = row[location_idx1]
            key = (timestamp, location)
            
            # Create a dictionary to hold the values for this row
            if key not in data_points:
                data_points[key] = {col: None for col in data_columns}
            
            # Add values from this row to the data_points dictionary
            for i, col_name in enumerate(ts1.columns):
                if i > 1:  # Skip timestamp and location
                    if i < len(row):
                        data_points[key][col_name] = row[i]
        
        # Process data from ts2 (similarly)
        timestamp_idx2 = 0  # First column is always timestamp
        location_idx2 = ts2.columns.index("location")
        
        for row in ts2.data:
            timestamp = row[timestamp_idx2]
            location = row[location_idx2]
            key = (timestamp, location)
            
            # Create or update the dictionary for this timestamp-location pair
            if key not in data_points:
                data_points[key] = {col: None for col in data_columns}
            
            # Add values from this row to the data_points dictionary
            for i, col_name in enumerate(ts2.columns):
                if i > 1:  # Skip timestamp and location
                    if i < len(row) and row[i] is not None:
                        data_points[key][col_name] = row[i]
        
        # Add all the data points to the merged TimeSeries
        for (timestamp, location), values in data_points.items():
            merged_ts.add_data(timestamp, location, values)
        
        return merged_ts