from typing import List, Optional, Union, Dict, Tuple
from uuid import uuid4


class BaseEntity:
    """Base class for all entities with ID, name and abbreviation properties."""
    
    def __init__(self, name: str, abbreviation: str, id: str = None):
        """
        Initialize a new BaseEntity.
        
        Args:
            name: The name of the entity
            abbreviation: The abbreviated name of the entity
            id: The unique identifier (defaults to a generated UUID if not provided)
        """
        self.id = id if id else str(uuid4())
        self.name = name
        self.abbreviation = abbreviation


class Bucket(BaseEntity):
    """
    A hydrological bucket representing a water storage component.
    """
    
    def __init__(self, name: str, abbreviation: str, depth_of_water: float,
                 characteristic_time_constant: float, relative_area: float, id: str = None):
        """
        Initialize a new Bucket.
        
        Args:
            name: The name of the bucket
            abbreviation: The abbreviated name of the bucket
            depth_of_water: Water depth in the bucket (mm)
            characteristic_time_constant: Time constant for water movement (days)
            relative_area: Relative area index of the bucket (0-1)
            id: Optional unique identifier
        """
        super().__init__(name, abbreviation, id)
        self.depth_of_water = depth_of_water
        self.characteristic_time_constant = characteristic_time_constant
        self.relative_area = relative_area
    
    @staticmethod
    def create_default_buckets(num_buckets: int) -> List['Bucket']:
        """
        Create a list of default buckets.
        
        Args:
            num_buckets: Number of buckets to create
            
        Returns:
            List of default Bucket objects
        """
        default_bucket_types = [
            ("Direct Runoff", "DR", 100.0, 1.0, 1.0),
            ("Soilwater", "SW", 200.0, 10.0, 1.0),
            ("Groundwater", "GW", 300.0, 100.0, 1.0),
            ("Quickflow", "QF", 75.0, 0.5, 1.0),
            ("Deep Groundwater", "DGW", 500.0, 500.0, 1.0),
            ("Interflow", "IF", 150.0, 5.0, 1.0),
        ]
        
        buckets = []
        for i in range(num_buckets):
            # Use default types if available, otherwise create generic buckets
            if i < len(default_bucket_types):
                name, abbr, depth, time_const, rel_area = default_bucket_types[i]
            else:
                name = f"Bucket {i+1}"
                abbr = f"B{i+1}"
                depth = 100.0
                time_const = 10.0 * (i + 1)
                rel_area = 1.0
            
            buckets.append(Bucket(name, abbr, depth, time_const, rel_area))
        
        return buckets


class BucketList(List[Bucket]):
    """A list of Bucket objects."""
    
    def __init__(self, buckets: List[Bucket] = None):
        """
        Initialize a new BucketList.
        
        Args:
            buckets: Optional initial list of buckets
        """
        super().__init__(buckets or [])
    
    @staticmethod
    def create_default(num_buckets: int) -> 'BucketList':
        """
        Create a default BucketList with the specified number of buckets.
        
        Args:
            num_buckets: Number of buckets to create
            
        Returns:
            A new BucketList with default buckets
        """
        return BucketList(Bucket.create_default_buckets(num_buckets))
    
    def get_bucket_by_id(self, bucket_id: str) -> Optional[Bucket]:
        """
        Find a bucket by its ID.
        
        Args:
            bucket_id: The ID of the bucket to find
            
        Returns:
            The bucket with the specified ID, or None if not found
        """
        for bucket in self:
            if bucket.id == bucket_id:
                return bucket
        return None


