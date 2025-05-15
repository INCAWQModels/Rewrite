import json
import os

def create_persist_parameter_file():
    """Create a PERSiSTParameter.json file from schema and headings"""
    # 1. Read the headings.json file to get the counts
    with open('headings.json', 'r') as f:
        headings = json.load(f)
    
    # Count the items in each category
    bucket_count = len(headings['bucket']['identifier']['name'])
    landcover_count = len(headings['landCover']['identifier']['name'])
    hru_count = len(headings['HRU']['identifier']['name'])
    
    print(f"Found {bucket_count} buckets, {landcover_count} land covers, and {hru_count} HRUs")
    
    # 2. Read the PERSiSTCatchmentPrecursor.json file
    with open('PERSiSTCatchmentPrecursor.json', 'r') as f:
        schema_text = f.read()
    
    # 3. Replace the placeholders with the actual counts
    schema_text = schema_text.replace('BUCKET_COUNT', str(bucket_count))
    schema_text = schema_text.replace('LANDCOVER_COUNT', str(landcover_count))
    schema_text = schema_text.replace('HRU_COUNT', str(hru_count))
    
    # Save the valid schema
    with open('PERSiSTCatchmentSchema.json', 'w') as f:
        f.write(schema_text)
    
    # 4. Parse the modified text as JSON
    try:
        schema = json.loads(schema_text)
        print("Successfully parsed schema")
    except json.JSONDecodeError as e:
        print(f"Error parsing schema: {e}")
        return
    
    # 5. Create a parameter file based on the schema and headings
    parameters = build_parameters(schema, headings)
    
    # 6. Save the parameters file
    with open('PERSiSTParameter.json', 'w') as f:
        json.dump(parameters, f, indent=2)
    
    print("Successfully created PERSiSTParameter.json")

