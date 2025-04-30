import json
import re
import os

def generate_json_files(identifiers_input, schema_precursor_file, output_schema_file="generated_schema.json", output_data_file="generated_data.json"):
    """
    Generate a valid JSON schema and data file based on identifiers and a schema precursor.
    
    Args:
        identifiers_input (str or dict): Path to the JSON file containing identifiers or a Python dictionary with identifiers
        schema_precursor_file (str): Path to the JSON schema precursor file
        output_schema_file (str): Path to save the generated schema
        output_data_file (str): Path to save the generated data
        
    Returns:
        tuple: Paths to the generated schema and data files
    """
    # Load the identifiers - either from file or use the provided dictionary
    if isinstance(identifiers_input, str):
        # Load from JSON file
        with open(identifiers_input, 'r') as f:
            identifiers = json.load(f)
    elif isinstance(identifiers_input, dict):
        # Use the provided dictionary directly
        identifiers = identifiers_input
    else:
        raise TypeError("identifiers_input must be a string (file path) or a dictionary")
    
    # Load the schema precursor
    with open(schema_precursor_file, 'r') as f:
        schema_precursor = json.load(f)
    
    # Calculate counts from identifiers
    counts = {
        "landcover_count": len(identifiers.get("landCover", {}).get("identifier", {}).get("name", [])),
        "bucket_count": len(identifiers.get("bucket", {}).get("identifier", {}).get("name", [])),
        "subcatchment_count": len(identifiers.get("subcatchment", {}).get("identifier", {}).get("name", [])),
        "reach_count": len(identifiers.get("reach", {}).get("identifier", {}).get("name", []))
    }
    
    print(f"Detected counts: {counts}")
    
    # Convert schema precursor to string to perform replacements
    schema_str = json.dumps(schema_precursor)
    
    # Replace count placeholders
    for count_key, count_value in counts.items():
        schema_str = schema_str.replace(f'"{count_key}"', str(count_value))
    
    # Convert back to object
    updated_schema = json.loads(schema_str)
    
    # Save the generated schema
    with open(output_schema_file, 'w') as f:
        json.dump(updated_schema, f, indent=2)
    
    # Now generate the actual data based on the schema and identifiers
    output_data = generate_data_from_schema(updated_schema, identifiers, counts)
    
    # Save the generated data
    with open(output_data_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    return output_schema_file, output_data_file

def generate_data_from_schema(schema, identifiers, counts):
    """
    Generate data based on the schema and identifiers.
    
    Args:
        schema (dict): The JSON schema
        identifiers (dict): The identifiers
        counts (dict): The counts of different elements
        
    Returns:
        dict: The generated data
    """
    data = {}
    
    # Generate general section
    data["general"] = {
        "name": schema["properties"]["general"]["properties"]["name"]["default"],
        "creator": schema["properties"]["general"]["properties"]["creator"]["default"],
        "timeStep": schema["properties"]["general"]["properties"]["timeStep"]["default"],
        "internalTimeStepMultiplier": schema["properties"]["general"]["properties"]["internalTimeStepMultiplier"]["default"],
        "startDate": schema["properties"]["general"]["properties"]["startDate"]["default"],
        "model": {
            "repository": schema["properties"]["general"]["properties"]["model"]["properties"]["repository"]["default"],
            "branch": schema["properties"]["general"]["properties"]["model"]["properties"]["branch"]["default"],
            "commit": schema["properties"]["general"]["properties"]["model"]["properties"]["commit"]["default"]
        },
        "chemistry": {}
    }
    
    # Generate bucket section
    data["bucket"] = {
        "identifier": {
            "name": identifiers["bucket"]["identifier"]["name"],
            "abbreviation": identifiers["bucket"]["identifier"]["abbreviation"]
        }
    }
    
    # Generate landCover section
    data["landCover"] = {
        "identifier": {
            "name": identifiers["landCover"]["identifier"]["name"],
            "abbreviation": identifiers["landCover"]["identifier"]["abbreviation"]
        },
        "general": generate_landcover_general(schema, counts),
        "precipitation": generate_landcover_precipitation(schema, counts),
        "routing": generate_landcover_routing(schema, counts),
        "soilOrSediment": {},
        "chemistry": {},
        "bucket": generate_landcover_buckets(schema, counts)
    }
    
    # Generate subcatchment section
    data["subcatchment"] = {
        "identifier": {
            "name": identifiers["subcatchment"]["identifier"]["name"]
        },
        "general": generate_subcatchment_general(schema, counts, identifiers),
        "hydrology": generate_subcatchment_hydrology(schema, counts),
        "soilOrSediment": {},
        "chemistry": {}
    }
    
    # Generate reach section
    data["reach"] = {
        "identifier": {
            "name": identifiers["reach"]["identifier"]["name"]
        },
        "general": generate_reach_general(schema, counts),
        "hydrology": generate_reach_hydrology(schema, counts),
        "soilOrSediment": {},
        "chemistry": {}
    }
    
    return data

def generate_landcover_general(schema, counts):
    """Generate the landcover general section"""
    landcover_general = {
        "soilTemperatureModel": {
            "C_s": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["soilTemperatureModel"]["properties"]["C_s"]["default"] 
                   for _ in range(counts["landcover_count"])],
            "K_t": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["soilTemperatureModel"]["properties"]["K_t"]["default"] 
                   for _ in range(counts["landcover_count"])],
            "C_ice": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["soilTemperatureModel"]["properties"]["C_ice"]["default"] 
                     for _ in range(counts["landcover_count"])],
            "f_s": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["soilTemperatureModel"]["properties"]["f_s"]["default"] 
                   for _ in range(counts["landcover_count"])]
        },
        "evapotranspirationModel": {
            "temperatureOffset": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["evapotranspirationModel"]["properties"]["temperatureOffset"]["default"] 
                                 for _ in range(counts["landcover_count"])],
            "scalingFactor": [schema["properties"]["landCover"]["properties"]["general"]["properties"]["evapotranspirationModel"]["properties"]["scalingFactor"]["default"] 
                             for _ in range(counts["landcover_count"])]
        }
    }
    return landcover_general

