import json
import csv
from typing import List, Dict, Any, Optional


class Bucket:
    """Describes water movement and storage in a hydrological bucket"""
    
    def __init__(self, name: str, abbreviation: str, receives_precipitation: bool = False):
        self.name = name
        self.abbreviation = abbreviation
        self.receives_precipitation = receives_precipitation
        self.general = {}
        self.hydrology = {}
        self.soil_or_sediment = {}
        self.chemistry = {}
    
    def __str__(self):
        return f"Bucket({self.name}, {self.abbreviation})"


class LandCover:
    """Represents a type of land cover with associated buckets"""
    
    def __init__(self, name: str, abbreviation: str, general_properties: Dict[str, Any],
                 precipitation_properties: Dict[str, Any], routing_properties: Dict[str, Any],
                 soil_or_sediment: Dict[str, Any], chemistry: Dict[str, Any], buckets: List[Bucket]):
        self.name = name
        self.abbreviation = abbreviation
        self.general = general_properties
        self.precipitation = precipitation_properties
        self.routing = routing_properties
        self.soil_or_sediment = soil_or_sediment
        self.chemistry = chemistry
        self.buckets = buckets
    
    def __str__(self):
        return f"LandCover({self.name}, Buckets: {len(self.buckets)})"


class Reach:
    """Defines the properties of a river section"""
    
    def __init__(self, name: str, abbreviation: str, general_properties: Dict[str, Any],
                 hydrology_properties: Dict[str, Any], soil_or_sediment: Dict[str, Any],
                 chemistry: Dict[str, Any]):
        self.name = name
        self.abbreviation = abbreviation
        self.general = general_properties
        self.hydrology = hydrology_properties
        self.soil_or_sediment = soil_or_sediment
        self.chemistry = chemistry
    
    def __str__(self):
        return f"Reach({self.name}, {self.abbreviation})"


class Subcatchment:
    """Includes a reach and one or more LandCover types"""
    
    def __init__(self, name: str, abbreviation: str, general_properties: Dict[str, Any],
                 hydrology_properties: Dict[str, Any], soil_or_sediment: Dict[str, Any],
                 chemistry: Dict[str, Any], reach: Reach, land_covers: List[LandCover],
                 land_cover_percentages: List[float]):
        self.name = name
        self.abbreviation = abbreviation
        self.general = general_properties
        self.hydrology = hydrology_properties
        self.soil_or_sediment = soil_or_sediment
        self.chemistry = chemistry
        self.reach = reach
        self.land_covers = land_covers
        self.land_cover_percentages = land_cover_percentages
    
    def __str__(self):
        return f"Subcatchment({self.name}, Reach: {self.reach.name}, LandCovers: {len(self.land_covers)})"


class Catchment:
    """Consists of one or more subcatchments"""
    
    def __init__(self, subcatchments: List[Subcatchment]):
        self.subcatchments = subcatchments
    
    def __str__(self):
        return f"Catchment(Subcatchments: {len(self.subcatchments)})"


