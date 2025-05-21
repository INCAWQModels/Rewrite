from typing import List, Optional, Dict, Any


class Bucket:
    """Represents a single water storage bucket in the model."""
    
    def __init__(self, name: str, abbreviation: str, receives_precipitation: bool = False):
        # Identifier
        self.name = name
        self.abbreviation = abbreviation
        
        # General properties
        self.receives_precipitation = receives_precipitation
        
        # These will be populated for each land cover type
        self.initial_soil_temperature = 5.0
        self.relative_area_index = 1.0
        self.soil_temperature_effective_depth = 30.0
        
        # Hydrology properties
        self.characteristic_time_constant = 1.0
        self.tightly_bound_water_depth = 10.0
        self.loosely_bound_water_depth = 50.0
        self.freely_draining_water_depth = 50.0
        self.initial_water_depth = 100.0
        self.relative_et_index = 0.0
        self.et_scaling_exponent = 1.0
        self.infiltration_threshold_temperature = 0.0
        
        # Chemistry properties
        self.soil_temperature_offset = 20.0
        self.soil_temperature_exponent = 2.0


class LandCoverType:
    """Represents a single land cover type (e.g., Forest, Urban, etc.)."""
    
    def __init__(self, name: str, abbreviation: str):
        # Identifier
        self.name = name
        self.abbreviation = abbreviation
        
        # General - Soil Temperature Model
        self.c_s = 1.0e7
        self.k_t = 0.6
        self.c_ice = 9.0e6
        self.f_s = -3.0
        
        # General - Evapotranspiration Model
        self.temperature_offset = 0.0
        self.scaling_factor = 70.0
        
        # Precipitation properties
        self.degree_day_melt_factor = 3.0
        self.rainfall_multiplier = 1.0
        self.snowfall_multiplier = 1.0
        self.snowfall_temperature = 0.0
        self.snowmelt_temperature = 0.0
        self.snowmelt_rate = 3.0
        self.snow_depth = 0.0
        
        # Routing - flow matrix to other buckets (will be a 5x5 matrix for 5 buckets)
        self.flow_matrix = [[0.0 for _ in range(5)] for _ in range(5)]
        
        # Bucket-specific properties for this land cover
        self.bucket_properties = {}  # Will store bucket-specific overrides


class Subcatchment:
    """Represents the land surface component of an HRU."""
    
    def __init__(self, area: float = 10.0):
        # General properties
        self.area = area
        self.latitude_at_outflow = 0.0
        self.longitude_at_outflow = 0.0
        
        # Land cover percentages (one value per land cover type)
        self.land_cover_percent = {}  # Will be populated with {land_cover_type: percentage}
        
        # Hydrology properties
        self.rainfall_multiplier = 1.0
        self.snowfall_multiplier = 1.0
        self.snowfall_temperature = 0.0
        self.snowmelt_temperature = 0.0


class Reach:
    """Represents a river reach within an HRU."""
    
    def __init__(self, length: float = 10000.0):
        # General properties
        self.length = length
        self.width_at_bottom = 10.0
        self.slope = 0.0001
        self.outflow_to = None  # Index of downstream HRU (None if outlet)
        self.inflows_from = []  # List of upstream HRU indices
        
        # Hydrology properties
        self.has_abstraction = False
        self.has_effluent = False
        
        # Manning equation parameters
        self.manning_a = 2.71
        self.manning_b = 0.557
        self.manning_c = 0.349
        self.manning_f = 0.341
        self.manning_n = 0.1
        
        self.initial_flow = 1.0


class HRU:
    """Hydrological Response Unit - contains subcatchment and reach."""
    
    def __init__(self, name: str, abbreviation: str = None):
        self.name = name
        self.abbreviation = abbreviation or name[:3].upper()
        
        # Components
        self.subcatchment = Subcatchment()
        self.reach = Reach()
        
        # Index in the HRU list (will be set when added to catchment)
        self.index = None