def generate_landcover_precipitation(schema, counts):
    """Generate the landcover precipitation section"""
    precipitation = {}
    for param in ["degreeDayMeltFactor", "rainfallMultiplier", "snowfallMultiplier", 
                  "snowfallTemperature", "snowmeltTemperature", "snowmeltRate", "snowDepth"]:
        precipitation[param] = [
            schema["properties"]["landCover"]["properties"]["precipitation"]["properties"][param]["default"] 
            for _ in range(counts["landcover_count"])
        ]
    return precipitation

def generate_landcover_routing(schema, counts):
    """Generate the landcover routing section"""
    # Create a 3D matrix for flow routing
    flow_matrix = []
    for _ in range(counts["landcover_count"]):
        land_matrix = []
        for _ in range(counts["bucket_count"]):
            bucket_matrix = [0.0] * counts["bucket_count"]  # Default all flows to 0
            land_matrix.append(bucket_matrix)
        flow_matrix.append(land_matrix)
    
    return {"flowMatrix": flow_matrix}

def generate_landcover_buckets(schema, counts):
    """Generate the landcover buckets section"""
    buckets = []
    
    for i in range(counts["bucket_count"]):
        bucket = {
            "general": {
                "surficial": schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["general"]["properties"]["surficial"]["default"],
                "initialSoilTemperature": schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["general"]["properties"]["initialSoilTemperature"]["default"],
                "relativeAreaIndex": [1.0] * counts["landcover_count"],
                "soilTemperatureEffectiveDepth": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["general"]["properties"]["soilTemperatureEffectiveDepth"]["default"]] * counts["landcover_count"]
            },
            "hydrology": {
                "characteristicTimeConstant": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["characteristicTimeConstant"]["default"]] * counts["landcover_count"],
                "tightlyBoundWaterDepth": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["tightlyBoundWaterDepth"]["default"]] * counts["landcover_count"],
                "looselyBoundWaterDepth": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["looselyBoundWaterDepth"]["default"]] * counts["landcover_count"],
                "freelyDrainingWaterDepth": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["freelyDrainingWaterDepth"]["default"]] * counts["landcover_count"],
                "initialWaterDepth": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["initialWaterDepth"]["default"]] * counts["landcover_count"],
                "relativeETIndex": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["relativeETIndex"]["default"]] * counts["landcover_count"],
                "ETScalingExponent": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["ETScalingExponent"]["default"]] * counts["landcover_count"],
                "infiltrationThresholdTempeerature": [schema["properties"]["landCover"]["properties"]["bucket"]["items"]["properties"]["hydrology"]["properties"]["infiltrationThresholdTempeerature"]["default"]] * counts["landcover_count"]
            },
            "soilOrSediment": {},
            "chemistry": {}
        }
        buckets.append(bucket)
    
    return buckets

