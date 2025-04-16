import json
import random
import argparse
import datetime
from typing import Any, Dict, List, Union, Optional


def merge_data(schema_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge input data with schema-generated data.
    Input data takes precedence over schema-generated data.
    
    Args:
        schema_data: Data generated from schema
        input_data: Input data to override schema values
        
    Returns:
        Merged data
    """
    result = schema_data.copy()
    
    if not isinstance(input_data, dict) or not isinstance(schema_data, dict):
        return input_data if input_data is not None else schema_data
    
    for key, value in input_data.items():
        if key in schema_data:
            if isinstance(value, dict) and isinstance(schema_data[key], dict):
                result[key] = merge_data(schema_data[key], value)
            else:
                result[key] = value
        else:
            result[key] = value
            
    return result


def generate_from_schema(schema: Dict[str, Any]) -> Any:
    """
    Generate a valid instance based on a JSON schema.
    
    Args:
        schema: The JSON schema as a dictionary
        
    Returns:
        A valid instance according to the schema
    """
    schema_type = schema.get("type")
    
    # Use default if available
    if "default" in schema:
        return schema["default"]
    
    if schema_type == "object":
        result = {}
        # Handle required properties
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for prop_name, prop_schema in properties.items():
            if prop_name in required or random.random() > 0.2:  # Include required and some optional props
                result[prop_name] = generate_from_schema(prop_schema)
        return result
    
    elif schema_type == "array":
        result = []
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 0)
        max_items = schema.get("maxItems", min_items)
        
        # Generate exactly min_items if specified
        num_items = min_items if min_items == max_items else random.randint(min_items, max_items)
        
        if isinstance(items_schema, dict):
            # All items follow the same schema
            for _ in range(num_items):
                result.append(generate_from_schema(items_schema))
        elif isinstance(items_schema, list):
            # Each position has its own schema
            for i in range(min(num_items, len(items_schema))):
                result.append(generate_from_schema(items_schema[i]))
        
        return result
    
    elif schema_type == "string":
        if schema.get("format") == "uri":
            return schema.get("default", "https://example.org")
        elif schema.get("pattern") and "\\d{4}-\\d{2}-\\d{2}" in schema.get("pattern"):
            # Date format
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif schema.get("pattern") and "[0-9a-f]" in schema.get("pattern"):
            # Commit hash
            return "1a2b3c4d5e6f7a8b9c0d"
        else:
            min_length = schema.get("minLength", 1)
            max_length = schema.get("maxLength", min_length + 10)
            length = random.randint(min_length, max_length)
            return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))
    
    elif schema_type == "number" or schema_type == "integer":
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", minimum + 100)
        
        if schema_type == "integer":
            return random.randint(minimum, maximum)
        else:
            # Generate a number with reasonable precision
            value = random.uniform(minimum, maximum)
            return round(value, 2)
    
    elif isinstance(schema_type, list):
        # Handle multiple types (union type)
        if "null" in schema_type and len(schema_type) > 1:
            if random.random() > 0.5:
                return None
            else:
                non_null_types = [t for t in schema_type if t != "null"]
                return generate_from_schema({"type": random.choice(non_null_types)})
        else:
            return generate_from_schema({"type": random.choice(schema_type)})
    
    elif schema_type == "boolean":
        return random.choice([True, False])
    
    else:
        # Default to null for unknown types
        return None


def fix_identifier_spelling(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix 'identifer' typo in the schema by standardizing to 'identifier'
    
    Args:
        data: Generated data that may contain 'identifer' typos
        
    Returns:
        Data with standardized identifiers
    """
    # Fix the typo in reach and subcatchment if needed
    for key in ['subcatchment', 'reach']:
        if key in data and 'identifer' in data[key]:
            data[key]['identifier'] = data[key].pop('identifer')
    
    return data


def generate_json_from_schema_file(schema_file: str, input_file: str = None, output_file: str = None) -> None:
    """
    Generate a JSON instance from a schema file and optionally write to an output file.
    
    Args:
        schema_file: Path to the JSON schema file
        input_file: Optional path to input data file with predefined values
        output_file: Optional path to write the generated JSON instance
        
    Returns:
        None
    """
    # Load schema
    with open(schema_file, 'r') as f:
        schema = json.load(f)
    
    # Generate instance from schema
    instance = generate_from_schema(schema)
    
    # Load input data if provided
    if input_file:
        try:
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            
            # Merge input data with schema-generated instance
            instance = merge_data(instance, input_data)
            
            # Fix the spelling of 'identifer' to 'identifier' if needed
            instance = fix_identifier_spelling(instance)
            
            print(f"Successfully merged input data from {input_file}")
        except Exception as e:
            print(f"Warning: Could not load input file: {str(e)}")
    
    # Write to file or return
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(instance, f, indent=2)
        print(f"JSON instance written to {output_file}")
    else:
        print(json.dumps(instance, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a JSON instance from a JSON schema file")
    parser.add_argument("schema_file", help="Path to the JSON schema file")
    parser.add_argument("-i", "--input", help="Input file with predefined values (optional)")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    generate_json_from_schema_file(args.schema_file, args.input, args.output)