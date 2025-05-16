import tkinter as tk
from tkinter import ttk
import json
import re

def format_key(key):
    """
    Format a camelCase key to 'Title Case With Spaces Before Caps'
    e.g., 'firstDayOut' -> 'First Day Out'
    """
    # Insert space before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', key)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
    # Capitalize the first letter
    return s2.capitalize()

class PERSiSTViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("PERSiST Parameter Viewer")
        self.root.geometry("900x700")

        # Load parameter data
        try:
            with open('PERSiSTParameter.json', 'r') as file:
                self.parameters = json.load(file)
        except FileNotFoundError:
            tk.Label(self.root, text="Error: PERSiSTParameter.json file not found").pack(pady=20)
            return
        
        # Load headings data for abbreviations
        try:
            with open('headings.json', 'r') as file:
                self.headings = json.load(file)
        except FileNotFoundError:
            self.headings = {}
        
        # Create main notebook for top-level tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames for top-level tabs
        self.landcover_frame = ttk.Frame(self.main_notebook)
        self.subcatchment_frame = ttk.Frame(self.main_notebook)
        self.reach_frame = ttk.Frame(self.main_notebook)
        
        # Add frames to main notebook
        self.main_notebook.add(self.landcover_frame, text="Land Cover")
        self.main_notebook.add(self.subcatchment_frame, text="Subcatchment")
        self.main_notebook.add(self.reach_frame, text="Reach")
        
        # Create and populate notebooks for each top-level tab
        self.create_landcover_notebook()
        self.create_subcatchment_notebook()
        self.create_reach_notebook()
    
    def create_landcover_notebook(self):
        """Create and populate the land cover notebook"""
        # Create notebook for land cover tab
        landcover_notebook = ttk.Notebook(self.landcover_frame)
        landcover_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Get land cover types
        landcover_types = self.parameters['landCover']['identifier']['name']
        
        # Add a tab for each land cover type
        for lc_type in landcover_types:
            frame = ttk.Frame(landcover_notebook)
            landcover_notebook.add(frame, text=lc_type)
            
            # Create scrollable frame
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add land cover data to the frame
            self.populate_landcover_tab(scrollable_frame, lc_type, landcover_types)
    
    def populate_landcover_tab(self, frame, lc_type, landcover_types):
        """Populate a land cover tab with data"""
        idx = landcover_types.index(lc_type)
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create a pane for soil temperature model
        soil_temp_frame = ttk.LabelFrame(main_frame, text="Soil Temperature Model")
        soil_temp_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Add soil temperature model data
        for key in self.parameters['landCover']['general']['soilTemperatureModel']:
            row = ttk.Frame(soil_temp_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['landCover']['general']['soilTemperatureModel'][key][idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for evapotranspiration model
        evap_frame = ttk.LabelFrame(main_frame, text="Evapotranspiration Model")
        evap_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Add evapotranspiration model data
        for key in self.parameters['landCover']['general']['evapotranspirationModel']:
            row = ttk.Frame(evap_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['landCover']['general']['evapotranspirationModel'][key][idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for precipitation
        precip_frame = ttk.LabelFrame(main_frame, text="Precipitation")
        precip_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Add precipitation data
        for key in self.parameters['landCover']['precipitation']:
            row = ttk.Frame(precip_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['landCover']['precipitation'][key][idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for flow routing matrix
        routing_frame = ttk.LabelFrame(main_frame, text="Routing Flow Matrix")
        routing_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Add flow matrix
        self.display_flow_matrix(routing_frame, idx)
        
        # Create a pane for buckets
        bucket_frame = ttk.LabelFrame(main_frame, text="Buckets")
        bucket_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create notebook for buckets
        bucket_notebook = ttk.Notebook(bucket_frame)
        bucket_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        bucket_types = self.parameters['bucket']['identifier']['name']
        bucket_abbrs = self.parameters['bucket']['identifier']['abbreviation']
        
        # Add a tab for each bucket
        for b_idx, bucket in enumerate(self.parameters['landCover']['bucket']):
            bucket_name = bucket_types[b_idx]
            bucket_abbr = bucket_abbrs[b_idx] if b_idx < len(bucket_abbrs) else f"B{b_idx+1}"
            
            bucket_frame = ttk.Frame(bucket_notebook)
            bucket_notebook.add(bucket_frame, text=bucket_abbr)
            
            # Create scrollable frame for the bucket
            canvas = tk.Canvas(bucket_frame)
            scrollbar = ttk.Scrollbar(bucket_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate the bucket tab
            self.populate_bucket_tab(scrollable_frame, bucket, bucket_name, idx)
    
    def display_flow_matrix(self, parent_frame, landcover_idx):
        """Display the flow matrix for a specific land cover type"""
        # Get bucket names and abbreviations
        bucket_names = self.parameters['bucket']['identifier']['name']
        bucket_abbrs = self.parameters['bucket']['identifier']['abbreviation']
        num_buckets = len(bucket_names)
        
        # Get the flow matrix for this land cover type
        flow_matrix = self.parameters['landCover']['routing']['flowMatrix'][landcover_idx]
        
        # Create frame to hold the matrix
        matrix_frame = ttk.Frame(parent_frame)
        matrix_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add empty cell in top-left corner
        ttk.Label(matrix_frame, text="", width=12).grid(row=0, column=0, padx=2, pady=2)
        
        # Add column headers (bucket abbreviations)
        for col_idx, abbr in enumerate(bucket_abbrs):
            ttk.Label(matrix_frame, text=abbr, font=("TkDefaultFont", 10, "bold"), width=6).grid(
                row=0, column=col_idx+1, padx=2, pady=2)
        
        # Add row identifiers (bucket names) and matrix values
        for row_idx, bucket_name in enumerate(bucket_names):
            # Add row label
            ttk.Label(matrix_frame, text=bucket_name, font=("TkDefaultFont", 9), anchor="e", width=12).grid(
                row=row_idx+1, column=0, sticky="e", padx=2, pady=2)
            
            # Add matrix values for this row
            for col_idx in range(num_buckets):
                value = flow_matrix[row_idx][col_idx]
                value_label = ttk.Label(matrix_frame, text=str(value), width=6)
                value_label.grid(row=row_idx+1, column=col_idx+1, padx=2, pady=2)
                
                # Add visual hint for non-zero values to make the connections more obvious
                if value > 0:
                    value_label.configure(background="#e0f0ff")
    
    def populate_bucket_tab(self, frame, bucket, bucket_name, landcover_idx):
        """Populate a bucket tab with data for a specific land cover type"""
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add bucket name header
        ttk.Label(main_frame, text=bucket_name, font=("TkDefaultFont", 11, "bold")).pack(anchor="w", padx=5, pady=2)
        
        # Add general bucket data in a pane
        general_frame = ttk.LabelFrame(main_frame, text="General")
        general_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in bucket['general']:
            row = ttk.Frame(general_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            if key == 'initialSoilTemperature':
                ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = bucket['general'][key]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
            elif isinstance(bucket['general'][key], list):
                ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = bucket['general'][key][landcover_idx]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Add hydrology data in a pane
        hydrology_frame = ttk.LabelFrame(main_frame, text="Hydrology")
        hydrology_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in bucket['hydrology']:
            row = ttk.Frame(hydrology_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = bucket['hydrology'][key][landcover_idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Add chemistry data if it exists
        if 'chemistry' in bucket and 'general' in bucket['chemistry']:
            chemistry_frame = ttk.LabelFrame(main_frame, text="Chemistry")
            chemistry_frame.pack(fill="x", expand=False, padx=5, pady=5)
            
            for key in bucket['chemistry']['general']:
                row = ttk.Frame(chemistry_frame)
                row.pack(fill="x", padx=5, pady=2)
                
                ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = bucket['chemistry']['general'][key][landcover_idx]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
    
    def create_subcatchment_notebook(self):
        """Create and populate the subcatchment notebook"""
        # Create notebook for subcatchment tab
        subcatchment_notebook = ttk.Notebook(self.subcatchment_frame)
        subcatchment_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Get HRU names
        hru_names = self.parameters['HRU']['identifier']['name']
        
        # Get HRU abbreviations if available
        hru_abbrs = []
        if 'HRU' in self.headings and 'identifier' in self.headings['HRU'] and 'abbreviation' in self.headings['HRU']['identifier']:
            hru_abbrs = self.headings['HRU']['identifier']['abbreviation']
        else:
            hru_abbrs = [f"SC{i+1}" for i in range(len(hru_names))]
        
        # Add a tab for each subcatchment (HRU)
        for i, hru_name in enumerate(hru_names):
            abbr = hru_abbrs[i] if i < len(hru_abbrs) else f"SC{i+1}"
            frame = ttk.Frame(subcatchment_notebook)
            subcatchment_notebook.add(frame, text=abbr)
            
            # Create scrollable frame
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate the subcatchment tab
            self.populate_subcatchment_tab(scrollable_frame, i, hru_name)
    
    def populate_subcatchment_tab(self, frame, idx, hru_name):
        """Populate a subcatchment tab with data"""
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add subcatchment name header
        ttk.Label(main_frame, text=f"Subcatchment: {hru_name}", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        
        # Create a pane for general subcatchment data
        general_frame = ttk.LabelFrame(main_frame, text="General")
        general_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in self.parameters['HRU']['subcatchment']['general']:
            if key != 'landCoverPercent':  # Handle landCoverPercent separately
                row = ttk.Frame(general_frame)
                row.pack(fill="x", padx=5, pady=2)
                
                ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = self.parameters['HRU']['subcatchment']['general'][key][idx]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for land cover percentage data
        landcover_frame = ttk.LabelFrame(main_frame, text="Land Cover Percentages")
        landcover_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        landcover_names = self.parameters['landCover']['identifier']['name']
        landcover_percentages = self.parameters['HRU']['subcatchment']['general']['landCoverPercent'][idx]
        
        for i, lc_name in enumerate(landcover_names):
            if i < len(landcover_percentages):
                row = ttk.Frame(landcover_frame)
                row.pack(fill="x", padx=5, pady=2)
                
                ttk.Label(row, text=f"{lc_name}:", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = landcover_percentages[i]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for hydrology data
        hydrology_frame = ttk.LabelFrame(main_frame, text="Hydrology")
        hydrology_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in self.parameters['HRU']['subcatchment']['hydrology']:
            row = ttk.Frame(hydrology_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['HRU']['subcatchment']['hydrology'][key][idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)
    
    def create_reach_notebook(self):
        """Create and populate the reach notebook"""
        # Create notebook for reach tab
        reach_notebook = ttk.Notebook(self.reach_frame)
        reach_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Get HRU names
        hru_names = self.parameters['HRU']['identifier']['name']
        
        # Get HRU abbreviations if available
        hru_abbrs = []
        if 'HRU' in self.headings and 'identifier' in self.headings['HRU'] and 'abbreviation' in self.headings['HRU']['identifier']:
            hru_abbrs = self.headings['HRU']['identifier']['abbreviation']
        else:
            hru_abbrs = [f"SC{i+1}" for i in range(len(hru_names))]
        
        # Add a tab for each reach (HRU)
        for i, hru_name in enumerate(hru_names):
            abbr = hru_abbrs[i] if i < len(hru_abbrs) else f"SC{i+1}"
            frame = ttk.Frame(reach_notebook)
            reach_notebook.add(frame, text=abbr)
            
            # Create scrollable frame
            canvas = tk.Canvas(frame)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, canvas=canvas: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate the reach tab
            self.populate_reach_tab(scrollable_frame, i, hru_name)
    
    def populate_reach_tab(self, frame, idx, hru_name):
        """Populate a reach tab with data"""
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add reach name header
        ttk.Label(main_frame, text=f"Reach: {hru_name}", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        
        # Create a pane for general reach data
        general_frame = ttk.LabelFrame(main_frame, text="General")
        general_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in self.parameters['HRU']['reach']['general']:
            row = ttk.Frame(general_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['HRU']['reach']['general'][key][idx]
            
            if key == 'inflows':
                # Handle inflows list specially
                inflows_str = ', '.join([str(x) for x in value if x is not None])
                if not inflows_str:
                    inflows_str = "None"
                ttk.Label(row, text=inflows_str).pack(side="right", padx=5)
            else:
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for hydrology data
        hydrology_frame = ttk.LabelFrame(main_frame, text="Hydrology")
        hydrology_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in self.parameters['HRU']['reach']['hydrology']:
            if key != 'Manning':  # Handle Manning separately
                row = ttk.Frame(hydrology_frame)
                row.pack(fill="x", padx=5, pady=2)
                
                ttk.Label(row, text=format_key(key) + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                value = self.parameters['HRU']['reach']['hydrology'][key][idx]
                ttk.Label(row, text=str(value)).pack(side="right", padx=5)
        
        # Create a pane for Manning data
        manning_frame = ttk.LabelFrame(main_frame, text="Manning Parameters")
        manning_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        for key in self.parameters['HRU']['reach']['hydrology']['Manning']:
            row = ttk.Frame(manning_frame)
            row.pack(fill="x", padx=5, pady=2)
            
            ttk.Label(row, text=key + ":", font=("TkDefaultFont", 10)).pack(side="left", padx=5)
            value = self.parameters['HRU']['reach']['hydrology']['Manning'][key][idx]
            ttk.Label(row, text=str(value)).pack(side="right", padx=5)

def main():
    root = tk.Tk()
    app = PERSiSTViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