def generate_subcatchment_general(schema, counts, identifiers):
    """Generate the subcatchment general section"""
    general = {
        "area": [schema["properties"]["subcatchment"]["properties"]["general"]["properties"]["area"]["default"]] * counts["subcatchment_count"],
        "latitudeAtOutflow": [schema["properties"]["subcatchment"]["properties"]["general"]["properties"]["latitudeAtOutflow"]["default"]] * counts["subcatchment_count"],
        "longitudeAtOutflow": [schema["properties"]["subcatchment"]["properties"]["general"]["properties"]["longitudeAtOutflow"]["default"]] * counts["subcatchment_count"],
        "landCoverPercent": []
    }
    
    # Generate land cover percentages for each subcatchment
    for _ in range(counts["subcatchment_count"]):
        # Equal distribution as default
        equal_percent = 100.0 / counts["landcover_count"] if counts["landcover_count"] > 0 else 0.0
        general["landCoverPercent"].append([equal_percent] * counts["landcover_count"])
    
    return general

def generate_subcatchment_hydrology(schema, counts):
    """Generate the subcatchment hydrology section"""
    hydrology = {}
    for param in ["rainfallMultiplier", "snowfallMultiplier", "snowfallTemperature", "snowmeltTemperature"]:
        hydrology[param] = [
            schema["properties"]["subcatchment"]["properties"]["hydrology"]["properties"][param]["default"] 
            for _ in range(counts["subcatchment_count"])
        ]
    return hydrology

def generate_reach_general(schema, counts):
    """Generate the reach general section"""
    general = {
        "length": [schema["properties"]["reach"]["properties"]["general"]["properties"]["length"]["default"]] * counts["reach_count"],
        "widthAtBottom": [schema["properties"]["reach"]["properties"]["general"]["properties"]["widthAtBottom"]["default"]] * counts["reach_count"],
        "slope": [schema["properties"]["reach"]["properties"]["general"]["properties"]["slope"]["default"]] * counts["reach_count"],
        "outflow": [None] * counts["reach_count"],  # Default all outflows to null
        "inflows": [[None]] * counts["reach_count"]  # Default all inflows to [null]
    }
    
    # Set up a simple sequential river network (if more than 1 reach)
    if counts["reach_count"] > 1:
        for i in range(counts["reach_count"] - 1):
            general["outflow"][i] = i + 1  # Current reach flows into the next reach
            general["inflows"][i + 1] = [i]  # Next reach has current reach as inflow
    
    return general

def generate_reach_hydrology(schema, counts):
    """Generate the reach hydrology section"""
    hydrology = {
        "hasAbstraction": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["hasAbstraction"]["default"]] * counts["reach_count"],
        "hasEffluent": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["hasEffluent"]["default"]] * counts["reach_count"],
        "Manning": {
            "a": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["Manning"]["properties"]["a"]["default"]] * counts["reach_count"],
            "b": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["Manning"]["properties"]["b"]["default"]] * counts["reach_count"],
            "c": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["Manning"]["properties"]["c"]["default"]] * counts["reach_count"],
            "f": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["Manning"]["properties"]["f"]["default"]] * counts["reach_count"],
            "n": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["Manning"]["properties"]["n"]["default"]] * counts["reach_count"]
        },
        "initialFlow": [schema["properties"]["reach"]["properties"]["hydrology"]["properties"]["initialFlow"]["default"]] * counts["reach_count"]
    }
    return hydrology

if __name__ == "__main__":
    # Example usage
    identifiers_file = "tmp_a.json"
    schema_precursor_file = "tmp_b.json"
    
    # Get output filenames from user
    output_schema = input("Enter output schema filename (default: generated_schema.json): ") or "generated_schema.json"
    output_data = input("Enter output data filename (default: generated_data.json): ") or "generated_data.json"
    
    schema_path, data_path = generate_json_files(
        identifiers_file,
        schema_precursor_file,
        output_schema,
        output_data
    )
    
    print(f"Schema generated and saved to: {schema_path}")
    print(f"Data generated and saved to: {data_path}")