class LandCover(BaseEntity):
    """
    A land cover type with associated hydrological properties.
    """
    
    def __init__(self, name: str, abbreviation: str, bucket_list: BucketList,
                 relative_area: float, rainfall_multiplier: float, snowfall_multiplier: float,
                 snowfall_temperature: float, snowmelt_temperature: float,
                 degree_day_melt_factor: float, id: str = None):
        """
        Initialize a new LandCover.
        
        Args:
            name: The name of the land cover
            abbreviation: The abbreviated name of the land cover
            bucket_list: List of buckets for this land cover
            relative_area: Relative area of this land cover
            rainfall_multiplier: Multiplier for rainfall on this land cover
            snowfall_multiplier: Multiplier for snowfall on this land cover
            snowfall_temperature: Temperature threshold for snowfall (°C)
            snowmelt_temperature: Temperature threshold for snowmelt (°C)
            degree_day_melt_factor: Degree-day factor for snowmelt calculation
            id: Optional unique identifier
        """
        super().__init__(name, abbreviation, id)
        self.bucket_list = bucket_list
        self.relative_area = relative_area
        self.rainfall_multiplier = rainfall_multiplier
        self.snowfall_multiplier = snowfall_multiplier
        self.snowfall_temperature = snowfall_temperature
        self.snowmelt_temperature = snowmelt_temperature
        self.degree_day_melt_factor = degree_day_melt_factor
    
    @staticmethod
    def create_default_land_covers(num_land_covers: int, num_buckets_per_land_cover: int) -> List['LandCover']:
        """
        Create a list of default land covers.
        
        Args:
            num_land_covers: Number of land covers to create
            num_buckets_per_land_cover: Number of buckets per land cover
            
        Returns:
            List of default LandCover objects
        """
        default_land_cover_types = [
            ("Forest", "F", 0.7, 1.0, 1.0, 0.0, 0.0, 3.0),
            ("Agriculture", "A", 0.6, 1.0, 1.0, 0.0, 0.0, 3.0),
            ("Urban", "U", 0.2, 1.2, 0.8, 0.0, 0.0, 4.0),
            ("Wetland", "W", 0.9, 1.0, 1.2, -0.5, 0.5, 2.5),
            ("Grassland", "G", 0.5, 1.0, 1.0, 0.0, 0.0, 3.5),
            ("Bare", "B", 0.1, 1.3, 0.7, 0.0, 0.0, 5.0),
        ]
        
        land_covers = []
        for i in range(num_land_covers):
            # Use default types if available, otherwise create generic land covers
            if i < len(default_land_cover_types):
                name, abbr, rel_area, rain_mult, snow_mult, snow_temp, melt_temp, dd_melt = default_land_cover_types[i]
            else:
                name = f"Land Cover {i+1}"
                abbr = f"LC{i+1}"
                rel_area = 1.0 / num_land_covers  # Equal distribution by default
                rain_mult = 1.0
                snow_mult = 1.0
                snow_temp = 0.0
                melt_temp = 0.0
                dd_melt = 3.0
            
            bucket_list = BucketList.create_default(num_buckets_per_land_cover)
            land_covers.append(LandCover(name, abbr, bucket_list, rel_area, rain_mult, 
                                         snow_mult, snow_temp, melt_temp, dd_melt))
        
        return land_covers


class LandCoverList(List[LandCover]):
    """A list of LandCover objects."""
    
    def __init__(self, land_covers: List[LandCover] = None):
        """
        Initialize a new LandCoverList.
        
        Args:
            land_covers: Optional initial list of land covers
        """
        super().__init__(land_covers or [])
    
    @staticmethod
    def create_default(num_land_covers: int, num_buckets_per_land_cover: int) -> 'LandCoverList':
        """
        Create a default LandCoverList with the specified number of land covers and buckets.
        
        Args:
            num_land_covers: Number of land covers to create
            num_buckets_per_land_cover: Number of buckets per land cover
            
        Returns:
            A new LandCoverList with default land covers
        """
        return LandCoverList(LandCover.create_default_land_covers(num_land_covers, num_buckets_per_land_cover))
    
    def get_land_cover_by_id(self, land_cover_id: str) -> Optional[LandCover]:
        """
        Find a land cover by its ID.
        
        Args:
            land_cover_id: The ID of the land cover to find
            
        Returns:
            The land cover with the specified ID, or None if not found
        """
        for land_cover in self:
            if land_cover.id == land_cover_id:
                return land_cover
        return None


