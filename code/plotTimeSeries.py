import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def plot_timeseries(ts, title=None, figsize=(12, 6), save_path=None, exclude_columns=None):
    """
    Plot all data columns in a TimeSeries object against time.
    
    Parameters:
    ts (TimeSeries): The TimeSeries object to plot
    title (str, optional): Title for the plot
    figsize (tuple, optional): Figure size as (width, height) in inches
    save_path (str, optional): Path to save the figure
    exclude_columns (list, optional): List of column names to exclude from plotting
    
    Returns:
    matplotlib.figure.Figure: The created figure object
    """
    if exclude_columns is None:
        exclude_columns = []
    
    # Always exclude timestamp and location columns
    exclude_columns.extend(["timestamp", "location"])
    
    # Convert data to dictionary
    data_dict = ts.to_dict()
    
    # Get timestamps
    timestamps = data_dict["timestamp"]
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Determine which columns to plot
    plot_columns = [col for col in ts.columns if col not in exclude_columns]
    
    # Plot each column
    for column in plot_columns:
        if column in data_dict:
            # Skip columns with no data or non-numeric data
            if all(val is None or not (isinstance(val, (int, float))) for val in data_dict[column]):
                continue
                
            # Replace None values with NaN for plotting
            values = [float('nan') if val is None else val for val in data_dict[column]]
            ax.plot(timestamps, values, label=column, marker='.', linestyle='-', alpha=0.8)
    
    # Format the plot
    if title:
        ax.set_title(title)
    else:
        location_info = ""
        if "location" in data_dict and data_dict["location"]:
            unique_locations = set(data_dict["location"])
            if len(unique_locations) == 1:
                location_info = f" for {next(iter(unique_locations))}"
            
        ax.set_title(f"Time Series Data{location_info}")
        
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    
    # Format x-axis with date formatter
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()  # Rotate date labels
    
    # Add a grid
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Add legend if we have multiple columns
    if len(plot_columns) > 1:
        ax.legend(loc='best')
    
    # Add metadata as text in the figure
    if ts.metadata:
        metadata_text = "\n".join([f"{key}: {value}" for key, value in ts.metadata.items()])
        plt.figtext(0.02, 0.02, metadata_text, fontsize=8, wrap=True)
    
    plt.tight_layout()
    
    # Save the figure if a path is provided
    if save_path:
        plt.savefig(save_path)
    
    return fig

def plot_timeseries_by_location(ts, title=None, figsize=(12, 6), save_path=None):
    """
    Plot data for each location in a separate subplot.
    
    Parameters:
    ts (TimeSeries): The TimeSeries object to plot
    title (str, optional): Title for the overall figure
    figsize (tuple, optional): Figure size as (width, height) in inches
    save_path (str, optional): Path to save the figure
    
    Returns:
    matplotlib.figure.Figure: The created figure object
    """
    # Get all unique locations
    locations = set(row[1] for row in ts.data)
    num_locations = len(locations)
    
    if num_locations == 0:
        return None
    
    # Create a figure with subplots for each location
    fig, axes = plt.subplots(num_locations, 1, figsize=figsize, sharex=True)
    
    # Handle the case where there's only one location
    if num_locations == 1:
        axes = [axes]
    
    # Plot data for each location
    for ax, location in zip(axes, locations):
        # Filter data for this location
        location_data = ts.get_data_by_location(location)
        
        # Extract timestamp and data values
        timestamps = [row[0] for row in location_data]
        
        # Plot each data column (starting from index 2 to skip timestamp and location)
        for i in range(2, len(ts.columns)):
            column_name = ts.columns[i]
            values = [row[i] if i < len(row) else None for row in location_data]
            
            # Skip columns with no data or non-numeric data
            if all(val is None or not (isinstance(val, (int, float))) for val in values):
                continue
                
            # Replace None values with NaN for plotting
            values = [float('nan') if val is None else val for val in values]
            ax.plot(timestamps, values, label=column_name, marker='.', linestyle='-', alpha=0.8)
        
        # Set labels and title for this subplot
        ax.set_title(f"Location: {location}")
        ax.set_ylabel("Value")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='best')
    
    # Set common x-axis label
    axes[-1].set_xlabel("Time")
    
    # Format x-axis with date formatter
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    fig.autofmt_xdate()  # Rotate date labels
    
    # Set overall title if provided
    if title:
        fig.suptitle(title, fontsize=14)
    
    # Add metadata as text in the figure
    if ts.metadata:
        metadata_text = "\n".join([f"{key}: {value}" for key, value in ts.metadata.items()])
        plt.figtext(0.02, 0.02, metadata_text, fontsize=8, wrap=True)
    
    plt.tight_layout()
    
    # Save the figure if a path is provided
    if save_path:
        plt.savefig(save_path)
    
    return fig

# Example usage
if __name__ == "__main__":
    from timeSeries import TimeSeries
    import datetime
    
    # Create a sample TimeSeries
    ts = TimeSeries()
    
    # Add metadata
    ts.add_metadata("source", "Example data")
    ts.add_metadata("created", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Add columns
    ts.add_column("temperature")
    ts.add_column("humidity")
    
    # Add data
    base_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
    for i in range(48):
        timestamp = base_time + datetime.timedelta(hours=i)
        # Simulate temperature between 15-25°C
        temp = 20 + 5 * math.sin(i * math.pi / 12)
        # Simulate humidity between 40-80%
        humidity = 60 + 20 * math.cos(i * math.pi / 8)
        
        location = "Station A" if i % 2 == 0 else "Station B"
        ts.add_data(timestamp, location, [temp, humidity])
    
    # Plot all data
    plot_timeseries(ts, title="Weather Data Time Series")
    
    # Plot data by location
    plot_timeseries_by_location(ts, title="Weather Data by Location")
    
    plt.show()