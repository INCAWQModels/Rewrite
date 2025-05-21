import json
from typing import Dict, Any, List, Optional
from persist_catchment_classes import Catchment, Bucket, LandCoverType, HRU, Subcatchment, Reach


def create_catchment_from_json(json_file_path: str) -> Catchment:
    """
    Create a Catchment object and its components from a JSON parameter file.
    
    Args:
        json_file_path: Path to the PERSiST parameter JSON file
        
    Returns:
        A fully populated Catchment instance
    """
    # Load the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Create the base catchment
    catchment = Catchment(
        id=data['general']['id'],
        name=data['general']['name'],
        creator=data['general']['creator']
    )
    
    # Create buckets
    create_buckets(catchment, data['bucket'])
    
    # Create land cover types
    create_land_cover_types(catchment, data['landCover'])
    
    # Create HRUs
    create_hrus(catchment, data['HRU'])
    
    # Set up connectivity between HRUs
    set_hru_connectivity(catchment, data['HRU'])
    
    return catchment


def create_buckets(catchment: Catchment, bucket_data: Dict[str, Any]) -> None:
    """Create bucket instances from JSON data and add them to the catchment."""
    bucket_names = bucket_data['identifier']['name']
    bucket_abbrevs = bucket_data['identifier']['abbreviation']
    
    # Create buckets with basic properties
    for i in range(len(bucket_names)):
        receives_precip = False
        if 'general' in bucket_data and 'receivesPrecipitation' in bucket_data['general']:
            # Handle boolean values stored as strings in JSON
            precip_value = bucket_data['general']['receivesPrecipitation'][i]
            if isinstance(precip_value, str):
                receives_precip = precip_value.lower() == 'true'
            else:
                receives_precip = bool(precip_value)
        
        bucket = Bucket(
            name=bucket_names[i],
            abbreviation=bucket_abbrevs[i],
            receives_precipitation=receives_precip
        )
        catchment.add_bucket(bucket)


def create_land_cover_types(catchment: Catchment, land_cover_data: Dict[str, Any]) -> None:
    """Create land cover type instances from JSON data and add them to the catchment."""
    lc_names = land_cover_data['identifier']['name']
    lc_abbrevs = land_cover_data['identifier']['abbreviation']
    
    for i in range(len(lc_names)):
        lc = LandCoverType(
            name=lc_names[i],
            abbreviation=lc_abbrevs[i]
        )
        
        # Set soil temperature model parameters
        stm = land_cover_data['general']['soilTemperatureModel']
        lc.c_s = stm['C_s'][i]
        lc.k_t = stm['K_t'][i]
        lc.c_ice = stm['C_ice'][i]
        lc.f_s = stm['f_s'][i]
        
        # Set evapotranspiration model parameters
        etm = land_cover_data['general']['evapotranspirationModel']
        lc.temperature_offset = etm['temperatureOffset'][i]
        lc.scaling_factor = etm['scalingFactor'][i]
        
        # Set precipitation parameters
        precip = land_cover_data['precipitation']
        lc.degree_day_melt_factor = precip['degreeDayMeltFactor'][i]
        lc.rainfall_multiplier = precip['rainfallMultiplier'][i]
        lc.snowfall_multiplier = precip['snowfallMultiplier'][i]
        lc.snowfall_temperature = precip['snowfallTemperature'][i]
        lc.snowmelt_temperature = precip['snowmeltTemperature'][i]
        lc.snowmelt_rate = precip['snowmeltRate'][i]
        lc.snow_depth = precip['snowDepth'][i]
        
        # Set flow matrix
        lc.flow_matrix = land_cover_data['routing']['flowMatrix'][i]
        
        # Process bucket-specific parameters for this land cover
        for bucket_idx, bucket_data in enumerate(land_cover_data['bucket']):
            bucket_props = {}
            
            # General bucket properties
            if 'general' in bucket_data:
                general = bucket_data['general']
                if 'initialSoilTemperature' in general:
                    bucket_props['initial_soil_temperature'] = general['initialSoilTemperature']
                if 'relativeAreaIndex' in general:
                    bucket_props['relative_area_index'] = general['relativeAreaIndex'][i]
                if 'soilTemperatureEffectiveDepth' in general:
                    bucket_props['soil_temperature_effective_depth'] = general['soilTemperatureEffectiveDepth'][i]
            
            # Hydrology bucket properties
            if 'hydrology' in bucket_data:
                hydro = bucket_data['hydrology']
                if 'characteristicTimeConstant' in hydro:
                    bucket_props['characteristic_time_constant'] = hydro['characteristicTimeConstant'][i]
                if 'tightlyBoundWaterDepth' in hydro:
                    bucket_props['tightly_bound_water_depth'] = hydro['tightlyBoundWaterDepth'][i]
                if 'looselyBoundWaterDepth' in hydro:
                    bucket_props['loosely_bound_water_depth'] = hydro['looselyBoundWaterDepth'][i]
                if 'freelyDrainingWaterDepth' in hydro:
                    bucket_props['freely_draining_water_depth'] = hydro['freelyDrainingWaterDepth'][i]
                if 'initialWaterDepth' in hydro:
                    bucket_props['initial_water_depth'] = hydro['initialWaterDepth'][i]
                if 'relativeETIndex' in hydro:
                    bucket_props['relative_et_index'] = hydro['relativeETIndex'][i]
                if 'ETScalingExponent' in hydro:
                    bucket_props['et_scaling_exponent'] = hydro['ETScalingExponent'][i]
                if 'infiltrationThresholdTemperature' in hydro:
                    bucket_props['infiltration_threshold_temperature'] = hydro['infiltrationThresholdTemperature'][i]
            
            # Chemistry bucket properties
            if 'chemistry' in bucket_data and 'general' in bucket_data['chemistry']:
                chem = bucket_data['chemistry']['general']
                if 'soilTemperatureOffset' in chem:
                    bucket_props['soil_temperature_offset'] = chem['soilTemperatureOffset'][i]
                if 'soilTemperatureExponent' in chem:
                    bucket_props['soil_temperature_exponent'] = chem['soilTemperatureExponent'][i]
            
            # Store the bucket properties for this land cover
            if bucket_idx < len(catchment.buckets):
                lc.bucket_properties[catchment.buckets[bucket_idx]] = bucket_props
        
        catchment.add_land_cover_type(lc)