class Reach(BaseEntity):
    """
    A river reach with associated properties.
    """
    
    def __init__(self, name: str, abbreviation: str, length: float,
                 width_at_bottom: float, latitude_of_outflow: float,
                 longitude_of_outflow: float, outflow_reach: Optional['Reach'] = None,
                 id: str = None):
        """
        Initialize a new Reach.
        
        Args:
            name: The name of the reach
            abbreviation: The abbreviated name of the reach
            length: Length of the reach (m)
            width_at_bottom: Width at the bottom of the reach (m)
            latitude_of_outflow: Latitude coordinate of the outflow point
            longitude_of_outflow: Longitude coordinate of the outflow point
            outflow_reach: Optional reach that this reach drains into
            id: Optional unique identifier
        """
        super().__init__(name, abbreviation, id)
        self.length = length
        self.width_at_bottom = width_at_bottom
        self.latitude_of_outflow = latitude_of_outflow
        self.longitude_of_outflow = longitude_of_outflow
        self.outflow_reach = outflow_reach
    
    def set_outflow(self, reach: Optional['Reach']) -> None:
        """
        Set the reach that this reach drains into.
        
        Args:
            reach: The reach that this reach drains into, or None if this is a terminal reach
        """
        self.outflow_reach = reach
    
    @staticmethod
    def create_default_reaches(num_reaches: int, auto_connect: bool = True) -> List['Reach']:
        """
        Create a list of default reaches.
        
        Args:
            num_reaches: Number of reaches to create
            auto_connect: If True, each reach will drain into the next reach in sequence
            
        Returns:
            List of default Reach objects
        """
        reaches = []
        
        # Create reaches with default values
        for i in range(num_reaches):
            # Reaches generally go from upstream to downstream
            name = f"Reach {i+1}"
            abbr = f"R{i+1}"
            
            # Default values that would typically vary by reach position in the network
            length = 1000.0 + i * 500.0  # Typically longer downstream
            width = 5.0 + i * 2.0        # Typically wider downstream
            
            # Simplified lat/long progression (in a real system would follow geography)
            lat = 59.0 + i * 0.01
            lon = 18.0 + i * 0.01
            
            reaches.append(Reach(name, abbr, length, width, lat, lon))
        
        # Connect reaches sequentially if requested
        if auto_connect and num_reaches > 1:
            for i in range(num_reaches - 1):
                reaches[i].outflow_reach = reaches[i + 1]
        
        return reaches
    
    @staticmethod
    def connect_reaches_sequentially(reaches: List['Reach']) -> None:
        """
        Connect a list of reaches sequentially, where each reach drains into the next one.
        
        Args:
            reaches: List of reaches to connect
        """
        if len(reaches) <= 1:
            return
        
        for i in range(len(reaches) - 1):
            reaches[i].outflow_reach = reaches[i + 1]
        
        # The last reach has no outflow
        reaches[-1].outflow_reach = None


class Subcatchment(BaseEntity):
    """
    A subcatchment with associated properties.
    """
    
    def __init__(self, name: str, abbreviation: str, land_cover_list: LandCoverList,
                 area: float, rainfall_multiplier: float, snowfall_multiplier: float,
                 snowfall_temperature: float, snowmelt_temperature: float, id: str = None):
        """
        Initialize a new Subcatchment.
        
        Args:
            name: The name of the subcatchment
            abbreviation: The abbreviated name of the subcatchment
            land_cover_list: List of land covers in this subcatchment
            area: Area of the subcatchment (km²)
            rainfall_multiplier: Multiplier for rainfall on this subcatchment
            snowfall_multiplier: Multiplier for snowfall on this subcatchment
            snowfall_temperature: Temperature threshold for snowfall (°C)
            snowmelt_temperature: Temperature threshold for snowmelt (°C)
            id: Optional unique identifier
        """
        super().__init__(name, abbreviation, id)
        self.land_cover_list = land_cover_list
        self.area = area
        self.rainfall_multiplier = rainfall_multiplier
        self.snowfall_multiplier = snowfall_multiplier
        self.snowfall_temperature = snowfall_temperature
        self.snowmelt_temperature = snowmelt_temperature
    
    @staticmethod
    def create_default_subcatchments(num_subcatchments: int, 
                                     num_land_covers_per_subcatchment: int,
                                     num_buckets_per_land_cover: int) -> List['Subcatchment']:
        """
        Create a list of default subcatchments.
        
        Args:
            num_subcatchments: Number of subcatchments to create
            num_land_covers_per_subcatchment: Number of land covers per subcatchment
            num_buckets_per_land_cover: Number of buckets per land cover
            
        Returns:
            List of default Subcatchment objects
        """
        subcatchments = []
        
        for i in range(num_subcatchments):
            name = f"Subcatchment {i+1}"
            abbr = f"SC{i+1}"
            
            # Create land cover list for this subcatchment
            land_cover_list = LandCoverList.create_default(
                num_land_covers_per_subcatchment, num_buckets_per_land_cover)
            
            # Typically area might be larger for downstream subcatchments
            area = 10.0 + i * 5.0
            
            # Other defaults
            rainfall_mult = 1.0
            snowfall_mult = 1.0
            snowfall_temp = 0.0
            snowmelt_temp = 0.0
            
            subcatchments.append(Subcatchment(
                name, abbr, land_cover_list, area, 
                rainfall_mult, snowfall_mult, snowfall_temp, snowmelt_temp))
        
        return subcatchments


