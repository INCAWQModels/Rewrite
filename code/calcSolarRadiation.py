from math import sin, cos, acos, tan, radians, degrees, pi, log10, exp
from csv import DictWriter
from calendar import isleap
from datetime import date
import datetime
import json
"""Python code to calculate solar radiation prted from INCA SQL code. Original equations are based on those presented in
Mousavi Maleki, S. A., Hizam, H., & Gomes, C. (2017). Estimation of hourly, daily and monthly global solar radiation on inclined surfaces: Models re-visited. Energies, 10(1), 134.
"""

def calculateSunriseAndSunset(in_date, latitudeInDegrees, longitudeInDegrees):
    """
    Calculate sunrise and sunset times
    
    Args:
        in_date: datetime object representing a calendar day
        latitudeInDegrees: float, latitude in degrees
        longitudeInDegrees: float, longitude in degrees
        
    Returns:
        dict with sunrise and sunset times in minutes from midnight
    """
    latitudeInRadians = radians(latitudeInDegrees)
    longitudeInRadians = radians(longitudeInDegrees)

    # Get day of year (0-based)
    #day_of_year = in_date.timetuple().tm_yday - 1
    targetYear=in_date.year
    january_first = datetime.date(in_date.year, 1, 1)
    
    # Calculate the difference in days
    dayOfYear = (in_date - january_first).days

    # Get days in year
    if (isleap(targetYear)): 
    #if in_date.year % 4 == 0 and (in_date.year % 100 != 0 or in_date.year % 400 == 0):
        daysInYear = 366
    else:
        daysInYear = 365
        
    # Calculate gamma (day angle)
    gamma = 2.0 * pi * dayOfYear / daysInYear
    
    # Calculate equation of time
    eqtime = (229.18 * (0.000075 + 0.001868 * cos(gamma)
              - 0.032077 * sin(gamma) - 0.014615 * cos(2.0 * gamma)
              - 0.040849 * sin(2.0 * gamma)))
    
    # Calculate declination
    decl = (0.006918 - 0.399912 * cos(gamma) + 0.070257 * sin(gamma)
           - 0.006758 * cos(2.0 * gamma) + 0.000907 * sin(2.0 * gamma)
           - 0.002697 * cos(3.0 * gamma) + 0.00148 * sin(3.0 * gamma))
    
    # Hour angle
    hourAngle = (
        (acos((cos(radians(90.833)) / (cos(latitudeInRadians)
          * cos(decl))) - tan(latitudeInRadians)
          * tan(decl))) 
          #* (180.0 / pi)
          )
    
    # Calculate sunrise and sunset in minutes from midnight
    out_sunrise = (720.0 + 4.0 * degrees(longitudeInRadians - hourAngle) - eqtime)
    out_sunset =  (720.0 + 4.0 * degrees(longitudeInRadians + hourAngle) - eqtime)
    
    return {'date': in_date, 'sunrise': out_sunrise, 'sunset': out_sunset}

def calculateSolarRadiation(in_date, in_sunrise, in_sunset, latitudeInRadians, longitudeInRadians, in_count=0):
    """
    Calculate solar radiation at a specific time
    
    Args:
        in_date: datetime object
        in_sunrise: float, sunrise time in minutes from midnight
        in_sunset: float, sunset time in minutes from midnight
        in_latitude: float, latitude in degrees
        in_longitude: float, longitude in degrees
        in_count: int, count of valid measurements
        
    Returns:
        dict with solar radiation value and updated count
    """
    # Get day of year (0-based)
    julian_day = in_date.timetuple().tm_yday - 1
    
    # Calculate time fraction in minutes from midnight
    time_fraction = in_date.hour * 60.0 + in_date.minute
    
    srad = 0.0
    
    # Only calculate solar radiation during daylight
    if time_fraction > in_sunrise and time_fraction < in_sunset:
        # Hour angle in radians
        houra = 2.0 * pi * time_fraction / (24.0 * 60.0)
        
        # Get days in year
        if in_date.year % 4 == 0 and (in_date.year % 100 != 0 or in_date.year % 400 == 0):
            days_in_year = 366
        else:
            days_in_year = 365
        
        dec2 = radians(360.0 * julian_day / days_in_year)
        dec1 = radians(0.39637 - 22.9133 * cos(dec2) + 4.02543 * sin(dec2) \
               - 0.3872 * cos(2.0 * dec2) + 0.052 * sin(2.0 * dec2))
        
        #check the requirement that soleLV be a small positive number
        soleLV = min( sin(latitudeInRadians) * sin(dec1) - cos(latitudeInRadians) * cos(dec1) * cos(houra), 0.005 )
        
        am = 1.0 / soleLV
        aa = 0.128 - 0.054 * log10(am)
        ae = exp(-3.0 * aa * am)
        srad = 1378.0 * soleLV * ae
        
        in_count += 1
    
    return {'srad': srad, 'count': in_count}

