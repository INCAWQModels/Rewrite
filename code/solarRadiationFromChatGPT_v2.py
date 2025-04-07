import math
import matplotlib.pyplot as plt

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

def solar_radiation(day_of_year, lat, hour, longitude=0, timezone_offset=0):
    decl = solar_declination(day_of_year)
    ha = solar_hour_angle(hour, longitude, timezone_offset)
    elev = solar_elevation_angle(lat, decl, ha)

    if elev <= 0:
        return 0

    I_0 = extraterrestrial_radiation(day_of_year)
    transmittance = 0.75
    radiation = I_0 * transmittance * math.sin(math.radians(elev))
    return radiation

def plot_solar_radiation(day_of_year, latitude, longitude, timezone_offset):
    hours = [i / 10.0 for i in range(0, 241)]  # 0.0 to 24.0 in 0.1 steps
    radiation = [solar_radiation(day_of_year, latitude, h, longitude, timezone_offset) for h in hours]

    plt.figure(figsize=(10, 5))
    plt.plot(hours, radiation, color="orange", linewidth=2)
    plt.fill_between(hours, radiation, color="orange", alpha=0.3)
    plt.title(f"Estimated Solar Radiation on Day {day_of_year}\nLat: {latitude}°, Lon: {longitude}°")
    plt.xlabel("Hour of Day")
    plt.ylabel("Solar Radiation (W/m²)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xticks(range(0, 25, 1))
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    day_of_year = 100           # e.g., April 9th
    latitude = 40.0             # degrees
    longitude = -105.0          # degrees
    timezone_offset = -6        # UTC offset

    plot_solar_radiation(day_of_year, latitude, longitude, timezone_offset)