class HRU(BaseEntity):
    """
    A Hydrological Response Unit (HRU) combining a subcatchment and a reach.
    """
    
    def __init__(self, subcatchment: Subcatchment, reach: Reach, id: str = None):
        """
        Initialize a new HRU.
        
        Args:
            subcatchment: The subcatchment part of this HRU
            reach: The reach part of this HRU
            id: Optional unique identifier
        """
        super().__init__(f"{subcatchment.name}-{reach.name}", f"{subcatchment.abbreviation}-{reach.abbreviation}", id)
        self.subcatchment = subcatchment
        self.reach = reach
    
    @staticmethod
    def create_default_hrus(num_hrus: int, 
                           num_land_covers_per_subcatchment: int,
                           num_buckets_per_land_cover: int,
                           auto_connect_reaches: bool = True) -> List['HRU']:
        """
        Create a list of default HRUs.
        
        Args:
            num_hrus: Number of HRUs to create
            num_land_covers_per_subcatchment: Number of land covers per subcatchment
            num_buckets_per_land_cover: Number of buckets per land cover
            auto_connect_reaches: If True, reaches will be connected sequentially
            
        Returns:
            List of default HRU objects
        """
        # Create subcatchments and reaches
        subcatchments = Subcatchment.create_default_subcatchments(
            num_hrus, num_land_covers_per_subcatchment, num_buckets_per_land_cover)
        
        reaches = Reach.create_default_reaches(num_hrus, auto_connect_reaches)
        
        # Create HRUs by pairing subcatchments with reaches
        hrus = []
        for i in range(num_hrus):
            hrus.append(HRU(subcatchments[i], reaches[i]))
        
        return hrus


