import json
import random
import string
import argparse
from datetime import datetime, date
import uuid
import re
import os

class JSONSchemaGenerator:
    def __init__(self):
        self.type_generators = {
            "string": self._generate_string,
            "number": self._generate_number,
            "integer": self._generate_integer,
            "boolean": self._generate_boolean,
            "array": self._generate_array,
            "object": self._generate_object,
            "null": self._generate_null
        }
        
        self.format_generators = {
            "date-time": self._generate_datetime,
            "date": self._generate_date,
            "time": self._generate_time,
            "email": self._generate_email,
            "hostname": self._generate_hostname,
            "ipv4": self._generate_ipv4,
            "ipv6": self._generate_ipv6,
            "uri": self._generate_uri,
            "uuid": self._generate_uuid
        }

    def generate(self, schema):
        """Generate a JSON instance from a JSON schema."""
        return self._generate_value(schema)

    def _generate_value(self, schema):
        """Generate a value according to the schema."""
        # Use default value if available
        if "default" in schema:
            return schema["default"]
            
        if "const" in schema:
            return schema["const"]
        
        if "enum" in schema:
            return random.choice(schema["enum"])
        
        schema_type = schema.get("type")
        
        # Handle multiple possible types
        if isinstance(schema_type, list):
            selected_type = random.choice(schema_type)
            temp_schema = schema.copy()
            temp_schema["type"] = selected_type
            return self._generate_value(temp_schema)
        
        # Handle anyOf, oneOf, allOf
        if "anyOf" in schema:
            return self._generate_value(random.choice(schema["anyOf"]))
        if "oneOf" in schema:
            return self._generate_value(random.choice(schema["oneOf"]))
        if "allOf" in schema:
            # Merge all schemas in allOf
            merged_schema = {}
            for subschema in schema["allOf"]:
                merged_schema.update(subschema)
            return self._generate_value(merged_schema)
            
        # Default to object if no type is specified
        if not schema_type:
            schema_type = "object"
            
        # Generate based on type
        generator = self.type_generators.get(schema_type)
        if generator:
            return generator(schema)
        else:
            return None

    def _generate_string(self, schema):
        """Generate a string value according to schema."""
        string_format = schema.get("format")
        if string_format and string_format in self.format_generators:
            return self.format_generators[string_format]()
        
        # Handle pattern
        if "pattern" in schema:
            # This is a simplified version, for complex patterns a library like exrex would be better
            pattern = schema["pattern"]
            if pattern == "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$":
                return self._generate_email()
            elif pattern.startswith("^[0-9]{") and pattern.endswith("}$"):
                # Match patterns like "^[0-9]{5}$" for zip codes
                digits = int(pattern[7:-2])
                return ''.join(random.choices(string.digits, k=digits))
            else:
                # Fallback for unsupported patterns
                return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        min_length = schema.get("minLength", 1)
        max_length = schema.get("maxLength", min_length + 20)
        length = random.randint(min_length, max_length)
        
        # Check if there are examples to draw from
        if "examples" in schema and schema["examples"]:
            return random.choice(schema["examples"])
            
        # Default string generation
        return ''.join(random.choices(string.ascii_letters + ' ', k=length))

    def _generate_number(self, schema):
        """Generate a number according to schema."""
        minimum = schema.get("minimum", -100.0)
        maximum = schema.get("maximum", 100.0)
        
        if "exclusiveMinimum" in schema:
            minimum = schema["exclusiveMinimum"] + 0.000001
        if "exclusiveMaximum" in schema:
            maximum = schema["exclusiveMaximum"] - 0.000001
            
        multiple_of = schema.get("multipleOf")
        if multiple_of:
            # Generate a number that is a multiple of multipleOf
            base = random.uniform(minimum / multiple_of, maximum / multiple_of)
            return round(multiple_of * round(base), 10)
        
        return round(random.uniform(minimum, maximum), 2)

    def _generate_integer(self, schema):
        """Generate an integer according to schema."""
        minimum = int(schema.get("minimum", -100))
        maximum = int(schema.get("maximum", 100))
        
        if "exclusiveMinimum" in schema:
            minimum = int(schema["exclusiveMinimum"]) + 1
        if "exclusiveMaximum" in schema:
            maximum = int(schema["exclusiveMaximum"]) - 1
            
        multiple_of = schema.get("multipleOf")
        if multiple_of:
            # Generate an integer that is a multiple of multipleOf
            base = random.randint(minimum // multiple_of, maximum // multiple_of)
            return multiple_of * base
        
        return random.randint(minimum, maximum)

    def _generate_boolean(self, schema):
        """Generate a boolean value."""
        return random.choice([True, False])

    def _generate_array(self, schema):
        """Generate an array according to schema."""
        # Check for default items first
        if "default" in schema:
            return schema["default"]
            
        min_items = schema.get("minItems", 0)
        max_items = schema.get("maxItems", min_items + 5)
        num_items = random.randint(min_items, max_items)
        
        # Use items schema for all elements
        items_schema = schema.get("items", {})
        
        # Check for uniqueness constraint
        unique_items = schema.get("uniqueItems", False)
        
        result = []
        for _ in range(num_items):
            value = self._generate_value(items_schema)
            # Ensure uniqueness if required
            if unique_items:
                while value in result:
                    value = self._generate_value(items_schema)
            result.append(value)
        
        return result

    def _generate_object(self, schema):
        """Generate an object according to schema."""
        result = {}
        
        # Handle required properties first
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for prop_name in required:
            if prop_name in properties:
                result[prop_name] = self._generate_value(properties[prop_name])
        
        # Handle optional properties based on probability
        for prop_name, prop_schema in properties.items():
            if prop_name not in result:  # Skip already generated required properties
                # Use default if available
                if "default" in prop_schema:
                    result[prop_name] = prop_schema["default"]
                # Otherwise generate with 70% probability
                elif random.random() < 0.7:
                    result[prop_name] = self._generate_value(prop_schema)
        
        # Handle additional properties if allowed
        additional_props = schema.get("additionalProperties", {})
        if additional_props and isinstance(additional_props, dict):
            # Add some random additional properties
            for _ in range(random.randint(0, 3)):
                prop_name = f"additional_{_}_{''.join(random.choices(string.ascii_lowercase, k=5))}"
                result[prop_name] = self._generate_value(additional_props)
                
        return result

    def _generate_null(self, schema):
        """Generate a null value."""
        return None

    # Format generators
    def _generate_datetime(self):
        """Generate a date-time string."""
        year = random.randint(2000, 2024)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Simplification to avoid month-specific limits
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"

    def _generate_date(self):
        """Generate a date string."""
        year = random.randint(2000, 2024)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{year:04d}-{month:02d}-{day:02d}"

    def _generate_time(self):
        """Generate a time string."""
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{hour:02d}:{minute:02d}:{second:02d}"

    def _generate_email(self):
        """Generate an email address."""
        user = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = ''.join(random.choices(string.ascii_lowercase, k=6))
        tld = random.choice(["com", "org", "net", "edu"])
        return f"{user}@{domain}.{tld}"

    def _generate_hostname(self):
        """Generate a hostname."""
        subdomain = ''.join(random.choices(string.ascii_lowercase, k=8))
        domain = ''.join(random.choices(string.ascii_lowercase, k=6))
        tld = random.choice(["com", "org", "net"])
        return f"{subdomain}.{domain}.{tld}"

    def _generate_ipv4(self):
        """Generate an IPv4 address."""
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))

    def _generate_ipv6(self):
        """Generate an IPv6 address."""
        return ':'.join(f"{random.randint(0, 65535):04x}" for _ in range(8))

    def _generate_uri(self):
        """Generate a URI."""
        protocols = ["http", "https", "ftp"]
        protocol = random.choice(protocols)
        domain = self._generate_hostname()
        path = '/'.join(''.join(random.choices(string.ascii_lowercase, k=5)) for _ in range(random.randint(1, 3)))
        return f"{protocol}://{domain}/{path}"

    def _generate_uuid(self):
        """Generate a UUID."""
        return str(uuid.uuid4())

