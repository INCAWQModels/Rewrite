import json
from typing import Dict, List, Any, Optional, Set, Tuple


def json_to_model(json_dict: Dict[str, Any]) -> 'Catchment':
    """
    Convert a JSON dictionary to a Catchment model object.
    
    Args:
        json_dict: Dictionary following the hydrological model JSON schema
        
    Returns:
        A Catchment object populated with the data from the JSON
    """
    # First, build lookup dictionaries for references
    reach_lookup = {}
    subcatchment_lookup = {}
    
    # Process reaches first (we'll resolve outflow references later)
    reaches_data = json_dict.get('reaches', [])
    for reach_data in reaches_data:
        reach = Reach(
            name=reach_data['name'],
            abbreviation=reach_data['abbreviation'],
            length=reach_data['length'],
            width_at_bottom=reach_data['width_at_bottom'],
            latitude_of_outflow=reach_data['latitude_of_outflow'],
            longitude_of_outflow=reach_data['longitude_of_outflow'],
            id=reach_data['id']
        )
        reach_lookup[reach.id] = reach
    
    # Connect reaches by updating outflow references
    for reach_data in reaches_data:
        outflow_id = reach_data.get('outflow_reach_id')
        if outflow_id:
            reach_lookup[reach_data['id']].outflow_reach = reach_lookup.get(outflow_id)
    
    # Process subcatchments
    subcatchments_data = json_dict.get('subcatchments', [])
    for subcatchment_data in subcatchments_data:
        # Process land covers for this subcatchment
        land_covers = []
        for land_cover_data in subcatchment_data.get('land_cover_list', []):
            # Process buckets for this land cover
            bucket_list = BucketList()
            for bucket_data in land_cover_data.get('bucket_list', []):
                bucket = Bucket(
                    name=bucket_data['name'],
                    abbreviation=bucket_data['abbreviation'],
                    depth_of_water=bucket_data['depth_of_water'],
                    characteristic_time_constant=bucket_data['characteristic_time_constant'],
                    relative_area=bucket_data['relative_area'],
                    id=bucket_data['id']
                )
                bucket_list.append(bucket)
            
            # Create land cover with its buckets
            land_cover = LandCover(
                name=land_cover_data['name'],
                abbreviation=land_cover_data['abbreviation'],
                bucket_list=bucket_list,
                relative_area=land_cover_data['relative_area'],
                rainfall_multiplier=land_cover_data['rainfall_multiplier'],
                snowfall_multiplier=land_cover_data['snowfall_multiplier'],
                snowfall_temperature=land_cover_data['snowfall_temperature'],
                snowmelt_temperature=land_cover_data['snowmelt_temperature'],
                degree_day_melt_factor=land_cover_data['degree_day_melt_factor'],
                id=land_cover_data['id']
            )
            land_covers.append(land_cover)
        
        # Create subcatchment with its land covers
        subcatchment = Subcatchment(
            name=subcatchment_data['name'],
            abbreviation=subcatchment_data['abbreviation'],
            land_cover_list=LandCoverList(land_covers),
            area=subcatchment_data['area'],
            rainfall_multiplier=subcatchment_data['rainfall_multiplier'],
            snowfall_multiplier=subcatchment_data['snowfall_multiplier'],
            snowfall_temperature=subcatchment_data['snowfall_temperature'],
            snowmelt_temperature=subcatchment_data['snowmelt_temperature'],
            id=subcatchment_data['id']
        )
        subcatchment_lookup[subcatchment.id] = subcatchment
    
    # Process HRUs
    hrus = []
    for hru_data in json_dict.get('hrus', []):
        subcatchment = subcatchment_lookup.get(hru_data['subcatchment_id'])
        reach = reach_lookup.get(hru_data['reach_id'])
        if subcatchment and reach:
            hru = HRU(
                subcatchment=subcatchment,
                reach=reach,
                id=hru_data['id']
            )
            hrus.append(hru)
    
    # Create catchment
    catchment = Catchment(
        name=json_dict['name'],
        abbreviation=json_dict['abbreviation'],
        description=json_dict['description'],
        hrus=hrus,
        id=json_dict['id']
    )
    
    return catchment


