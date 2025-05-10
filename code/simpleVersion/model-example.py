import datetime
import json
from typing import List, Dict, Any, Optional, Union

# Import our custom classes
from time_series import TimeSeries
# Assume hydrological classes are imported here
# from hydrological_classes import Catchment, HRU, Subcatchment, Reach, LandCover, Bucket, BucketList, LandCoverList
# from schema_converter import json_to_model, model_to_json
from model import Model

def create_example_model() -> Model:
    """
    Create an example hydrological model with a catchment and time series.
    
    Returns:
        Model object with example data
    """
    # For this example, we'll load a catchment from a JSON file
    with open('example_model.json', 'r') as f:
        catchment_json = json.load(f)
    
    # Convert JSON to catchment object
    from schema_converter import json_to_model
    catchment = json_to_model(catchment_json)
    
    # Create a model with the catchment and specify time steps
    model = Model(
        name="River Valley Rainfall-Runoff Model",
        description="Rainfall-runoff model for the River Valley catchment with meteorological data",
        catchment=catchment,
        external_time_step=86400.0,  # Daily time step (86400 seconds)
        internal_time_step=3600.0    # Hourly computational time step (3600 seconds)
    )
    
    # Create meteorological time series
    # For this example, we'll create 2 met_ts to cover all HRUs
    
    # First met_ts - for upper half of the catchment
    upper_met_ts = TimeSeries(name="Upper Meteorological Data")
    
    # Add metadata
    upper_met_ts.add_metadata("data_type", "meteorological")
    upper_met_ts.add_metadata("time_step", "daily")
    upper_met_ts.add_metadata("source", "Weather Station Data")
    
    # Define column names
    upper_met_ts.columns = [upper_met_ts.uuid, "location", "precipitation", "temperature"]
    
    # Second met_ts - for lower half of the catchment
    lower_met_ts = TimeSeries(name="Lower Meteorological Data")
    
    # Add metadata
    lower_met_ts.add_metadata("data_type", "meteorological")
    lower_met_ts.add_metadata("time_step", "daily")
    lower_met_ts.add_metadata("source", "Weather Station Data")
    
    # Define column names
    lower_met_ts.columns = [lower_met_ts.uuid, "location", "precipitation", "temperature"]
    
    # Base date for our time series
    base_date = datetime.datetime(2023, 1, 1)
    
    # Generate sample data for both meteorological time series
    # The "location" will be a generic identifier since met_ts are associated with HRUs by mapping
    for day in range(30):
        # Create a timestamp for this day
        timestamp = base_date + datetime.timedelta(days=day)
        
        # Generate values for upper catchment
        upper_precip = 5.0 + (day % 7) * 2.0  # Higher precipitation
        upper_temp = 15.0 + (day % 10) - (day % 3)  # Temperature with some variation
        
        # Generate values for lower catchment
        lower_precip = 3.0 + (day % 7) * 1.0  # Lower precipitation
        lower_temp = 18.0 + (day % 10) - (day % 3)  # Higher temperature with variation
        
        # Add the data points
        upper_met_ts.add_data(timestamp, "upper_catchment", {
            "precipitation": upper_precip,
            "temperature": upper_temp
        })
        
        lower_met_ts.add_data(timestamp, "lower_catchment", {
            "precipitation": lower_precip,
            "temperature": lower_temp
        })
    
    # Add meteorological time series to the model
    model.add_time_series(upper_met_ts)
    model.add_time_series(lower_met_ts)
    
    # Associate met_ts with HRUs
    # First, get all HRU IDs from the catchment
    all_hrus = catchment.get_all_hrus()
    hru_ids = list(all_hrus.keys())
    
    # Divide HRUs into upper and lower groups
    # For simplicity, we'll just split them in half
    upper_hrus = hru_ids[:len(hru_ids)//2]
    lower_hrus = hru_ids[len(hru_ids)//2:]
    
    # Associate each group with the corresponding met_ts
    model.add_met_timeseries(upper_met_ts, upper_hrus)
    model.add_met_timeseries(lower_met_ts, lower_hrus)
    
    # Validate the met_ts coverage
    is_valid, uncovered, multiple = model.validate_met_timeseries_coverage()
    if not is_valid:
        print(f"Warning: Invalid met_ts coverage. Uncovered HRUs: {uncovered}, Multiple coverage: {multiple}")
    
    return model

def use_example_model(model: Model) -> None:
    """
    Demonstrate the use of a hydrological model.
    
    Args:
        model: Hydrological model to use
    """
    print(f"Model: {model.name}")
    print(f"Description: {model.description}")
    print(f"Catchment: {model.catchment.name} with {len(model.catchment.hrus)} HRUs")
    print(f"Time Series: {len(model.time_series)} series")
    print(f"Time Steps: External={model.external_time_step/86400:.1f} days, Internal={model.internal_time_step/3600:.1f} hours")
    
    # Print time range
    start_time, end_time = model.get_time_range()
    if start_time and end_time:
        print(f"Time Range: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
    
    # Check meteorological time series coverage
    is_valid, uncovered, multiple = model.validate_met_timeseries_coverage()
    print(f"\nMet TS Coverage Valid: {is_valid}")
    if not is_valid:
        if uncovered:
            print(f"  Uncovered HRUs: {uncovered}")
        if multiple:
            print(f"  HRUs with multiple coverage: {multiple}")
    
    # Get all HRUs
    hrus = model.catchment.get_all_hrus()
    if hrus:
        print(f"\nHRU Count: {len(hrus)}")
        
        # Get the first HRU
        first_hru_id = next(iter(hrus.keys()))
        first_hru = hrus[first_hru_id]
        
        print(f"\nData for HRU '{first_hru.name}' (ID: {first_hru_id}):")
        
        # Get the meteorological time series for this HRU
        met_ts = model.get_met_timeseries_for_hru(first_hru_id)
        if met_ts:
            print(f"  Associated Met TS: {met_ts.name} (ID: {met_ts.uuid})")
            
            # Get some sample data from the met_ts
            # Since the actual location in the met_ts might not match the HRU ID,
            # we need to get data from the met_ts by its known location
            location = "upper_catchment" if first_hru_id in model.get_hrus_for_met_timeseries(met_ts.uuid) else "lower_catchment"
            data = met_ts.get_data_by_location(location)
            if data:
                print(f"  Met TS Data Points: {len(data)}")
                print(f"  First Data Point: {data[0]}")
                
                # Show the precipitation and temperature values
                timestamp, loc, *values = data[0]
                if 'precipitation' in met_ts.columns and 'temperature' in met_ts.columns:
                    precip_idx = met_ts.columns.index('precipitation')
                    temp_idx = met_ts.columns.index('temperature')
                    if len(data[0]) > max(precip_idx, temp_idx):
                        print(f"  First Day Precipitation: {data[0][precip_idx]} mm")
                        print(f"  First Day Temperature: {data[0][temp_idx]} °C")
    
    # Get all subcatchments
    subcatchments = model.catchment.get_all_subcatchments()
    if subcatchments:
        # Get the first subcatchment
        first_sc_id = next(iter(subcatchments.keys()))
        first_sc = subcatchments[first_sc_id]
        
        print(f"\nData for subcatchment '{first_sc.name}':")
        
        # Get all HRUs in this subcatchment
        subcatchment_hrus = [hru for hru in model.catchment.hrus if hru.subcatchment.id == first_sc_id]
        print(f"  HRUs in this subcatchment: {len(subcatchment_hrus)}")
        
        # Show which met_ts is associated with each HRU in this subcatchment
        for hru in subcatchment_hrus:
            met_ts = model.get_met_timeseries_for_hru(hru.id)
            if met_ts:
                print(f"  HRU {hru.name} is associated with met_ts: {met_ts.name}")
    
    # Test changing time steps
    print("\nChanging time steps...")
    model.set_time_steps(43200.0, 1800.0)  # 12 hours external, 30 minutes internal
    print(f"New Time Steps: External={model.external_time_step/3600:.1f} hours, Internal={model.internal_time_step/60:.1f} minutes")
    
    # Save the model to files
    print("\nSaving model to files...")
    model_file, ts_files = model.save_to_files("example_output")
    print(f"Model saved to: {model_file}")
    print(f"Time series saved to: {len(ts_files)} files")
    
    # Demonstrate how to load the model back
    print("\nLoading model from files...")
    loaded_model = Model.load_from_files(model_file)
    print(f"Loaded model: {loaded_model.name} with {len(loaded_model.time_series)} time series")
    print(f"Loaded Time Steps: External={loaded_model.external_time_step/3600:.1f} hours, Internal={loaded_model.internal_time_step/60:.1f} minutes")
    print(f"Met TS mappings: {len(loaded_model.met_ts_mappings)} mappings")

if __name__ == "__main__":
    # Create an example model
    model = create_example_model()
    
    # Use the model
    use_example_model(model)
