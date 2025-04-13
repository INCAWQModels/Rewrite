import datetime
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
    
    def __init__(self):
        """Initialize an empty TimeSeries object."""
        # Create an empty list for data rows
        self.data = []
        # Store column names
        self.columns = ["timestamp", "location"]
        # Create an empty dictionary for metadata
        self.metadata = {}
    
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
        timestamp_idx = self.columns.index("timestamp")
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
    
    def __str__(self):
        """Return a string representation of the TimeSeries object."""
        data_info = f"TimeSeries with {len(self.data)} rows and {len(self.columns)} columns"
        meta_info = f"Metadata: {len(self.metadata)} entries"
        column_info = f"Columns: {', '.join(self.columns)}"
        return f"{data_info}\n{column_info}\n{meta_info}"