def model_to_json(catchment: 'Catchment') -> Dict[str, Any]:
    """
    Convert a Catchment model object to a JSON dictionary.
    
    Args:
        catchment: Catchment object to convert
        
    Returns:
        Dictionary following the hydrological model JSON schema
    """
    # Track objects we've already processed to avoid duplicates
    processed_ids: Set[str] = set()
    
    # Create the base dictionary
    json_dict = {
        'id': catchment.id,
        'name': catchment.name,
        'abbreviation': catchment.abbreviation,
        'description': catchment.description,
        'hrus': [],
        'subcatchments': [],
        'reaches': []
    }
    
    # Process reaches
    for hru in catchment.hrus:
        reach = hru.reach
        if reach.id not in processed_ids:
            reach_dict = {
                'id': reach.id,
                'name': reach.name,
                'abbreviation': reach.abbreviation,
                'length': reach.length,
                'width_at_bottom': reach.width_at_bottom,
                'latitude_of_outflow': reach.latitude_of_outflow,
                'longitude_of_outflow': reach.longitude_of_outflow,
                'outflow_reach_id': reach.outflow_reach.id if reach.outflow_reach else None
            }
            json_dict['reaches'].append(reach_dict)
            processed_ids.add(reach.id)
    
    # Process subcatchments and their nested components
    processed_ids.clear()  # Reset to track subcatchments separately
    for hru in catchment.hrus:
        subcatchment = hru.subcatchment
        if subcatchment.id not in processed_ids:
            # Convert land covers
            land_cover_list = []
            for land_cover in subcatchment.land_cover_list:
                # Convert buckets
                bucket_list = []
                for bucket in land_cover.bucket_list:
                    bucket_dict = {
                        'id': bucket.id,
                        'name': bucket.name,
                        'abbreviation': bucket.abbreviation,
                        'depth_of_water': bucket.depth_of_water,
                        'characteristic_time_constant': bucket.characteristic_time_constant,
                        'relative_area': bucket.relative_area
                    }
                    bucket_list.append(bucket_dict)
                
                # Add the land cover
                land_cover_dict = {
                    'id': land_cover.id,
                    'name': land_cover.name,
                    'abbreviation': land_cover.abbreviation,
                    'relative_area': land_cover.relative_area,
                    'rainfall_multiplier': land_cover.rainfall_multiplier,
                    'snowfall_multiplier': land_cover.snowfall_multiplier,
                    'snowfall_temperature': land_cover.snowfall_temperature,
                    'snowmelt_temperature': land_cover.snowmelt_temperature,
                    'degree_day_melt_factor': land_cover.degree_day_melt_factor,
                    'bucket_list': bucket_list
                }
                land_cover_list.append(land_cover_dict)
            
            # Add the subcatchment
            subcatchment_dict = {
                'id': subcatchment.id,
                'name': subcatchment.name,
                'abbreviation': subcatchment.abbreviation,
                'area': subcatchment.area,
                'rainfall_multiplier': subcatchment.rainfall_multiplier,
                'snowfall_multiplier': subcatchment.snowfall_multiplier,
                'snowfall_temperature': subcatchment.snowfall_temperature,
                'snowmelt_temperature': subcatchment.snowmelt_temperature,
                'land_cover_list': land_cover_list
            }
            json_dict['subcatchments'].append(subcatchment_dict)
            processed_ids.add(subcatchment.id)
    
    # Process HRUs
    for hru in catchment.hrus:
        hru_dict = {
            'id': hru.id,
            'name': hru.name,
            'abbreviation': hru.abbreviation,
            'subcatchment_id': hru.subcatchment.id,
            'reach_id': hru.reach.id
        }
        json_dict['hrus'].append(hru_dict)
    
    return json_dict


def load_from_json(file_path: str) -> 'Catchment':
    """
    Load a catchment model from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        A Catchment object populated with the data from the JSON file
    """
    with open(file_path, 'r') as f:
        json_dict = json.load(f)
    
    return json_to_model(json_dict)


def save_to_json(catchment: 'Catchment', file_path: str, indent: int = 2) -> None:
    """
    Save a catchment model to a JSON file.
    
    Args:
        catchment: Catchment object to save
        file_path: Path to save the JSON file
        indent: Indentation level for pretty printing (default: 2)
    """
    json_dict = model_to_json(catchment)
    
    with open(file_path, 'w') as f:
        json.dump(json_dict, f, indent=indent)


# Example usage:
if __name__ == "__main__":
    # Load schema from file
    try:
        with open('example_model.json', 'r') as f:
            json_data = json.load(f)
        
        # Convert to model
        model = json_to_model(json_data)
        print(f"Loaded catchment: {model.name} with {len(model.hrus)} HRUs")
        
        # Convert back to JSON
        json_output = model_to_json(model)
        
        # Save to a new file
        with open('output_model.json', 'w') as f:
            json.dump(json_output, f, indent=2)
        
        print(f"Saved catchment to output_model.json")
        
    except FileNotFoundError:
        print("Example file not found. To use this script:")
        print("1. Create an example_model.json file following the schema")
        print("2. Run this script to convert between JSON and model objects")
