import datetime
import math
import timeSeries

def calculate_pet(solar_ts, temp_ts, method="priestley-taylor", solar_column="solar_radiation", 
                 temp_column="air_temperature", jh_offset=3.0, scaling_factor=1.0):
    """
    Calculate Potential Evapotranspiration (PET) using either the Priestley-Taylor method
    or the Jensen-Haise McGuinness method with customizable parameters.
    
    Parameters:
    solar_ts (TimeSeries): Input time series object containing solar radiation data
    temp_ts (TimeSeries): Input time series object containing air temperature data
    method (str): Method to use for PET calculation - 'priestley-taylor' or 'jensen-haise'
    solar_column (str): Name of the column containing solar radiation values (W/m²)
    temp_column (str): Name of the column containing temperature values (°C)
    jh_offset (float): Temperature offset parameter for Jensen-Haise McGuinness formula (default 3.0)
    scaling_factor (float): Empirical scaling factor to apply to all PET values (default 1.0)
    
    Returns:
    TimeSeries: A new time series object with PET values (mm/day)
    """
    # Validate method
    valid_methods = ["priestley-taylor", "jensen-haise"]
    if method.lower() not in valid_methods:
        raise ValueError(f"Invalid method '{method}'. Valid options are: {', '.join(valid_methods)}")
    
    # Set method name for metadata
    method_name = "Priestley Taylor" if method.lower() == "priestley-taylor" else "Jensen-Haise McGuinness"
    
    # Create a new TimeSeries object for the output
    output_ts = timeSeries.TimeSeries()
    
    # Get latitude from solar time series metadata
    if "latitude" not in solar_ts.metadata:
        raise ValueError("Latitude not found in solar radiation time series metadata")
    
    latitude_deg = solar_ts.metadata["latitude"]
    
    # Copy metadata from input solar timeseries
    for key, value in solar_ts.metadata.items():
        output_ts.add_metadata(key, value)
    
    # Set the method metadata
    output_ts.add_metadata("method", method_name)
    
    # Add the scaling factor to metadata
    output_ts.add_metadata("scaling_factor", scaling_factor)
    
    # Add Jensen-Haise offset to metadata if using that method
    if method.lower() == "jensen-haise":
        output_ts.add_metadata("offset", jh_offset)
    
    # Get indices for required columns in solar time series
    try:
        timestamp_idx_solar = solar_ts.columns.index("timestamp")
        location_idx_solar = solar_ts.columns.index("location")
        solar_idx = solar_ts.columns.index(solar_column)
    except ValueError as e:
        raise ValueError(f"Required column not found in solar time series: {e}")
    
    # Get indices for required columns in temperature time series
    try:
        timestamp_idx_temp = temp_ts.columns.index("timestamp")
        location_idx_temp = temp_ts.columns.index("location")
        temp_idx = temp_ts.columns.index(temp_column)
    except ValueError as e:
        raise ValueError(f"Required column not found in temperature time series: {e}")
    
    # Create a lookup dictionary for temperature data for easy matching
    temp_lookup = {}
    for row in temp_ts.data:
        timestamp = row[timestamp_idx_temp]
        location = row[location_idx_temp]
        temperature = row[temp_idx]
        
        # Create a unique key from timestamp and location
        key = (timestamp, location)
        temp_lookup[key] = temperature
    
    # Process each data point from solar radiation time series
    for row in solar_ts.data:
        timestamp = row[timestamp_idx_solar]
        location = row[location_idx_solar]
        solar_radiation = row[solar_idx]
        
        # Create key to look up corresponding temperature
        key = (timestamp, location)
        temperature = temp_lookup.get(key)
        
        # Calculate PET if both solar radiation and temperature are available
        if solar_radiation is not None and temperature is not None:
            # Calculate day of year (DOY)
            doy = timestamp.timetuple().tm_yday
            
            # Convert latitude to radians
            lat_rad = math.radians(latitude_deg)
            
            # Calculate solar declination (radians)
            solar_declination = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
            
            # Calculate sunset hour angle (radians)
            sunset_angle = math.acos(-math.tan(lat_rad) * math.tan(solar_declination))
            
            # Calculate extraterrestrial radiation (Ra) in MJ/m²/day
            dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)  # inverse relative distance Earth-Sun
            ra = 24 * 60 / math.pi * 0.0820 * dr * (
                sunset_angle * math.sin(lat_rad) * math.sin(solar_declination) +
                math.cos(lat_rad) * math.cos(solar_declination) * math.sin(sunset_angle)
            )
            
            # Convert solar radiation from W/m² to MJ/m²/day
            rs = solar_radiation * 0.0864
            
            # Calculate PET based on selected method
            if method.lower() == "priestley-taylor":
                # Calculate net radiation (Rn) - simplified approach
                rn = 0.77 * rs
                
                # Calculate saturation vapor pressure slope (Delta) in kPa/°C
                delta = 4098 * (0.6108 * math.exp((17.27 * temperature) / (temperature + 237.3))) / ((temperature + 237.3) ** 2)
                
                # Calculate psychrometric constant (gamma) in kPa/°C
                gamma = 0.067
                
                # Calculate PET using Priestley-Taylor equation (mm/day)
                alpha_pt = 1.26  # Priestley-Taylor coefficient
                pet = alpha_pt * (delta / (delta + gamma)) * (rn * 0.408)  # 0.408 converts MJ/m²/day to mm/day
                
            else:  # Jensen-Haise McGuinness
                # Constants for Jensen-Haise McGuinness
                ct = 0.025  # Temperature coefficient
                
                # Convert temperature to Celsius if not already
                temp_c = temperature
                
                # Calculate PET using Jensen-Haise McGuinness equation with user-specified offset (mm/day)
                # PET = Rs * Ct * (T + offset)
                pet = rs * ct * (temp_c + jh_offset)
            
            # Apply the scaling factor
            pet *= scaling_factor
                
            # Add data to output timeseries
            output_ts.add_data(timestamp, location, {"pet_mm_day": pet})
        else:
            # Handle missing data
            output_ts.add_data(timestamp, location, {"pet_mm_day": None})
    
    return output_ts