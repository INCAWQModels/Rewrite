import json
import datetime
import uuid
from typing import List, Dict, Any, Optional, Union, Set, Tuple
from uuid import uuid4

# Assuming the Catchment and other hydrological classes are imported
# from hydrological_classes import Catchment, HRU, Subcatchment, Reach, LandCover, Bucket, BucketList, LandCoverList

# Assuming the TimeSeries class is imported
# from time_series import TimeSeries

class Model:
    """
    A hydrological model combining a catchment with time series data.
    
    The Model class represents a complete hydrological model with both:
    1. A catchment representing the physical environment (HRUs, reaches, subcatchments, etc.)
    2. One or more time series containing data for model input and output
    3. Meteorological time series (met_ts) with temperature and precipitation data associated with HRUs
    """
    
    def __init__(self, name: str, description: str, catchment: 'Catchment', 
                 time_series: Optional[List['TimeSeries']] = None, 
                 external_time_step: float = 86400.0, 
                 internal_time_step: float = 3600.0,
                 id: str = None):
        """
        Initialize a new hydrological model.
        
        Args:
            name: Name of the model
            description: Description of the model
            catchment: Catchment object representing the physical environment
            time_series: Optional list of TimeSeries objects (default: empty list)
            external_time_step: Time step for input/output data in seconds (default: 86400.0 - daily)
            internal_time_step: Computational time step in seconds (default: 3600.0 - hourly)
            id: Optional unique identifier (default: generate UUID)
        """
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description
        self.catchment = catchment
        self.time_series = time_series or []
        self.external_time_step = external_time_step  # Time step for input/output data (seconds)
        self.internal_time_step = internal_time_step  # Computational time step (seconds)
        self.creation_date = datetime.datetime.now()
        self.metadata = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creation_date": self.creation_date.isoformat(),
            "catchment_id": self.catchment.id,
            "external_time_step": self.external_time_step,
            "internal_time_step": self.internal_time_step
        }
        
        # Dictionary to track meteorological time series mappings
        # Keys: met_ts UUIDs, Values: lists of HRU IDs
        self.met_ts_mappings = {}
        
    def add_time_series(self, time_series: 'TimeSeries') -> None:
        """
        Add a TimeSeries object to the model.
        
        Args:
            time_series: TimeSeries object to add
        """
        self.time_series.append(time_series)
        # Update metadata to track the time series
        if "time_series_ids" not in self.metadata:
            self.metadata["time_series_ids"] = []
        if hasattr(time_series, 'uuid'):
            self.metadata["time_series_ids"].append(time_series.uuid)
    
    def add_met_timeseries(self, time_series: 'TimeSeries', hru_ids: List[str]) -> None:
        """
        Add a meteorological TimeSeries object and associate it with specific HRUs.
        
        Args:
            time_series: Meteorological TimeSeries object containing temperature and precipitation data
            hru_ids: List of HRU IDs that this met_ts should be associated with
        
        Raises:
            ValueError: If an HRU is already associated with another met_ts or if an HRU ID doesn't exist
        """
        # Verify the time series contains temperature and precipitation
        has_temp = False
        has_precip = False
        
        # Check if the columns indicate temperature and precipitation
        if hasattr(time_series, 'columns'):
            col_names = [col.lower() if isinstance(col, str) else col for col in time_series.columns]
            has_temp = any('temp' in col.lower() if isinstance(col, str) else False for col in time_series.columns)
            has_precip = any(precip in col.lower() if isinstance(col, str) else False 
                          for col in time_series.columns for precip in ['precip', 'rainfall', 'rain'])
        
        # Check metadata as an alternative
        if hasattr(time_series, 'metadata'):
            if 'data_type' in time_series.metadata:
                data_type = time_series.metadata['data_type'].lower() if isinstance(time_series.metadata['data_type'], str) else ''
                if 'met' in data_type or 'meteorological' in data_type:
                    # If metadata explicitly says it's meteorological data, assume it has both
                    has_temp = True
                    has_precip = True
                elif 'temp' in data_type:
                    has_temp = True
                elif any(p in data_type for p in ['precip', 'rainfall', 'rain']):
                    has_precip = True
        
        # Warn if the time series doesn't seem to have both temperature and precipitation
        if not (has_temp and has_precip):
            print(f"Warning: Meteorological time series {time_series.uuid if hasattr(time_series, 'uuid') else 'unknown'} "
                  f"may not contain both temperature and precipitation data.")
        
        # Verify HRU IDs exist
        all_hrus = self.catchment.get_all_hrus()
        for hru_id in hru_ids:
            if hru_id not in all_hrus:
                raise ValueError(f"HRU ID {hru_id} does not exist in the catchment")
        
        # Verify HRUs aren't already assigned to another met_ts
        for existing_ts_uuid, existing_hru_ids in self.met_ts_mappings.items():
            overlap = set(existing_hru_ids).intersection(set(hru_ids))
            if overlap:
                raise ValueError(f"HRUs {overlap} are already associated with met_ts {existing_ts_uuid}")
        
        # Add the time series if it's not already added
        ts_uuid = time_series.uuid if hasattr(time_series, 'uuid') else None
        if ts_uuid:
            if not any(ts.uuid == ts_uuid for ts in self.time_series if hasattr(ts, 'uuid')):
                self.add_time_series(time_series)
            
            # Create the mapping
            self.met_ts_mappings[ts_uuid] = hru_ids
        else:
            raise ValueError("Meteorological time series must have a UUID")
    
    def remove_time_series(self, time_series_uuid: str) -> bool:
        """
        Remove a TimeSeries object from the model by UUID.
        
        Args:
            time_series_uuid: UUID of the TimeSeries to remove
            
        Returns:
            True if the TimeSeries was found and removed, False otherwise
        """
        for i, ts in enumerate(self.time_series):
            if hasattr(ts, 'uuid') and ts.uuid == time_series_uuid:
                del self.time_series[i]
                # Update metadata
                if "time_series_ids" in self.metadata:
                    self.metadata["time_series_ids"].remove(time_series_uuid)
                
                # Remove from met_ts mappings if present
                if time_series_uuid in self.met_ts_mappings:
                    del self.met_ts_mappings[time_series_uuid]
                
                return True
        return False
    
    def get_time_series(self, time_series_uuid: str) -> Optional['TimeSeries']:
        """
        Get a TimeSeries object by UUID.
        
        Args:
            time_series_uuid: UUID of the TimeSeries to retrieve
            
        Returns:
            The TimeSeries object if found, None otherwise
        """
        for ts in self.time_series:
            if hasattr(ts, 'uuid') and ts.uuid == time_series_uuid:
                return ts
        return None
    
    def get_time_series_by_name(self, name: str) -> List['TimeSeries']:
        """
        Get all TimeSeries objects with the specified name.
        
        Args:
            name: Name of the TimeSeries objects to retrieve
            
        Returns:
            List of TimeSeries objects with the specified name
        """
        return [ts for ts in self.time_series if hasattr(ts, 'name') and ts.name == name]
    
    def get_time_series_by_location(self, location: str) -> Dict[str, 'TimeSeries']:
        """
        Get all TimeSeries objects that contain data for the specified location.
        
        Args:
            location: Location identifier to filter by
            
        Returns:
            Dictionary mapping TimeSeries UUID to TimeSeries object
        """
        result = {}
        for ts in self.time_series:
            # Check if the time series has data for this location
            location_data = ts.get_data_by_location(location) if hasattr(ts, 'get_data_by_location') else []
            if location_data:
                result[ts.uuid] = ts
        return result
    
    def get_time_series_for_reach(self, reach_id: str) -> Dict[str, 'TimeSeries']:
        """
        Get all TimeSeries objects that contain data for the specified reach.
        
        Args:
            reach_id: ID of the reach to filter by
            
        Returns:
            Dictionary mapping TimeSeries UUID to TimeSeries object
        """
        # Get the reach by ID
        reach = self.catchment.get_reach_by_id(reach_id)
        if not reach:
            return {}
        
        # Get time series for this reach's location
        # Assuming the location identifier in the time series is the reach name or ID
        reach_ts = self.get_time_series_by_location(reach.name)
        reach_ts.update(self.get_time_series_by_location(reach.id))
        
        return reach_ts
    
    def get_time_series_for_subcatchment(self, subcatchment_id: str) -> Dict[str, 'TimeSeries']:
        """
        Get all TimeSeries objects that contain data for the specified subcatchment.
        
        Args:
            subcatchment_id: ID of the subcatchment to filter by
            
        Returns:
            Dictionary mapping TimeSeries UUID to TimeSeries object
        """
        # Get the subcatchment by ID
        subcatchment = self.catchment.get_subcatchment_by_id(subcatchment_id)
        if not subcatchment:
            return {}
        
        # Get time series for this subcatchment's location
        # Assuming the location identifier in the time series is the subcatchment name or ID
        subcatchment_ts = self.get_time_series_by_location(subcatchment.name)
        subcatchment_ts.update(self.get_time_series_by_location(subcatchment.id))
        
        return subcatchment_ts
    
    def get_met_timeseries_for_hru(self, hru_id: str) -> Optional['TimeSeries']:
        """
        Get the meteorological time series (met_ts) associated with a specific HRU.
        
        Args:
            hru_id: ID of the HRU
            
        Returns:
            The TimeSeries object if found, None otherwise
        """
        # Check if the HRU exists
        hru = self.catchment.get_hru_by_id(hru_id)
        if not hru:
            return None
        
        # Find the met_ts UUID associated with this HRU
        for ts_uuid, hru_ids in self.met_ts_mappings.items():
            if hru_id in hru_ids:
                # Return the time series object
                return self.get_time_series(ts_uuid)
        
        return None
    
    def get_hrus_for_met_timeseries(self, time_series_uuid: str) -> List[str]:
        """
        Get the list of HRU IDs associated with a specific meteorological time series.
        
        Args:
            time_series_uuid: UUID of the meteorological time series
            
        Returns:
            List of HRU IDs
        """
        return self.met_ts_mappings.get(time_series_uuid, [])
    
    def validate_met_timeseries_coverage(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that all HRUs are covered by exactly one met_ts.
        
        Returns:
            Tuple of:
            - Boolean indicating if all HRUs are covered by exactly one met_ts
            - List of uncovered HRU IDs
            - List of HRU IDs with multiple met_ts
        """
        all_hrus = set(self.catchment.get_all_hrus().keys())
        covered_hrus = set()
        multiple_coverage = set()
        
        # Track which HRUs are covered by which met_ts
        coverage_map = {}
        for ts_uuid, hru_ids in self.met_ts_mappings.items():
            for hru_id in hru_ids:
                if hru_id in coverage_map:
                    multiple_coverage.add(hru_id)
                    coverage_map[hru_id].append(ts_uuid)
                else:
                    coverage_map[hru_id] = [ts_uuid]
                covered_hrus.add(hru_id)
        
        # Find uncovered HRUs
        uncovered_hrus = all_hrus - covered_hrus
        
        # Check if all HRUs are covered exactly once
        all_covered_exactly_once = (len(uncovered_hrus) == 0) and (len(multiple_coverage) == 0)
        
        return all_covered_exactly_once, list(uncovered_hrus), list(multiple_coverage)
    
    def get_time_series_for_hru(self, hru_id: str) -> Dict[str, 'TimeSeries']:
        """
        Get all TimeSeries objects that contain data for the specified HRU.
        
        Args:
            hru_id: ID of the HRU to filter by
            
        Returns:
            Dictionary mapping TimeSeries UUID to TimeSeries object
        """
        # Get the HRU by ID
        hru = self.catchment.get_hru_by_id(hru_id)
        if not hru:
            return {}
        
        # Get time series for this HRU's location
        # Assuming the location identifier in the time series is the HRU name or ID
        hru_ts = self.get_time_series_by_location(hru.name)
        hru_ts.update(self.get_time_series_by_location(hru.id))
        
        # Also get time series for the HRU's subcatchment and reach
        hru_ts.update(self.get_time_series_for_subcatchment(hru.subcatchment.id))
        hru_ts.update(self.get_time_series_for_reach(hru.reach.id))
        
        # Add the meteorological time series if it exists
        met_ts = self.get_met_timeseries_for_hru(hru_id)
        if met_ts and hasattr(met_ts, 'uuid'):
            hru_ts[met_ts.uuid] = met_ts
        
        return hru_ts
    
    def get_time_range(self) -> Tuple[Optional[datetime.datetime], Optional[datetime.datetime]]:
        """
        Get the overall time range covered by all time series in the model.
        
        Returns:
            Tuple of (start_time, end_time), or (None, None) if no time series data
        """
        if not self.time_series:
            return None, None
        
        start_times = []
        end_times = []
        
        for ts in self.time_series:
            if not hasattr(ts, 'data') or not ts.data:
                continue
            
            # Assuming the first column of each row is the timestamp
            timestamps = [row[0] for row in ts.data if len(row) > 0 and isinstance(row[0], datetime.datetime)]
            if timestamps:
                start_times.append(min(timestamps))
                end_times.append(max(timestamps))
        
        if not start_times or not end_times:
            return None, None
        
        return min(start_times), max(end_times)
    
    def set_time_steps(self, external_time_step: float, internal_time_step: float) -> None:
        """
        Set the external and internal time steps for the model.
        
        Args:
            external_time_step: Time step for input/output data in seconds
            internal_time_step: Computational time step in seconds
        
        Raises:
            ValueError: If time steps are not positive
        """
        if external_time_step <= 0 or internal_time_step <= 0:
            raise ValueError("Time steps must be positive")
        
        self.external_time_step = external_time_step
        self.internal_time_step = internal_time_step
        
        # Update metadata
        self.metadata["external_time_step"] = external_time_step
        self.metadata["internal_time_step"] = internal_time_step
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add a metadata key-value pair to the model.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary representation.
        
        Returns:
            Dictionary representation of the model
        """
        # Convert catchment to dictionary using the schema converter
        from schema_converter import model_to_json
        catchment_dict = model_to_json(self.catchment)
        
        # Create basic model dictionary
        model_dict = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "creation_date": self.creation_date.isoformat(),
            "external_time_step": self.external_time_step,
            "internal_time_step": self.internal_time_step,
            "metadata": self.metadata,
            "catchment": catchment_dict,
            "time_series": [],
            "met_ts_mappings": self.met_ts_mappings
        }
        
        # Add time series UUIDs
        for ts in self.time_series:
            if hasattr(ts, 'uuid'):
                model_dict["time_series"].append(ts.uuid)
        
        return model_dict
    
    @classmethod
    def from_dict(cls, model_dict: Dict[str, Any], time_series_dict: Dict[str, 'TimeSeries'] = None) -> 'Model':
        """
        Create a Model object from a dictionary representation.
        
        Args:
            model_dict: Dictionary representation of the model
            time_series_dict: Optional dictionary mapping UUIDs to TimeSeries objects
                            (if not provided, the model will have empty time series)
        
        Returns:
            A new Model object
        """
        # Convert catchment from dictionary using the schema converter
        from schema_converter import json_to_model
        catchment = json_to_model(model_dict["catchment"])
        
        # Get time steps
        external_time_step = model_dict.get("external_time_step", 86400.0)
        internal_time_step = model_dict.get("internal_time_step", 3600.0)
        
        # Create the model object
        model = cls(
            name=model_dict["name"],
            description=model_dict["description"],
            catchment=catchment,
            external_time_step=external_time_step,
            internal_time_step=internal_time_step,
            id=model_dict["id"]
        )
        
        # Set creation date
        if "creation_date" in model_dict:
            try:
                model.creation_date = datetime.datetime.fromisoformat(model_dict["creation_date"])
            except ValueError:
                # If the date format cannot be parsed, keep the current creation date
                pass
        
        # Set metadata
        if "metadata" in model_dict:
            model.metadata = model_dict["metadata"]
        
        # Add time series if provided
        if time_series_dict and "time_series" in model_dict:
            for ts_uuid in model_dict["time_series"]:
                if ts_uuid in time_series_dict:
                    model.add_time_series(time_series_dict[ts_uuid])
        
        # Restore met_ts mappings
        if "met_ts_mappings" in model_dict:
            model.met_ts_mappings = model_dict["met_ts_mappings"]
        
        return model
    
    def save_to_files(self, base_name: str = None) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Save the model to files.
        
        Args:
            base_name: Base name for the output files (default: model name)
        
        Returns:
            Tuple of (model_json_path, list of (csv_path, json_path) for each time series)
        """
        # Determine the base name for files
        base_name = base_name or self.name
        if not base_name:
            base_name = f"model_{self.id}"
        
        # Save model as JSON
        model_dict = self.to_dict()
        model_json_path = f"{base_name}_model.json"
        with open(model_json_path, 'w') as json_file:
            json.dump(model_dict, json_file, indent=2)
        
        # Save time series files
        time_series_paths = []
        for i, ts in enumerate(self.time_series):
            if hasattr(ts, 'save_to_files'):
                ts_base_name = f"{base_name}_timeseries_{i+1}" if not hasattr(ts, 'name') or not ts.name else f"{base_name}_{ts.name}"
                csv_path, json_path = ts.save_to_files(ts_base_name)
                time_series_paths.append((csv_path, json_path))
        
        return model_json_path, time_series_paths
    
    @classmethod
    def load_from_files(cls, model_json_path: str, load_time_series: bool = True) -> 'Model':
        """
        Load a model from files.
        
        Args:
            model_json_path: Path to the model JSON file
            load_time_series: Whether to load time series files (default: True)
        
        Returns:
            A new Model object
        """
        # Load model from JSON
        with open(model_json_path, 'r') as json_file:
            model_dict = json.load(json_file)
        
        # Load time series if requested
        time_series_dict = {}
        if load_time_series and "time_series" in model_dict:
            from time_series import TimeSeries
            
            # Extract directory from model JSON path
            import os
            dir_path = os.path.dirname(model_json_path)
            base_name = os.path.splitext(os.path.basename(model_json_path))[0]
            base_name = base_name.replace("_model", "")
            
            # Try to load each time series
            for ts_uuid in model_dict["time_series"]:
                # Look for JSON metadata file for this time series
                ts_json_path = os.path.join(dir_path, f"{base_name}_{ts_uuid}.json")
                ts_csv_path = os.path.join(dir_path, f"{base_name}_{ts_uuid}.csv")
                
                # Try alternative naming patterns if files don't exist
                if not os.path.exists(ts_json_path):
                    # Try to find a matching JSON file in the directory
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.json') and ts_uuid in filename and "_model" not in filename:
                            ts_json_path = os.path.join(dir_path, filename)
                            ts_csv_path = os.path.join(dir_path, filename.replace('.json', '.csv'))
                            break
                
                # Load time series if files exist
                if os.path.exists(ts_json_path) and os.path.exists(ts_csv_path):
                    # Implementation would depend on TimeSeries class load functionality
                    # This is a simplified example
                    ts = TimeSeries()
                    # Load CSV data and JSON metadata
                    # ...
                    time_series_dict[ts_uuid] = ts
        
        # Create and return the model
        return cls.from_dict(model_dict, time_series_dict)
    
    def __str__(self) -> str:
        """
        Get a string representation of the model.
        
        Returns:
            String representation
        """
        # Validate met_ts coverage
        is_valid, uncovered, multiple = self.validate_met_timeseries_coverage()
        coverage_status = "All HRUs covered by exactly one met_ts" if is_valid else \
                         f"Invalid met_ts coverage: {len(uncovered)} HRUs not covered, {len(multiple)} HRUs with multiple met_ts"
        
        # Get time range
        time_range = self.get_time_range()
        time_range_str = f"from {time_range[0].isoformat()} to {time_range[1].isoformat()}" if time_range[0] and time_range[1] else "no data"
        
        # Format time steps
        ext_ts_str = self.format_time_step(self.external_time_step)
        int_ts_str = self.format_time_step(self.internal_time_step)
        
        return (f"Model '{self.name}' (ID: {self.id})\n"
                f"Description: {self.description}\n"
                f"Time Steps: External={ext_ts_str}, Internal={int_ts_str}\n"
                f"Catchment: {self.catchment.name} with {len(self.catchment.hrus)} HRUs\n"
                f"Time Series: {len(self.time_series)} series, {time_range_str}\n"
                f"Met TS: {len(self.met_ts_mappings)} meteorological time series\n"
                f"Met TS Coverage: {coverage_status}")
    
    @staticmethod
    def format_time_step(seconds: float) -> str:
        """Format a time step in seconds to a human-readable string."""
        if seconds >= 86400:
            return f"{seconds/86400:.1f} days"
        elif seconds >= 3600:
            return f"{seconds/3600:.1f} hours"
        elif seconds >= 60:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds:.1f} seconds"