class Catchment:
    """Main catchment class containing all model components."""
    
    def __init__(self, id: str = "XXX", name: str = "New parameter set", creator: str = "Anonymous"):
        # General properties
        self.id = id
        self.name = name
        self.creator = creator
        
        # Collections of instances
        self.buckets = []  # List of Bucket instances
        self.land_cover_types = []  # List of LandCoverType instances
        self.hrus = []  # List of HRU instances
    
    def add_bucket(self, bucket: Bucket):
        """Add a bucket to the catchment."""
        self.buckets.append(bucket)
    
    def add_land_cover_type(self, land_cover: LandCoverType):
        """Add a land cover type to the catchment."""
        self.land_cover_types.append(land_cover)
    
    def add_hru(self, hru: HRU):
        """Add an HRU to the catchment."""
        hru.index = len(self.hrus)
        self.hrus.append(hru)
        
        # Initialize land cover percentages for the subcatchment
        for lc in self.land_cover_types:
            hru.subcatchment.land_cover_percent[lc] = 100.0 / len(self.land_cover_types)
    
    def connect_hrus(self, upstream_index: int, downstream_index: int):
        """Connect two HRUs in series."""
        if upstream_index < len(self.hrus) and downstream_index < len(self.hrus):
            self.hrus[upstream_index].reach.outflow_to = downstream_index
            self.hrus[downstream_index].reach.inflows_from.append(upstream_index)
    
    def get_bucket_by_name(self, name: str) -> Optional[Bucket]:
        """Find a bucket by name."""
        for bucket in self.buckets:
            if bucket.name == name:
                return bucket
        return None
    
    def get_land_cover_by_name(self, name: str) -> Optional[LandCoverType]:
        """Find a land cover type by name."""
        for lc in self.land_cover_types:
            if lc.name == name:
                return lc
        return None
    
    def get_hru_by_name(self, name: str) -> Optional[HRU]:
        """Find an HRU by name."""
        for hru in self.hrus:
            if hru.name == name:
                return hru
        return None


# Example usage
if __name__ == "__main__":
    # Create a new catchment
    catchment = Catchment(id="TEST001", name="Test Catchment", creator="John Doe")
    
    # Manually add buckets
    bucket_data = [
        ("Direct runoff", "DR", False),
        ("Upper Unsaturated", "US", False),
        ("Lower Unsaturated", "LS", False),
        ("Upper Groundwater", "UG", False),
        ("Lower Groundwater", "LG", False)
    ]
    
    for name, abbrev, precip in bucket_data:
        catchment.add_bucket(Bucket(name, abbrev, precip))
    
    # Manually add land cover types
    land_cover_data = [
        ("Forest", "F"),
        ("Wetland", "W"),
        ("Arable", "A"),
        ("Pasture", "P"),
        ("Urban", "U"),
        ("Industrial", "I")
    ]
    
    for name, abbrev in land_cover_data:
        catchment.add_land_cover_type(LandCoverType(name, abbrev))
    
    # Add HRUs
    hru_names = ["Top", "Upper Middle", "Lower Middle", "Bottom"]
    for name in hru_names:
        hru = HRU(name)
        catchment.add_hru(hru)
    
    # Connect HRUs in a linear chain
    for i in range(len(catchment.hrus) - 1):
        catchment.connect_hrus(i, i + 1)
    
    # Modify land cover percentages for the first HRU
    top_hru = catchment.get_hru_by_name("Top")
    forest = catchment.get_land_cover_by_name("Forest")
    urban = catchment.get_land_cover_by_name("Urban")
    
    if top_hru and forest and urban:
        # Set custom land cover percentages
        top_hru.subcatchment.land_cover_percent[forest] = 60.0
        top_hru.subcatchment.land_cover_percent[urban] = 10.0
        # Remaining 30% distributed among other types
    
    # Modify flow routing for Forest land cover
    if forest:
        # Example: 50% of direct runoff goes to upper unsaturated
        forest.flow_matrix[0][1] = 0.5
    
    # Print catchment structure
    print(f"Catchment: {catchment.name}")
    print(f"Number of HRUs: {len(catchment.hrus)}")
    print(f"Number of Land Cover Types: {len(catchment.land_cover_types)}")
    print(f"Number of Buckets: {len(catchment.buckets)}")
    
    print("\nHRU Connections:")
    for hru in catchment.hrus:
        outflow = f"HRU {hru.reach.outflow_to}" if hru.reach.outflow_to is not None else "Outlet"
        print(f"  {hru.name} → {outflow}")