def calculateSolarRadiationTimeSeries(in_latitude, in_longitude, in_start_date, in_step_size, in_step_count):
    """
    Calculate solar radiation over a period of time
    
    Args:
        in_latitude: float, latitude in degrees
        in_longitude: float, longitude in degrees
        in_start_date: Python datetime, starting date and time
        in_step_size: int, time step size in seconds
        in_step_count: int, number of time steps to calculate
        
    Returns:
        list of dicts with timestep and solar radiation values
    """
    curr_date = in_start_date
    num_intervals = min(96, (in_step_size // 60))
    last_day = 0
    
    # Get initial sunrise and sunset times
    json_sunrise_sunset = calculateSunriseAndSunset(in_start_date, in_latitude, in_longitude)
    sunrise = json_sunrise_sunset['sunrise']
    sunset = json_sunrise_sunset['sunset']
    
    # Create results table
    srad_results = []
    
    current_step = 1
    
    while current_step <= in_step_count:
        solar_sum = 0.0
        valid_count = 0.0
        current_interval = 1
        
        while current_interval <= num_intervals:
            # Calculate solar radiation for current interval
            json_sr = calculateSolarRadiation(curr_date, sunrise, sunset, in_latitude, in_longitude, valid_count)
            srad = json_sr['srad']
            valid_count = json_sr['count']
            
            solar_sum += srad
            
            # Move to next interval
            interval_seconds = in_step_size // num_intervals
            curr_date += datetime.timedelta(seconds=interval_seconds)
            
            # Check if day has changed
            current_day = curr_date.timetuple().tm_yday
            
            if current_day > last_day:
                # Recalculate sunrise and sunset for new day
                json_sunrise_sunset = calculateSolarNoon(curr_date, in_latitude, in_longitude)
                sunrise = json_sunrise_sunset['sunrise']
                sunset = json_sunrise_sunset['sunset']
                last_day = current_day
            
            current_interval += 1
        
        # Calculate average solar radiation for this step
        sr = 0.0
        
        if solar_sum > 0.0 and valid_count > 0:
            sr = solar_sum / valid_count
        
        # Add result
        srad_results.append({
            'timestep': curr_date,
            'srad': sr
        })
        
        current_step += 1
    
    return srad_results


if __name__ == '__main__':
    #check the various routines
    
    startDate=datetime.date(2023,1,1)
    endDate=datetime.date(2024,1,1)
    dateRange = [startDate + datetime.timedelta(days=delta) for delta in range((endDate - startDate).days + 1)]

    csvFile="sunriseSunset.csv"
    d = calculateSunriseAndSunset(date.today(), 62.0, -15.0)
    fields = list(d.keys())

    with open(csvFile, mode='w', newline='') as file:
        writer=DictWriter(file, fields)
        writer.writeheader()
        for res_date in dateRange:
            writer.writerow(calculateSunriseAndSunset(res_date, 60.0, 30.0))

# Example usage:
# latitude = 37.7749
# longitude = -122.4194
# start_date = datetime.datetime(2025, 3, 22, 8, 0, 0)  # March 22, 2025, 8:00 AM
# step_size = 3600  # 1 hour in seconds
# step_count = 24  # Calculate for 24 hours
# 
# results = calc_solar(latitude, longitude, start_date, step_size, step_count)
# for result in results:
#     print(f"Time: {result['timestep']}, Solar Radiation: {result['srad']:.2f}")