class Catchment(BaseEntity):
    """
    A catchment containing one or more HRUs.
    """
    
    def __init__(self, name: str, abbreviation: str, description: str,
                 hrus: List[HRU] = None, id: str = None):
        """
        Initialize a new Catchment.
        
        Args:
            name: The name of the catchment
            abbreviation: The abbreviated name of the catchment
            description: Description of the catchment
            hrus: List of HRUs in this catchment (optional)
            id: Optional unique identifier
        """
        super().__init__(name, abbreviation, id)
        self.description = description
        self.hrus = hrus or []
    
    @classmethod
    def create_default(cls, name: str, abbreviation: str, description: str,
                      num_hrus: int = 3,
                      num_land_covers_per_subcatchment: int = 4,
                      num_buckets_per_land_cover: int = 3,
                      auto_connect_reaches: bool = True) -> 'Catchment':
        """
        Create a default catchment with the specified parameters.
        
        Args:
            name: Name of the catchment
            abbreviation: Abbreviation for the catchment
            description: Description of the catchment
            num_hrus: Number of HRUs to create
            num_land_covers_per_subcatchment: Number of land covers per subcatchment
            num_buckets_per_land_cover: Number of buckets per land cover
            auto_connect_reaches: If True, reaches will be connected sequentially
            
        Returns:
            A new Catchment with default components
        """
        hrus = HRU.create_default_hrus(
            num_hrus, num_land_covers_per_subcatchment, 
            num_buckets_per_land_cover, auto_connect_reaches)
        
        return cls(name, abbreviation, description, hrus)
    
    def get_reach_by_id(self, reach_id: str) -> Optional[Reach]:
        """
        Find a reach by its ID.
        
        Args:
            reach_id: The ID of the reach to find
            
        Returns:
            The reach with the specified ID, or None if not found
        """
        for hru in self.hrus:
            if hru.reach.id == reach_id:
                return hru.reach
        return None
    
    def get_subcatchment_by_id(self, subcatchment_id: str) -> Optional[Subcatchment]:
        """
        Find a subcatchment by its ID.
        
        Args:
            subcatchment_id: The ID of the subcatchment to find
            
        Returns:
            The subcatchment with the specified ID, or None if not found
        """
        for hru in self.hrus:
            if hru.subcatchment.id == subcatchment_id:
                return hru.subcatchment
        return None
    
    def get_hru_by_id(self, hru_id: str) -> Optional[HRU]:
        """
        Find an HRU by its ID.
        
        Args:
            hru_id: The ID of the HRU to find
            
        Returns:
            The HRU with the specified ID, or None if not found
        """
        for hru in self.hrus:
            if hru.id == hru_id:
                return hru
        return None
    
    def reconnect_reaches(self, connections: Dict[str, str]) -> None:
        """
        Modify the connections between reaches in the catchment using reach IDs.
        
        Args:
            connections: Dictionary mapping source reach IDs to target reach IDs
                        (target_id of None or empty string makes it a terminal reach)
        """
        # Build a lookup dictionary of reaches by ID
        reaches_by_id = {hru.reach.id: hru.reach for hru in self.hrus}
        
        # Update the connections
        for source_id, target_id in connections.items():
            if source_id in reaches_by_id:
                if target_id in reaches_by_id:
                    reaches_by_id[source_id].outflow_reach = reaches_by_id[target_id]
                elif target_id is None or target_id == "":
                    reaches_by_id[source_id].outflow_reach = None
                else:
                    raise ValueError(f"Target reach with ID {target_id} not found in catchment")
            else:
                raise ValueError(f"Source reach with ID {source_id} not found in catchment")
    
    def get_all_reaches(self) -> Dict[str, Reach]:
        """
        Get a dictionary of all reaches in the catchment, keyed by ID.
        
        Returns:
            Dictionary mapping reach IDs to Reach objects
        """
        return {hru.reach.id: hru.reach for hru in self.hrus}
    
    def get_all_subcatchments(self) -> Dict[str, Subcatchment]:
        """
        Get a dictionary of all subcatchments in the catchment, keyed by ID.
        
        Returns:
            Dictionary mapping subcatchment IDs to Subcatchment objects
        """
        return {hru.subcatchment.id: hru.subcatchment for hru in self.hrus}
    
    def get_all_hrus(self) -> Dict[str, HRU]:
        """
        Get a dictionary of all HRUs in the catchment, keyed by ID.
        
        Returns:
            Dictionary mapping HRU IDs to HRU objects
        """
        return {hru.id: hru for hru in self.hrus}


