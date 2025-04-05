import json

def extract_names_by_level(json_file):
    # Load the JSON data from file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Dictionaries to store names by level
    top_level_names = []
    second_level_names = []
    third_level_names = []
    fourth_level_names = []
    
    # Extract names at each level
    for top_key, top_value in data.items():
        if isinstance(top_value, dict) and "name" in top_value:
            top_level_names.append(top_value["name"])
            
        # Check for second level
        for second_key, second_value in top_value.items():
            if isinstance(second_value, dict) and "name" in second_value:
                second_level_names.append(second_value["name"])
                
            # Check for third level
            if isinstance(second_value, dict):
                for third_key, third_value in second_value.items():
                    if isinstance(third_value, dict) and "name" in third_value:
                        third_level_names.append(third_value["name"])
                        
                    # Check for fourth level
                    if isinstance(third_value, dict):
                        for fourth_key, fourth_value in third_value.items():
                            if isinstance(fourth_value, dict) and "name" in fourth_value:
                                fourth_level_names.append(fourth_value["name"])
    
    # Print the names by level
    print("Top Level Names:")
    for name in top_level_names:
        print(f"  - {name}")
    
    print("\nSecond Level Names:")
    for name in second_level_names:
        print(f"  - {name}")
    
    print("\nThird Level Names:")
    for name in third_level_names:
        print(f"  - {name}")
    
    print("\nFourth Level Names:")
    for name in fourth_level_names:
        print(f"  - {name}")

# Example usage
if __name__ == "__main__":
    extract_names_by_level("testLevels.json")