def build_parameters(schema, headings):
    """Build a complete parameter set based on the schema and headings"""
    bucket_count = len(headings['bucket']['identifier']['name'])
    landcover_count = len(headings['landCover']['identifier']['name'])
    hru_count = len(headings['HRU']['identifier']['name'])
    
    # Create parameter structure
    parameters = {}
    
    # === GENERAL SECTION ===
    parameters["general"] = {
        "id": "XXX",
        "name": "New parameter set",
        "creator": "Anonymous"
    }
    
    # === BUCKET SECTION ===
    parameters["bucket"] = {
        "identifier": {
            "name": headings["bucket"]["identifier"]["name"],
            "abbreviation": headings["bucket"]["identifier"]["abbreviation"]
        },
        "general": {
            "receivesPrecipitation": ["false" for _ in range(bucket_count)]
        }
    }
    
    # === LANDCOVER SECTION ===
    parameters["landCover"] = {
        "identifier": {
            "name": headings["landCover"]["identifier"]["name"],
            "abbreviation": headings["landCover"]["identifier"]["abbreviation"]
        },
        "general": {
            "soilTemperatureModel": {
                "C_s": [10000000.0 for _ in range(landcover_count)],
                "K_t": [0.6 for _ in range(landcover_count)],
                "C_ice": [9000000.0 for _ in range(landcover_count)],
                "f_s": [-3.0 for _ in range(landcover_count)]
            },
            "evapotranspirationModel": {
                "temperatureOffset": [0.0 for _ in range(landcover_count)],
                "scalingFactor": [70.0 for _ in range(landcover_count)]
            }
        },
        "precipitation": {
            "degreeDayMeltFactor": [3.0 for _ in range(landcover_count)],
            "rainfallMultiplier": [1.0 for _ in range(landcover_count)],
            "snowfallMultiplier": [1.0 for _ in range(landcover_count)],
            "snowfallTemperature": [0.0 for _ in range(landcover_count)],
            "snowmeltTemperature": [0.0 for _ in range(landcover_count)],
            "snowmeltRate": [3.0 for _ in range(landcover_count)],
            "snowDepth": [0.0 for _ in range(landcover_count)]
        },
        "routing": {
            "flowMatrix": []
        },
        "bucket": []
    }
    
    # Build flow matrix
    flow_matrix = []
    for _ in range(landcover_count):
        landcover_matrix = []
        for _ in range(bucket_count):
            bucket_row = [0.0 for _ in range(bucket_count)]
            landcover_matrix.append(bucket_row)
        flow_matrix.append(landcover_matrix)
    parameters["landCover"]["routing"]["flowMatrix"] = flow_matrix
    
    # Build bucket settings
    for _ in range(bucket_count):
        bucket_settings = {
            "general": {
                "initialSoilTemperature": 5.0,
                "relativeAreaIndex": [1.0 for _ in range(landcover_count)],
                "soilTemperatureEffectiveDepth": [30.0 for _ in range(landcover_count)]
            },
            "hydrology": {
                "characteristicTimeConstant": [1.0 for _ in range(landcover_count)],
                "tightlyBoundWaterDepth": [10.0 for _ in range(landcover_count)],
                "looselyBoundWaterDepth": [50.0 for _ in range(landcover_count)],
                "freelyDrainingWaterDepth": [50.0 for _ in range(landcover_count)],
                "initialWaterDepth": [100.0 for _ in range(landcover_count)],
                "relativeETIndex": [0.0 for _ in range(landcover_count)],
                "ETScalingExponent": [1.0 for _ in range(landcover_count)],
                "infiltrationThresholdTemperature": [0.0 for _ in range(landcover_count)]
            },
            "chemistry": {
                "general": {
                    "soilTemperatureOffset": [20.0 for _ in range(landcover_count)],
                    "soilTemperatureExponent": [2.0 for _ in range(landcover_count)]
                }
            }
        }
        parameters["landCover"]["bucket"].append(bucket_settings)
    
    # === HRU SECTION ===
    parameters["HRU"] = {
        "identifier": {
            "name": headings["HRU"]["identifier"]["name"]
        },
        "subcatchment": {
            "general": {
                "area": [10.0 for _ in range(hru_count)],
                "latitudeAtOutflow": [0.0 for _ in range(hru_count)],
                "longitudeAtOutflow": [0.0 for _ in range(hru_count)],
                "landCoverPercent": []
            },
            "hydrology": {
                "rainfallMultiplier": [1.0 for _ in range(hru_count)],
                "snowfallMultiplier": [1.0 for _ in range(hru_count)],
                "snowfallTemperature": [0.0 for _ in range(hru_count)],
                "snowmeltTemperature": [0.0 for _ in range(hru_count)]
            }
        },
        "reach": {
            "general": {
                "length": [10000.0 for _ in range(hru_count)],
                "widthAtBottom": [10.0 for _ in range(hru_count)],
                "slope": [0.0001 for _ in range(hru_count)],
                "outflow": [None for _ in range(hru_count)],
                "inflows": []
            },
            "hydrology": {
                "hasAbstraction": [False for _ in range(hru_count)],
                "hasEffluent": [False for _ in range(hru_count)],
                "Manning": {
                    "a": [2.71 for _ in range(hru_count)],
                    "b": [0.557 for _ in range(hru_count)],
                    "c": [0.349 for _ in range(hru_count)],
                    "f": [0.341 for _ in range(hru_count)],
                    "n": [0.1 for _ in range(hru_count)]
                },
                "initialFlow": [1.0 for _ in range(hru_count)]
            }
        }
    }
    
    # Build landCoverPercent (array of arrays)
    landcover_percent = []
    for _ in range(hru_count):
        landcover_percent.append([20.0 for _ in range(landcover_count)])
    parameters["HRU"]["subcatchment"]["general"]["landCoverPercent"] = landcover_percent
    
    # Build inflows (array of arrays)
    inflows = []
    for _ in range(hru_count):
        inflows.append([None])  # Each HRU starts with one null inflow
    parameters["HRU"]["reach"]["general"]["inflows"] = inflows
    
    return parameters

if __name__ == '__main__':
    create_persist_parameter_file()