# Example of how to use these classes:
if __name__ == "__main__":
    # Example 1: Create a catchment with default parameters
    print("==== Example 1: Default Catchment ====")
    default_catchment = Catchment.create_default(
        name="Default River Basin",
        abbreviation="DRB",
        description="A default river basin with automatically generated components",
        num_hrus=3,
        num_land_covers_per_subcatchment=2,
        num_buckets_per_land_cover=3
    )
    
    print(f"Catchment: {default_catchment.name} ({default_catchment.abbreviation})")
    print(f"Description: {default_catchment.description}")
    print(f"Number of HRUs: {len(default_catchment.hrus)}")
    
    # Print reach IDs and connectivity 
    print("\nReach Connectivity by ID:")
    reaches = default_catchment.get_all_reaches()
    for reach_id, reach in reaches.items():
        outflow_id = reach.outflow_reach.id if reach.outflow_reach else "None (terminal)"
        print(f"  {reach.name} (ID: {reach_id}) -> {outflow_id}")
    
    # Example 2: Change reach connectivity using IDs
    print("\n==== Example 2: Modified Reach Connectivity by ID ====")
    # Get the reach IDs for easier reference
    reach_ids = list(reaches.keys())
    
    # Change the connectivity to make the first reach drain directly to the third reach
    connections = {reach_ids[0]: reach_ids[2] if len(reach_ids) > 2 else None}
    default_catchment.reconnect_reaches(connections)
    
    # Print the updated connectivity
    print("Updated Reach Connectivity:")
    for reach_id, reach in reaches.items():
        outflow_id = reach.outflow_reach.id if reach.outflow_reach else "None (terminal)"
        print(f"  {reach.name} (ID: {reach_id}) -> {outflow_id}")
    
    # Example 3: Manual creation of a catchment
    print("\n==== Example 3: Manual Catchment Creation with IDs ====")
    # Create buckets
    quickflow_bucket = Bucket(
        name="Direct Runoff",
        abbreviation="DR",
        depth_of_water=100.0,
        characteristic_time_constant=1.0,
        relative_area=1.0
    )
    
    soil_bucket = Bucket(
        name="Soilwater",
        abbreviation="SW",
        depth_of_water=200.0,
        characteristic_time_constant=10.0,
        relative_area=1.0
    )
    
    groundwater_bucket = Bucket(
        name="Groundwater",
        abbreviation="GW",
        depth_of_water=300.0,
        characteristic_time_constant=100.0,
        relative_area=1.0
    )
    
    # Create a bucket list
    bucket_list = BucketList([quickflow_bucket, soil_bucket, groundwater_bucket])
    
    # Create land covers
    forest = LandCover(
        name="Forest",
        abbreviation="F",
        bucket_list=bucket_list,
        relative_area=0.7,
        rainfall_multiplier=1.0,
        snowfall_multiplier=1.0,
        snowfall_temperature=0.0,
        snowmelt_temperature=0.0,
        degree_day_melt_factor=3.0
    )
    
    agricultural = LandCover(
        name="Agricultural",
        abbreviation="A",
        bucket_list=BucketList([
            Bucket("Ag Runoff", "AR", 80.0, 0.5, 1.0),
            Bucket("Ag Soil", "AS", 150.0, 8.0, 1.0),
            Bucket("Ag Groundwater", "AGW", 250.0, 80.0, 1.0)
        ]),
        relative_area=0.3,
        rainfall_multiplier=1.0,
        snowfall_multiplier=1.0,
        snowfall_temperature=0.0,
        snowmelt_temperature=0.0,
        degree_day_melt_factor=3.0
    )
    
    # Create a land cover list
    land_cover_list = LandCoverList([forest, agricultural])
    
    # Create reaches
    reach3 = Reach(
        name="Downstream",
        abbreviation="R3",
        length=5000.0,
        width_at_bottom=10.0,
        latitude_of_outflow=59.3293,
        longitude_of_outflow=18.0686
    )
    
    reach2 = Reach(
        name="Midstream",
        abbreviation="R2",
        length=4000.0,
        width_at_bottom=7.0,
        latitude_of_outflow=59.3400,
        longitude_of_outflow=18.0600
    )
    
    reach1 = Reach(
        name="Upstream",
        abbreviation="R1",
        length=3000.0,
        width_at_bottom=5.0,
        latitude_of_outflow=59.3500,
        longitude_of_outflow=18.0500
    )
    
    # Set up the reach network (upstream to downstream)
    Reach.connect_reaches_sequentially([reach1, reach2, reach3])
    
    # Create subcatchments
    subcatchment1 = Subcatchment(
        name="Upper Catchment",
        abbreviation="SC1",
        land_cover_list=land_cover_list,
        area=15.0,
        rainfall_multiplier=1.1,
        snowfall_multiplier=1.2,
        snowfall_temperature=0.0,
        snowmelt_temperature=0.0
    )
    
    subcatchment2 = Subcatchment(
        name="Middle Catchment",
        abbreviation="SC2",
        land_cover_list=land_cover_list,
        area=20.0,
        rainfall_multiplier=1.0,
        snowfall_multiplier=1.0,
        snowfall_temperature=0.0,
        snowmelt_temperature=0.0
    )
    
    subcatchment3 = Subcatchment(
        name="Lower Catchment",
        abbreviation="SC3",
        land_cover_list=land_cover_list,
        area=25.0,
        rainfall_multiplier=0.9,
        snowfall_multiplier=0.8,
        snowfall_temperature=0.0,
        snowmelt_temperature=0.0
    )
    
    # Create HRUs
    hru1 = HRU(subcatchment1, reach1)
    hru2 = HRU(subcatchment2, reach2)
    hru3 = HRU(subcatchment3, reach3)
    
    # Create the catchment
    river_catchment = Catchment(
        name="River Valley",
        abbreviation="RV",
        description="A river valley catchment with forest and agricultural land covers",
        hrus=[hru1, hru2, hru3]
    )
    
    # Print information about the catchment
    print(f"Catchment: {river_catchment.name} ({river_catchment.abbreviation})")
    print(f"Description: {river_catchment.description}")
    print(f"Number of HRUs: {len(river_catchment.hrus)}")
    
    # Print reach IDs and connectivity
    print("\nReach Connectivity by ID:")
    for hru in river_catchment.hrus:
        reach = hru.reach
        outflow_id = reach.outflow_reach.id if reach.outflow_reach else "None (terminal)"
        print(f"  {reach.name} (ID: {reach.id}) -> {outflow_id}")
    
    # Modify the connectivity using IDs - make Reach 1 drain directly to Reach 3 (bypass Reach 2)
    print("\nModifying connectivity by ID to create a bypass from Upstream to Downstream...")
    
    connections = {reach1.id: reach3.id}
    river_catchment.reconnect_reaches(connections)
    
    # Print the updated connectivity
    print("Updated Reach Connectivity:")
    for hru in river_catchment.hrus:
        reach = hru.reach
        outflow_id = reach.outflow_reach.id if reach.outflow_reach else "None (terminal)"
        print(f"  {reach.name} (ID: {reach.id}) -> {outflow_id}")
        
    # Print IDs for all components of the first HRU
    hru = river_catchment.hrus[0]
    print(f"\nComponent IDs for HRU {hru.name}:")
    print(f"HRU ID: {hru.id}")
    print(f"Subcatchment ID: {hru.subcatchment.id}")
    print(f"Reach ID: {hru.reach.id}")
    
    # Print land cover IDs
    land_cover_list = hru.subcatchment.land_cover_list
    print(f"\nLand Cover IDs:")
    for land_cover in land_cover_list:
        print(f"  {land_cover.name}: {land_cover.id}")
    
    # Print bucket IDs
    print(f"\nBucket IDs for {land_cover_list[0].name}:")
    for bucket in land_cover_list[0].bucket_list:
        print(f"  {bucket.name}: {bucket.id}")
    
    # Example of how to find objects by ID
    print("\n==== Example 4: Finding Objects by ID ====")
    
    # Get all IDs
    all_reaches = river_catchment.get_all_reaches()
    all_subcatchments = river_catchment.get_all_subcatchments()
    all_hrus = river_catchment.get_all_hrus()
    
    # Find a specific reach by ID
    sample_reach_id = list(all_reaches.keys())[0]
    found_reach = river_catchment.get_reach_by_id(sample_reach_id)
    print(f"Found reach by ID {sample_reach_id}: {found_reach.name}")
    
    # Find a specific subcatchment by ID
    sample_subcatchment_id = list(all_subcatchments.keys())[0]
    found_subcatchment = river_catchment.get_subcatchment_by_id(sample_subcatchment_id)
    print(f"Found subcatchment by ID {sample_subcatchment_id}: {found_subcatchment.name}")
    
    # Find a specific HRU by ID
    sample_hru_id = list(all_hrus.keys())[0]
    found_hru = river_catchment.get_hru_by_id(sample_hru_id)
    print(f"Found HRU by ID {sample_hru_id}: {found_hru.name}")