def create_hrus(catchment: Catchment, hru_data: Dict[str, Any]) -> None:
    """Create HRU instances from JSON data and add them to the catchment."""
    hru_names = hru_data['identifier']['name']
    
    # Get abbreviations if available, otherwise use None
    hru_abbrevs = None
    if 'abbreviation' in hru_data['identifier']:
        hru_abbrevs = hru_data['identifier']['abbreviation']
    
    for i in range(len(hru_names)):
        abbrev = hru_abbrevs[i] if hru_abbrevs else None
        hru = HRU(
            name=hru_names[i],
            abbreviation=abbrev
        )
        
        # Set subcatchment properties
        subcat = hru.subcatchment
        subcat_gen = hru_data['subcatchment']['general']
        subcat.area = subcat_gen['area'][i]
        subcat.latitude_at_outflow = subcat_gen['latitudeAtOutflow'][i]
        subcat.longitude_at_outflow = subcat_gen['longitudeAtOutflow'][i]
        
        # Set land cover percentages
        lc_percents = subcat_gen['landCoverPercent'][i]
        for lc_idx, percent in enumerate(lc_percents):
            if lc_idx < len(catchment.land_cover_types):
                subcat.land_cover_percent[catchment.land_cover_types[lc_idx]] = percent
        
        # Set subcatchment hydrology properties
        subcat_hydro = hru_data['subcatchment']['hydrology']
        subcat.rainfall_multiplier = subcat_hydro['rainfallMultiplier'][i]
        subcat.snowfall_multiplier = subcat_hydro['snowfallMultiplier'][i]
        subcat.snowfall_temperature = subcat_hydro['snowfallTemperature'][i]
        subcat.snowmelt_temperature = subcat_hydro['snowmeltTemperature'][i]
        
        # Set reach properties
        reach = hru.reach
        reach_gen = hru_data['reach']['general']
        reach.length = reach_gen['length'][i]
        reach.width_at_bottom = reach_gen['widthAtBottom'][i]
        reach.slope = reach_gen['slope'][i]
        
        # HRU connectivity will be set in a separate step after all HRUs are created
        
        # Set reach hydrology properties
        reach_hydro = hru_data['reach']['hydrology']
        reach.has_abstraction = reach_hydro['hasAbstraction'][i]
        reach.has_effluent = reach_hydro['hasEffluent'][i]
        
        manning = reach_hydro['Manning']
        reach.manning_a = manning['a'][i]
        reach.manning_b = manning['b'][i]
        reach.manning_c = manning['c'][i]
        reach.manning_f = manning['f'][i]
        reach.manning_n = manning['n'][i]
        
        reach.initial_flow = reach_hydro['initialFlow'][i]
        
        catchment.add_hru(hru)


def set_hru_connectivity(catchment: Catchment, hru_data: Dict[str, Any]) -> None:
    """Set up the connectivity between HRUs based on outflow and inflow data."""
    reach_gen = hru_data['reach']['general']
    
    # Process outflows
    for i, outflow in enumerate(reach_gen['outflow']):
        if i < len(catchment.hrus) and outflow is not None:
            catchment.hrus[i].reach.outflow_to = outflow
    
    # Process inflows
    for i, inflows in enumerate(reach_gen['inflows']):
        if i < len(catchment.hrus):
            catchment.hrus[i].reach.inflows_from = [
                inflow for inflow in inflows if inflow is not None
            ]


def export_catchment_to_json(catchment: Catchment, json_file_path: str) -> None:
    """
    Export a catchment to a JSON parameter file.
    
    Args:
        catchment: The catchment instance to export
        json_file_path: Output file path
    """
    # This would be the implementation of exporting back to JSON
    # (Left as a future extension)
    pass


# Example usage
if __name__ == "__main__":
    # Import a catchment from a JSON file
    catchment = create_catchment_from_json("PERSiSTParameter.json")
    
    # Print catchment structure
    print(f"Catchment: {catchment.name}")
    print(f"Number of HRUs: {len(catchment.hrus)}")
    print(f"Number of Land Cover Types: {len(catchment.land_cover_types)}")
    print(f"Number of Buckets: {len(catchment.buckets)}")
    
    print("\nHRU Connections:")
    for hru in catchment.hrus:
        outflow = f"HRU {hru.reach.outflow_to}" if hru.reach.outflow_to is not None else "Outlet"
        print(f"  {hru.name} → {outflow}")
    
    print("\nLand Cover Types:")
    for lc in catchment.land_cover_types:
        print(f"  {lc.name} ({lc.abbreviation})")
        print(f"    Rainfall multiplier: {lc.rainfall_multiplier}")
        
    print("\nBuckets:")
    for bucket in catchment.buckets:
        print(f"  {bucket.name} ({bucket.abbreviation})")
        print(f"    Receives precipitation: {bucket.receives_precipitation}")
