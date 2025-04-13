import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from timeSeries import TimeSeries

def solar_declination(day_of_year):
    return 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

def solar_hour_angle(hour, longitude, timezone_offset):
    solar_time = hour + (longitude / 15) - timezone_offset
    return 15 * (solar_time - 12)

def solar_elevation_angle(lat, decl, hour_angle):
    lat_rad = math.radians(lat)
    decl_rad = math.radians(decl)
    ha_rad = math.radians(hour_angle)

    elevation = math.asin(
        math.sin(lat_rad) * math.sin(decl_rad) +
        math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad)
    )
    return math.degrees(elevation)

def extraterrestrial_radiation(day_of_year):
    G_sc = 1367  # W/m²
    return G_sc * (1 + 0.033 * math.cos(math.radians(360 * day_of_year / 365)))

def solar_radiation(dt, lat, longitude=0, timezone_offset=0):
    day_of_year = dt.timetuple().tm_yday
    hour = dt.hour + dt.minute / 60 + dt.second / 3600

    decl = solar_declination(day_of_year)
    ha = solar_hour_angle(hour, longitude, timezone_offset)
    elev = solar_elevation_angle(lat, decl, ha)

    if elev <= 0:
        return 0

    I_0 = extraterrestrial_radiation(day_of_year)
    transmittance = 0.75
    radiation = I_0 * transmittance * math.sin(math.radians(elev))
    return radiation

def compute_radiation_series(start_time, end_time, step_seconds, latitude, longitude, timezone_offset):
    current_time = start_time
    times = []
    radiation = []

    while current_time <= end_time:
        rad = solar_radiation(current_time, latitude, longitude, timezone_offset)
        times.append(current_time)
        radiation.append(rad)
        current_time += timedelta(seconds=step_seconds)

    return times, radiation

def compute_radiation_timeseries(start_time, end_time, step_seconds, latitude, longitude, timezone_offset, location_id="default"):
    """
    Compute solar radiation over a time period and return results as a TimeSeries object
    
    Args:
        start_time: datetime object, start of the computation period
        end_time: datetime object, end of the computation period
        step_seconds: int, time step in seconds
        latitude: float, latitude in degrees
        longitude: float, longitude in degrees
        timezone_offset: float, timezone offset from UTC in hours
        location_id: str, identifier for the location
        
    Returns:
        TimeSeries object with solar radiation data and metadata
    """
    # Calculate radiation values
    times, radiation_values = compute_radiation_series(start_time, end_time, step_seconds, 
                                                      latitude, longitude, timezone_offset)
    
    # Create TimeSeries object
    ts = TimeSeries()
    
    # Add metadata
    ts.add_metadata("latitude", str(latitude))
    ts.add_metadata("longitude", str(longitude))
    ts.add_metadata("source", "Python solar radiation model (solar_radiation.py)")
    ts.add_metadata("generation_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Add column for solar radiation
    ts.add_column("solar_radiation")
    
    # Add data to TimeSeries
    for i in range(len(times)):
        ts.add_data(times[i], location_id, [radiation_values[i]])
    
    return ts

def plot_radiation(times, radiation):
    hours_since_start = [(t - times[0]).total_seconds() / 3600 for t in times]

    plt.figure(figsize=(12, 6))
    plt.plot(hours_since_start, radiation, color='orange', linewidth=1.5)
    plt.fill_between(hours_since_start, radiation, color='orange', alpha=0.3)
    plt.title("Solar Radiation Over Time")
    plt.xlabel("Time (hours since start)")
    plt.ylabel("Solar Radiation (W/m²)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

def plot_timeseries_radiation(ts):
    """
    Plot radiation data from a TimeSeries object
    
    Args:
        ts: TimeSeries object containing solar radiation data
    """
    times = []
    radiation = []
    
    for row in ts.data:
        times.append(row[0])  # timestamp
        radiation.append(row[2])  # solar radiation value
    
    plot_radiation(times, radiation)

# Example usage
if __name__ == "__main__":
    # User input
    start_date_str = "2024-06-21 06:00:00"  # Summer solstice
    end_date_str = "2024-06-21 20:00:00"
    step_seconds = 300  # Every 5 minutes

    # Location info
    latitude = 40.0
    longitude = -105.0
    timezone_offset = -6  # e.g., MDT
    location_id = "Boulder"

    # Parse datetimes
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")

    # Original functionality
    times, radiation = compute_radiation_series(start_dt, end_dt, step_seconds, latitude, longitude, timezone_offset)
    
    # New functionality - create TimeSeries object
    ts = compute_radiation_timeseries(start_dt, end_dt, step_seconds, latitude, longitude, timezone_offset, location_id)
    
    # Print TimeSeries information
    print(ts)
    print("\nMetadata:")
    for key, value in ts.metadata.items():
        print(f"  {key}: {value}")
    
    # Print a sample of data
    print("\nSample of Solar Radiation Data:")
    for i, row in enumerate(ts.data[:5]):  # Print first 5 rows
        timestamp = row[0]
        location = row[1]
        solar_radiation = row[2]
        print(f"  {timestamp.strftime('%Y-%m-%d %H:%M:%S')} at {location}: {solar_radiation:.2f} W/m²")
    
    # Plot using the original function
    plot_radiation(times, radiation)
    
    # Plot using the TimeSeries function
    plot_timeseries_radiation(ts)