import json
import os
import re
import sys
from typing import Union, Dict, Tuple

def generate_parameter_set_json(catchment_structure: Union[Dict, str], schema_precursor_file: str, 
                              output_schema_file=None, output_parameter_file=None) -> Tuple[Dict, Dict]:
    """
    Generate a JSON schema and parameter set for INCA water quality model based on catchment structure.
    
    This function takes a catchment structure (either as a dictionary or a path to a JSON file)
    and a schema precursor file, then generates a complete JSON schema and parameter set with
    appropriate array sizes and default values.
    
    Args:
        catchment_structure: Either a dictionary containing the catchment structure or a path to a JSON file
        schema_precursor_file (str): Path to the JSON schema precursor file
        output_schema_file (str, optional): Path for the output JSON schema file
        output_parameter_file (str, optional): Path for the output parameter file
        
    Returns:
        tuple: The generated schema and parameter set as dictionaries
        
    Example:
        # Using a JSON file:
        schema, params = generate_parameter_set_json('catchmentStructure.json', 'parameterSetPrecursor.json')
        
        # Using a dictionary:
        catchment = {
            "landCover": {"identifier": {"name": ["Forest", "Urban"], "abbreviation": ["F", "U"]}},
            "bucket": {"identifier": {"name": ["Runoff", "Groundwater"], "abbreviation": ["R", "G"]}},
            "subcatchment": {"identifier": {"name": ["Upper", "Lower"], "abbreviation": ["U", "L"]}},
            "reach": {"identifier": {"name": ["Stream1", "Stream2"], "abbreviation": ["S1", "S2"]}}
        }
        schema, params = generate_parameter_set_json(catchment, 'parameterSetPrecursor.json')
    """
    # Load catchment structure if a file path is provided
    if isinstance(catchment_structure, str):
        try:
            with open(catchment_structure, 'r') as f:
                catchment_structure = json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading catchment structure from file: {e}")
    
    # Verify catchment_structure is a dictionary
    if not isinstance(catchment_structure, dict):
        raise TypeError("catchment_structure must be a dictionary or a path to a JSON file")
    # Set default output filenames if not provided
    if output_schema_file is None:
        output_schema_file = "parameterSet_schema.json"
    if output_parameter_file is None:
        output_parameter_file = "parameterSet.json"
    
    # Get counts from catchment structure
    counts = {
        "bucket_count": len(catchment_structure.get("bucket", {}).get("identifier", {}).get("name", [])),
        "landcover_count": len(catchment_structure.get("landCover", {}).get("identifier", {}).get("name", [])),
        "subcatchment_count": len(catchment_structure.get("subcatchment", {}).get("identifier", {}).get("name", [])),
        "reach_count": len(catchment_structure.get("reach", {}).get("identifier", {}).get("name", []))
    }
    
    # Load schema precursor
    with open(schema_precursor_file, 'r') as f:
        schema_precursor = json.load(f)
    
    # Convert schema precursor to string for easier manipulation
    schema_str = json.dumps(schema_precursor)
    
    # Replace count placeholders
    for count_key, count_value in counts.items():
        schema_str = schema_str.replace(f'"{count_key}"', str(count_value))
    
    # Convert back to dictionary
    schema = json.loads(schema_str)
    
    # Generate parameter set with default values
    parameter_set = generate_default_parameter_set(schema, catchment_structure, counts)
    
    # Save the schema to file
    with open(output_schema_file, 'w') as f:
        json.dump(schema, f, indent=2)
    
    # Save the parameter set to file
    with open(output_parameter_file, 'w') as f:
        json.dump(parameter_set, f, indent=2)
    
    print(f"Schema saved to {output_schema_file}")
    print(f"Parameter set saved to {output_parameter_file}")
    
    return schema, parameter_set

def generate_default_parameter_set(schema, catchment_structure, counts):
    """
    Generate a parameter set with default values based on the schema.
    
    Args:
        schema (dict): The JSON schema
        catchment_structure (dict): The catchment structure
        counts (dict): Dictionary of counts for each component
        
    Returns:
        dict: The generated parameter set
    """
    parameter_set = {}
    
    # Process each main section of the schema
    for section in ["general", "bucket", "landCover", "subcatchment", "reach"]:
        if section in schema["properties"]:
            parameter_set[section] = process_section(
                schema["properties"][section], 
                section, 
                catchment_structure, 
                counts
            )
    
    return parameter_set

def process_section(section_schema, section_name, catchment_structure, counts):
    """
    Process a section of the schema to generate default values.
    
    Args:
        section_schema (dict): Schema for the section
        section_name (str): Name of the section
        catchment_structure (dict): The catchment structure
        counts (dict): Dictionary of counts for each component
        
    Returns:
        dict: The generated section with default values
    """
    # If section_schema is not a dictionary with properties, return empty dict
    if not isinstance(section_schema, dict) or "properties" not in section_schema:
        return {}
    result = {}
    
    # Copy identifier from catchment structure if available
    if "identifier" in section_schema["properties"] and section_name in catchment_structure:
        result["identifier"] = catchment_structure[section_name]["identifier"]
    
    # Process other properties
    for prop_name, prop_schema in section_schema["properties"].items():
        if prop_name == "identifier":
            continue
            
        if prop_schema["type"] == "object":
            result[prop_name] = process_section(prop_schema, f"{section_name}.{prop_name}", catchment_structure, counts)
        elif prop_name == "bucket" and section_name == "landCover":
            # Special handling for landCover.bucket array
            result[prop_name] = []
            for i in range(counts["bucket_count"]):
                bucket_item = process_section(
                    prop_schema["items"], 
                    f"{section_name}.{prop_name}[{i}]", 
                    catchment_structure, 
                    counts
                )
                result[prop_name].append(bucket_item)
        elif prop_schema["type"] == "array":
            result[prop_name] = process_array(prop_schema, prop_name, section_name, counts)
    
    return result