class TimeSeries:
    """Represents time series data for the model"""
    
    def __init__(self, csv_path: str):
        self.data = self._read_csv(csv_path)
    
    def _read_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Read CSV file and return as a list of dictionaries"""
        result = []
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric values to float or int where appropriate
                converted_row = {}
                for key, value in row.items():
                    try:
                        # Try to convert to float first
                        float_val = float(value)
                        # If it's an integer, convert to int
                        if float_val.is_integer():
                            converted_row[key] = int(float_val)
                        else:
                            converted_row[key] = float_val
                    except (ValueError, TypeError):
                        # Keep as string if conversion fails
                        converted_row[key] = value
                result.append(converted_row)
        return result
    
    def __str__(self):
        return f"TimeSeries(Rows: {len(self.data)})"


class Model:
    """Consists of a catchment and one or more time series"""
    
    def __init__(self, catchment: Catchment, time_series: List[TimeSeries]):
        self.catchment = catchment
        self.time_series = time_series
    
    def __str__(self):
        return f"Model(Catchment: {self.catchment}, TimeSeries: {len(self.time_series)})"


class HydrologyModelFactory:
    """Factory class to create a Model from the JSON configuration"""
    
    @staticmethod
    def create_buckets(bucket_config: Dict[str, Any]) -> List[Bucket]:
        """Create Bucket instances from configuration"""
        bucket_names = bucket_config["identifier"]["name"]
        bucket_abbreviations = bucket_config["identifier"]["abbreviation"]
        receives_precipitation = bucket_config["general"]["receivesPrecipitation"]
        
        buckets = []
        for i, name in enumerate(bucket_names):
            bucket = Bucket(name, bucket_abbreviations[i], 
                          receives_precipitation[i].lower() == "true")
            buckets.append(bucket)
        
        return buckets
    
    @staticmethod
    def create_land_covers(land_cover_config: Dict[str, Any], buckets: List[Bucket]) -> List[LandCover]:
        """Create LandCover instances from configuration"""
        land_cover_names = land_cover_config["identifier"]["name"]
        land_cover_abbreviations = land_cover_config["identifier"]["abbreviation"]
        bucket_configs = land_cover_config.get("bucket", [])
        
        land_covers = []
        for i, name in enumerate(land_cover_names):
            # Create instances of all buckets for this land cover
            land_cover_buckets = []
            for bucket_idx, bucket in enumerate(buckets):
                if bucket_idx < len(bucket_configs):
                    # Configure the bucket with specific properties
                    bucket_copy = Bucket(bucket.name, bucket.abbreviation, 
                                       bucket.receives_precipitation)
                    bucket_copy.general = bucket_configs[bucket_idx].get("general", {})
                    bucket_copy.hydrology = bucket_configs[bucket_idx].get("hydrology", {})
                    bucket_copy.soil_or_sediment = bucket_configs[bucket_idx].get("soilOrSediment", {})
                    bucket_copy.chemistry = bucket_configs[bucket_idx].get("chemistry", {})
                    land_cover_buckets.append(bucket_copy)
            
            land_cover = LandCover(
                name=name,
                abbreviation=land_cover_abbreviations[i],
                general_properties=land_cover_config.get("general", {}),
                precipitation_properties=land_cover_config.get("precipitation", {}),
                routing_properties=land_cover_config.get("routing", {}),
                soil_or_sediment=land_cover_config.get("soilOrSediment", {}),
                chemistry=land_cover_config.get("chemistry", {}),
                buckets=land_cover_buckets
            )
            land_covers.append(land_cover)
        
        return land_covers
    
    @staticmethod
    def create_reaches(reach_config: Dict[str, Any]) -> List[Reach]:
        """Create Reach instances from configuration"""
        reach_names = reach_config["identifier"]["name"]
        reach_abbreviations = reach_config["identifier"]["abbreviation"]
        
        reaches = []
        for i, name in enumerate(reach_names):
            reach = Reach(
                name=name,
                abbreviation=reach_abbreviations[i],
                general_properties=reach_config.get("general", {}),
                hydrology_properties=reach_config.get("hydrology", {}),
                soil_or_sediment=reach_config.get("soilOrSediment", {}),
                chemistry=reach_config.get("chemistry", {})
            )
            reaches.append(reach)
        
        return reaches
    
    @staticmethod
    def create_subcatchments(subcatchment_config: Dict[str, Any], reaches: List[Reach], 
                           land_covers: List[LandCover]) -> List[Subcatchment]:
        """Create Subcatchment instances from configuration"""
        subcatchment_names = subcatchment_config["identifier"]["name"]
        subcatchment_abbreviations = subcatchment_config["identifier"]["abbreviation"]
        land_cover_percentages = subcatchment_config["general"]["landCoverPercent"]
        
        subcatchments = []
        for i, name in enumerate(subcatchment_names):
            # Get the corresponding reach (assuming same index)
            reach = reaches[i] if i < len(reaches) else reaches[0]
            
            # Get land cover percentages for this subcatchment
            subcatchment_percentages = land_cover_percentages[i]
            
            subcatchment = Subcatchment(
                name=name,
                abbreviation=subcatchment_abbreviations[i],
                general_properties=subcatchment_config.get("general", {}),
                hydrology_properties=subcatchment_config.get("hydrology", {}),
                soil_or_sediment=subcatchment_config.get("soilOrSediment", {}),
                chemistry=subcatchment_config.get("chemistry", {}),
                reach=reach,
                land_covers=land_covers,
                land_cover_percentages=subcatchment_percentages
            )
            subcatchments.append(subcatchment)
        
        return subcatchments
    
    @staticmethod
    def create_model_from_json(json_path: str, time_series_paths: List[str]) -> Model:
        """Create a Model instance from JSON configuration and time series files"""
        with open(json_path, 'r') as f:
            config = json.load(f)
        
        # Create buckets
        buckets = HydrologyModelFactory.create_buckets(config["bucket"])
        
        # Create land covers
        land_covers = HydrologyModelFactory.create_land_covers(config["landCover"], buckets)
        
        # Create reaches
        reaches = HydrologyModelFactory.create_reaches(config["reach"])
        
        # Create subcatchments
        subcatchments = HydrologyModelFactory.create_subcatchments(
            config["subcatchment"], reaches, land_covers)
        
        # Create catchment
        catchment = Catchment(subcatchments)
        
        # Create time series
        time_series = [TimeSeries(path) for path in time_series_paths]
        
        # Create the model
        model = Model(catchment, time_series)
        
        return model


# Example usage
if __name__ == "__main__":
    # Example of how to use the classes
    json_path = "parameterSet.json"
    time_series_paths = ["timeseries1.csv", "timeseries2.csv"]
    
    try:
        model = HydrologyModelFactory.create_model_from_json(json_path, time_series_paths)
        print(model)
        
        # Accessing model components
        for subcatchment in model.catchment.subcatchments:
            print(f"\nSubcatchment: {subcatchment}")
            print(f"Reach: {subcatchment.reach}")
            
            for i, land_cover in enumerate(subcatchment.land_covers):
                percentage = subcatchment.land_cover_percentages[i]
                print(f"LandCover: {land_cover} ({percentage}%)")
                
                for bucket in land_cover.buckets:
                    print(f"  Bucket: {bucket}")
    
    except Exception as e:
        print(f"Error: {e}")