def read_schema_file(file_path):
    """Read and parse a JSON schema file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json_file(data, output_file):
    """Write data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Generate JSON data from a JSON schema.')
    parser.add_argument('schema_file', help='Path to the JSON schema file')
    parser.add_argument('-o', '--output', default='output.json', help='Output JSON file path')
    parser.add_argument('-n', '--num_instances', type=int, default=1, help='Number of instances to generate')
    parser.add_argument('--ignore-defaults', action='store_true', help='Ignore default values in the schema')
    args = parser.parse_args()
    
    try:
        schema = read_schema_file(args.schema_file)
        generator = JSONSchemaGenerator()
        
        # If ignore-defaults is specified, remove default values from schema
        if args.ignore_defaults:
            def remove_defaults(s):
                if isinstance(s, dict):
                    if "default" in s:
                        del s["default"]
                    for key, value in list(s.items()):
                        if isinstance(value, (dict, list)):
                            remove_defaults(value)
                elif isinstance(s, list):
                    for item in s:
                        if isinstance(item, (dict, list)):
                            remove_defaults(item)
                return s
            
            schema = remove_defaults(schema)
        
        if args.num_instances > 1:
            result = [generator.generate(schema) for _ in range(args.num_instances)]
        else:
            result = generator.generate(schema)
            
        write_json_file(result, args.output)
        print(f"Successfully generated JSON data and saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())