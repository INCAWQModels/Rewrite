import datetime
import math
from timeSeries import TimeSeries

def simulate_soil_temperature(
    input_timeseries,
    T_0=5.0,        # Initial soil temperature (°C)
    C_s=1.3e06,     # Soil heat capacity (J/m³/K)
    K_t=0.63,       # Thermal conductivity (W/m/K)
    C_ice=9.3e06,   # Ice heat capacity (J/m³/K)
    f_s=-3.3,       # Snow damping factor
    Z_s=0.5,        # Soil depth (m)
    T_ice=0.0,      # Critical ice temperature (°C)
    output_name=None
):
    """
    Simulate soil temperature based on air temperature and snow depth.
    
    Parameters:
    -----------
    input_timeseries : TimeSeries
        A TimeSeries object containing 'air_T' and 'snow_depth' columns
    T_0 : float, default=5.0
        Initial soil temperature (°C)
    C_s : float, default=1.3e06
        Soil heat capacity (J/m³/K)
    K_t : float, default=0.63
        Thermal conductivity (W/m/K)
    C_ice : float, default=9.3e06
        Ice heat capacity (J/m³/K)
    f_s : float, default=-3.3
        Snow damping factor
    Z_s : float, default=0.5
        Soil depth (m)
    T_ice : float, default=0.0
        Critical ice temperature (°C)
    output_name : str, optional
        Name for output TimeSeries object (defaults to input name with "_soil_temp" appended)
        
    Returns:
    --------
    TimeSeries
        A TimeSeries object containing 'soil_T' column with simulated soil temperatures
    
    Raises:
    -------
    ValueError
        If input_timeseries doesn't contain required columns
    """
    # Verify input TimeSeries has required columns
    required_columns = ['air_T', 'snow_depth']
    for col in required_columns:
        if col not in input_timeseries.columns:
            raise ValueError(f"Input TimeSeries must contain '{col}' column")
    
    # Create output TimeSeries
    if output_name is None:
        if input_timeseries.name:
            output_name = f"{input_timeseries.name}_soil_temp"
        else:
            output_name = "soil_temperature_results"
    
    output_ts = TimeSeries(output_name)
    
    # Add simulation parameters to metadata
    model_parameters = {
        'T_0': T_0,
        'C_s': C_s,
        'K_t': K_t,
        'C_ice': C_ice,
        'f_s': f_s,
        'Z_s': Z_s,
        'T_ice': T_ice
    }
    
    # Copy all metadata from input TimeSeries
    for key, value in input_timeseries.metadata.items():
        output_ts.add_metadata(key, value)
    
    # Add new simulation parameters to metadata
    for key, value in model_parameters.items():
        output_ts.add_metadata(key, value)
    
    # Get indices for required columns
    air_T_idx = input_timeseries.get_column_index('air_T')
    snow_depth_idx = input_timeseries.get_column_index('snow_depth')
    timestamp_idx = input_timeseries.get_column_index('timestamp')
    location_idx = input_timeseries.get_column_index('location')
    
    # Sort input data by timestamp to ensure proper time sequencing
    sorted_data = sorted(input_timeseries.data, key=lambda row: row[timestamp_idx])
    
    # Initialize soil temperature
    current_soil_T = T_0
    
    # Process each time step
    for i, row in enumerate(sorted_data):
        timestamp = row[timestamp_idx]
        location = row[location_idx]
        air_T = row[air_T_idx]
        snow_depth = row[snow_depth_idx]
        
        # Skip if any required data is None
        if air_T is None or snow_depth is None:
            continue
        
        # Calculate delta_T based on current soil temperature
        snow_effect = math.exp(f_s * snow_depth)
        
        if current_soil_T >= T_ice:
            # Above freezing case
            delta_T = snow_effect * (K_t / (C_s * (Z_s**2))) * (air_T - current_soil_T)
        else:
            # Below freezing case with ice effect
            delta_T = snow_effect * (K_t / ((C_s + C_ice) * (Z_s**2))) * (air_T - current_soil_T)
        
        # Update soil temperature for this time step
        current_soil_T = current_soil_T + delta_T
        
        # Add calculated soil temperature to output TimeSeries
        output_ts.add_data(
            timestamp=timestamp,
            location=location,
            values={'soil_T': current_soil_T}
        )
    
    # Add source information to metadata
    output_ts.add_metadata('source_timeseries', input_timeseries.name if input_timeseries.name else 'unnamed')
    output_ts.add_metadata('simulation_datetime', datetime.datetime.now().isoformat())
    
    return output_ts