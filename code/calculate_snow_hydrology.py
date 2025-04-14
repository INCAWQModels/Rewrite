def calculate_snow_hydrology(
    input_timeseries,
    initial_snow_depth=0.0,
    melt_temperature=0.0,
    rainfall_temperature=0.0,
    snowfall_multiplier=1.0,
    rainfall_multiplier=1.0,
    melt_rate=3.0,
    output_name=None
):
    """
    Calculate rainfall, snowfall, snow depth, and snow melt from temperature and precipitation data.
    
    Parameters:
    -----------
    input_timeseries : TimeSeries
        A TimeSeries object containing 'air_temperature' and 'precipitation' columns
    initial_snow_depth : float, default=0.0
        Initial snow depth at time t=0
    melt_temperature : float, default=0.0
        Temperature threshold for snow melt to occur (°C)
    rainfall_temperature : float, default=0.0
        Temperature threshold for precipitation to fall as rain (°C)
    snowfall_multiplier : float, default=1.0
        Multiplier to adjust snowfall amounts
    rainfall_multiplier : float, default=1.0
        Multiplier to adjust rainfall amounts
    melt_rate : float, default=3.0
        Rate of snow melt per degree above melt temperature
    output_name : str, optional
        Name for output TimeSeries object (defaults to input name with "_hydrology" appended)
        
    Returns:
    --------
    TimeSeries
        A TimeSeries object containing 'rainfall', 'snowfall', 'snow_depth', and 'snow_melt' columns
    
    Raises:
    -------
    ValueError
        If input_timeseries doesn't contain required columns
    """
    from collections import defaultdict
    
    # Verify input TimeSeries has required columns
    required_columns = ['air_temperature', 'precipitation']
    for col in required_columns:
        if col not in input_timeseries.columns:
            raise ValueError(f"Input TimeSeries must contain '{col}' column")
    
    # Create output TimeSeries
    if output_name is None:
        if input_timeseries.name:
            output_name = f"{input_timeseries.name}_hydrology"
        else:
            output_name = "hydrology_results"
    
    output_ts = TimeSeries(output_name)
    
    # Add metadata
    model_parameters = {
        'initial_snow_depth': initial_snow_depth,
        'melt_temperature': melt_temperature,
        'rainfall_temperature': rainfall_temperature,
        'snowfall_multiplier': snowfall_multiplier,
        'rainfall_multiplier': rainfall_multiplier,
        'melt_rate': melt_rate
    }
    
    for key, value in model_parameters.items():
        output_ts.add_metadata(key, value)
    
    # Get indices for required columns
    temp_idx = input_timeseries.get_column_index('air_temperature')
    precip_idx = input_timeseries.get_column_index('precipitation')
    timestamp_idx = input_timeseries.get_column_index('timestamp')
    location_idx = input_timeseries.get_column_index('location')
    
    # Sort input data by timestamp to ensure proper time sequencing
    sorted_data = sorted(input_timeseries.data, key=lambda row: row[timestamp_idx])
    
    # Initialize results storage
    results = defaultdict(list)
    current_snow_depth = initial_snow_depth
    
    # Process each time step
    for i, row in enumerate(sorted_data):
        timestamp = row[timestamp_idx]
        location = row[location_idx]
        temperature = row[temp_idx]
        precipitation = row[precip_idx]
        
        # Skip if any required data is None
        if temperature is None or precipitation is None:
            continue
            
        # Calculate rainfall
        if temperature >= rainfall_temperature:
            rainfall = rainfall_multiplier * precipitation
        else:
            rainfall = 0.0
            
        # Calculate snowfall
        if temperature < rainfall_temperature:
            snowfall = snowfall_multiplier * precipitation
        else:
            snowfall = 0.0
            
        # Calculate snow melt
        melt_potential = max((temperature - melt_temperature), 0.0) * melt_rate
        snow_melt = min(current_snow_depth, melt_potential)
        
        # Update snow depth for next iteration
        new_snow_depth = current_snow_depth + snowfall - snow_melt
        
        # Add calculated values to results
        results['timestamp'].append(timestamp)
        results['location'].append(location)
        results['rainfall'].append(rainfall)
        results['snowfall'].append(snowfall)
        results['snow_depth'].append(current_snow_depth)  # Current snow depth (before update)
        results['snow_melt'].append(snow_melt)
        
        # Update current snow depth for next time step
        current_snow_depth = new_snow_depth
    
    # Add data to output TimeSeries
    for i in range(len(results['timestamp'])):
        # Create a dictionary of values for the current row
        values = {
            'rainfall': results['rainfall'][i],
            'snowfall': results['snowfall'][i],
            'snow_depth': results['snow_depth'][i],
            'snow_melt': results['snow_melt'][i]
        }
        
        # Add data to output TimeSeries
        output_ts.add_data(
            timestamp=results['timestamp'][i],
            location=results['location'][i],
            values=values
        )
    
    # Add source information to metadata
    output_ts.add_metadata('source_timeseries', input_timeseries.name if input_timeseries.name else 'unnamed')
    output_ts.add_metadata('creation_datetime', datetime.datetime.now().isoformat())
    
    return output_ts