def process_array(array_schema, prop_name, section_name, counts):
    """
    Process an array schema to generate default values.
    
    Args:
        array_schema (dict): Schema for the array
        prop_name (str): Name of the property
        section_name (str): Name of the section
        counts (dict): Dictionary of counts for each component
        
    Returns:
        list: The generated array with default values
    """
    result = []
    
    # Determine the number of items needed
    if "minItems" in array_schema and isinstance(array_schema["minItems"], int):
        num_items = array_schema["minItems"]
    elif "maxItems" in array_schema and isinstance(array_schema["maxItems"], int):
        num_items = array_schema["maxItems"]
    else:
        # Default to 1 if no count specified
        num_items = 1
    
    # Generate array items
    for i in range(num_items):
        if "items" in array_schema:
            item_schema = array_schema["items"]
            
            if item_schema["type"] == "array":
                # Handle nested arrays (e.g., landCoverPercent)
                inner_result = process_array(item_schema, f"{prop_name}[{i}]", section_name, counts)
                result.append(inner_result)
            elif item_schema["type"] == "object":
                # Handle array of objects
                item_result = process_section(item_schema, f"{section_name}.{prop_name}[{i}]", {}, counts)
                result.append(item_result)
            else:
                # Handle simple types
                if "default" in item_schema:
                    result.append(item_schema["default"])
                elif item_schema["type"] == "number":
                    # Use minimum value if no default
                    result.append(item_schema.get("minimum", 0))
                elif item_schema["type"] == "string":
                    result.append("")
                elif item_schema["type"] == "boolean":
                    result.append(False)
                elif item_schema["type"] == ["integer", "null"]:
                    result.append(None)
                else:
                    result.append(None)
    
    return result

def main():
    """
    Main function to demonstrate the parameter set generator usage.
    
    This function shows how to use the generate_parameter_set_json function.
    Run this script directly or import the generate_parameter_set_json function
    into your own code.
    """
    import argparse
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description='Generate INCA parameter set JSON from catchment structure',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument('catchment_structure', type=str,
                        help='Path to catchment structure JSON file')
    
    parser.add_argument('schema_precursor', type=str,
                        help='Path to schema precursor JSON file')
    
    parser.add_argument('--output-schema', type=str, default='parameterSet_schema.json',
                        help='Path for output schema file (default: parameterSet_schema.json)')
    
    parser.add_argument('--output-parameters', type=str, default='parameterSet.json',
                        help='Path for output parameter set file (default: parameterSet.json)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.exists(args.catchment_structure):
        print(f"Error: Catchment structure file '{args.catchment_structure}' not found.")
        return
    
    if not os.path.exists(args.schema_precursor):
        print(f"Error: Schema precursor file '{args.schema_precursor}' not found.")
        return
    
    # Generate parameter set
    try:
        generate_parameter_set_json(
            args.catchment_structure,
            args.schema_precursor,
            args.output_schema,
            args.output_parameters
        )
        print("\nParameter set generation completed successfully!")
    except Exception as e:
        print(f"\nError generating parameter set: {e}")
        
    print("\nUsage examples:")
    print("\n1. From Python code:")
    print("   from parameter_generator import generate_parameter_set_json")
    print("   # Using a JSON file:")
    print("   generate_parameter_set_json('catchmentStructure.json', 'parameterSetPrecursor.json')")
    print("   # Using a dictionary:")
    print("   catchment_dict = {...}  # Your catchment structure dictionary")
    print("   generate_parameter_set_json(catchment_dict, 'parameterSetPrecursor.json')")
    
    print("\n2. From command line:")
    print("   python parameter_generator.py catchmentStructure.json parameterSetPrecursor.json")
    print("   python parameter_generator.py catchmentStructure.json parameterSetPrecursor.json --output-schema my_schema.json --output-parameters my_params.json")

if __name__ == "__main__":
    print("INCA Water Quality Model Parameter Set Generator")
    print("===============================================")
    print("This tool generates parameter set files for the INCA water quality model based on")
    print("catchment structure definitions and a parameter schema precursor.\n")
    
    # Check if this script is being run directly
    if len(sys.argv) == 1:
        print("To use this tool:")
        print("  1. Import the generate_parameter_set_json function into your code, or")
        print("  2. Run this script from the command line with arguments\n")
        print("Command line usage:")
        print("  python parameter_generator.py catchmentStructure.json parameterSetPrecursor.json [OPTIONS]")
        print("\nOptions:")
        print("  --output-schema FILE       Output schema file path (default: parameterSet_schema.json)")
        print("  --output-parameters FILE   Output parameter set file path (default: parameterSet.json)")
        print("\nExample:")
        print("  python parameter_generator.py catchmentStructure.json parameterSetPrecursor.json")
        print("  python parameter_generator.py catchmentStructure.json parameterSetPrecursor.json --output-schema my_schema.json")
        sys.exit(0)
    
    main()