import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os

class JSONEditorApp:
    def __init__(self, root, json_data):
        self.root = root
        self.root.title("INCA Parameter Editor")
        self.root.geometry("1000x700")
        self.json_data = json_data
        
        self.root.wm_iconphoto(True,tk.PhotoImage(file="incaMan.png"))
        
        # Store all widget references for later retrieval
        self.entry_widgets = {}

        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top menu
        self.create_menu()
        
        # Create main notebook
        self.main_notebook = ttk.Notebook(main_frame)
        self.main_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for top-level objects
        self.create_general_tab()
        self.create_bucket_tab()
        self.create_landcover_tab()
        self.create_subcatchment_tab()
        self.create_reach_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save", command=self.save_json)
        file_menu.add_command(label="Save As...", command=self.save_json_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def show_about(self):
        messagebox.showinfo("About", "INCA Parameter Editor\nVersion 1.0")
    
    def create_general_tab(self):
        general_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(general_frame, text="General")
        
        general_data = self.json_data.get("general", {})
        
        # Create scrollable frame
        canvas = tk.Canvas(general_frame)
        scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add fields for general data
        row = 0
        for key, value in general_data.items():
            if key == "model":
                # Handle nested model object
                model_frame = ttk.LabelFrame(scrollable_frame, text="Model")
                model_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
                
                model_row = 0
                for model_key, model_value in general_data["model"].items():
                    ttk.Label(model_frame, text=f"{model_key}:").grid(row=model_row, column=0, padx=5, pady=2, sticky="w")
                    
                    entry = ttk.Entry(model_frame, width=50)
                    entry.grid(row=model_row, column=1, padx=5, pady=2, sticky="ew")
                    entry.insert(0, str(model_value))
                    
                    # Store widget reference
                    self.entry_widgets[f"general.model.{model_key}"] = entry
                    
                    model_row += 1
            else:
                ttk.Label(scrollable_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=2, sticky="w")
                
                entry = ttk.Entry(scrollable_frame, width=50)
                entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
                entry.insert(0, str(value))
                
                # Store widget reference
                self.entry_widgets[f"general.{key}"] = entry
            
            row += 1
    
    def create_bucket_tab(self):
        bucket_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(bucket_frame, text="Bucket")
        
        bucket_data = self.json_data.get("bucket", {})
        identifier_data = bucket_data.get("identifier", {})
        
        # Create notebook for bucket identifiers
        bucket_notebook = ttk.Notebook(bucket_frame)
        bucket_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Get bucket names and abbreviations
        bucket_names = identifier_data.get("name", [])
        bucket_abbrs = identifier_data.get("abbreviation", [])
        
        # Create a tab for each bucket
        for i, (name, abbr) in enumerate(zip(bucket_names, bucket_abbrs)):
            bucket_tab = ttk.Frame(bucket_notebook)
            bucket_notebook.add(bucket_tab, text=f"{name} ({abbr})")
            
            # Create a form for bucket properties
            form_frame = ttk.Frame(bucket_tab)
            form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ttk.Label(form_frame, text=f"Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            name_entry = ttk.Entry(form_frame, width=30)
            name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            name_entry.insert(0, name)
            self.entry_widgets[f"bucket.identifier.name[{i}]"] = name_entry
            
            ttk.Label(form_frame, text=f"Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            abbr_entry = ttk.Entry(form_frame, width=30)
            abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            abbr_entry.insert(0, abbr)
            self.entry_widgets[f"bucket.identifier.abbreviation[{i}]"] = abbr_entry
    
    def create_landcover_tab(self):
        landcover_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(landcover_frame, text="Land Cover")
        
        landcover_data = self.json_data.get("landCover", {})
        identifier_data = landcover_data.get("identifier", {})
        
        # Create notebook for landcover identifiers
        landcover_notebook = ttk.Notebook(landcover_frame)
        landcover_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Get landcover names and abbreviations
        landcover_names = identifier_data.get("name", [])
        landcover_abbrs = identifier_data.get("abbreviation", [])
        
        # Create a tab for each landcover type
        for i, (name, abbr) in enumerate(zip(landcover_names, landcover_abbrs)):
            landcover_tab = ttk.Frame(landcover_notebook)
            landcover_notebook.add(landcover_tab, text=f"{name} ({abbr})")
            
            # Create nested notebook for landcover properties
            properties_notebook = ttk.Notebook(landcover_tab)
            properties_notebook.pack(fill=tk.BOTH, expand=True)
            
            # Create tabs for each property category
            self.create_landcover_identifier_tab(properties_notebook, identifier_data, i)
            self.create_landcover_general_tab(properties_notebook, landcover_data.get("general", {}), i)
            self.create_landcover_precipitation_tab(properties_notebook, landcover_data.get("precipitation", {}), i)
            self.create_landcover_flowmatrix_tab(properties_notebook, landcover_data.get("flowMatrix", []), i)
    
    def create_landcover_identifier_tab(self, parent_notebook, identifier_data, index):
        identifier_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(identifier_frame, text="Identifier")
        
        form_frame = ttk.Frame(identifier_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name and abbreviation
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.insert(0, identifier_data.get("name", [])[index] if len(identifier_data.get("name", [])) > index else "")
        self.entry_widgets[f"landCover.identifier.name[{index}]"] = name_entry
        
        ttk.Label(form_frame, text="Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        abbr_entry = ttk.Entry(form_frame, width=30)
        abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        abbr_entry.insert(0, identifier_data.get("abbreviation", [])[index] if len(identifier_data.get("abbreviation", [])) > index else "")
        self.entry_widgets[f"landCover.identifier.abbreviation[{index}]"] = abbr_entry
    
    def create_landcover_general_tab(self, parent_notebook, general_data, index):
        general_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(general_frame, text="General")
        
        # Create notebook for general properties
        general_notebook = ttk.Notebook(general_frame)
        general_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each model
        self.create_soil_temperature_model_tab(general_notebook, general_data.get("soilTemperatureModel", {}), index)
        self.create_evapotranspiration_model_tab(general_notebook, general_data.get("evapotranspirationModel", {}), index)
    
    def create_soil_temperature_model_tab(self, parent_notebook, model_data, index):
        model_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(model_frame, text="Soil Temperature Model")
        
        form_frame = ttk.Frame(model_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add fields for soil temperature model parameters
        row = 0
        for key, values in model_data.items():
            ttk.Label(form_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            value = values[index] if len(values) > index else ""
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"landCover.general.soilTemperatureModel.{key}[{index}]"] = entry
            
            row += 1
    
    def create_evapotranspiration_model_tab(self, parent_notebook, model_data, index):
        model_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(model_frame, text="Evapotranspiration Model")
        
        form_frame = ttk.Frame(model_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add fields for evapotranspiration model parameters
        row = 0
        for key, values in model_data.items():
            ttk.Label(form_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            value = values[index] if len(values) > index else ""
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"landCover.general.evapotranspirationModel.{key}[{index}]"] = entry
            
            row += 1
    
    def create_landcover_precipitation_tab(self, parent_notebook, precipitation_data, index):
        precipitation_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(precipitation_frame, text="Precipitation")
        
        form_frame = ttk.Frame(precipitation_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add fields for precipitation parameters
        row = 0
        for key, values in precipitation_data.items():
            ttk.Label(form_frame, text=f"{key}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            value = values[index] if len(values) > index else ""
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"landCover.precipitation.{key}[{index}]"] = entry
            
            row += 1
    
    def create_landcover_flowmatrix_tab(self, parent_notebook, flow_matrix_data, index):
        flow_matrix_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(flow_matrix_frame, text="Flow Matrix")
        
        # Create scrollable frame
        canvas = tk.Canvas(flow_matrix_frame)
        scrollbar = ttk.Scrollbar(flow_matrix_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get the matrix for this landcover
        if len(flow_matrix_data) > index:
            matrix = flow_matrix_data[index]
            
            ttk.Label(scrollable_frame, text="Flow Matrix:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            # Create a grid of entries for the matrix
            for i, row_data in enumerate(matrix):
                for j, value in enumerate(row_data):
                    entry = ttk.Entry(scrollable_frame, width=8)
                    entry.grid(row=i+1, column=j+1, padx=2, pady=2)
                    entry.insert(0, str(value))
                    
                    self.entry_widgets[f"landCover.flowMatrix[{index}][{i}][{j}]"] = entry
                
                # Add row labels
                ttk.Label(scrollable_frame, text=f"Row {i+1}").grid(row=i+1, column=0, padx=5, pady=2, sticky="e")
            
            # Add column labels
            for j in range(len(matrix[0])):
                ttk.Label(scrollable_frame, text=f"Col {j+1}").grid(row=0, column=j+1, padx=2, pady=2)
    
    def create_subcatchment_tab(self):
        subcatchment_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(subcatchment_frame, text="Subcatchment")
        
        subcatchment_data = self.json_data.get("subcatchment", {})
        identifier_data = subcatchment_data.get("identifier", {})
        
        # Create notebook for subcatchment identifiers
        subcatchment_notebook = ttk.Notebook(subcatchment_frame)
        subcatchment_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Get subcatchment names and abbreviations
        subcatchment_names = identifier_data.get("name", [])
        subcatchment_abbrs = identifier_data.get("abbreviation", [])
        
        # Create a tab for each subcatchment
        for i, (name, abbr) in enumerate(zip(subcatchment_names, subcatchment_abbrs)):
            subcatchment_tab = ttk.Frame(subcatchment_notebook)
            subcatchment_notebook.add(subcatchment_tab, text=f"{name} ({abbr})")
            
            # Create nested notebook for subcatchment properties
            properties_notebook = ttk.Notebook(subcatchment_tab)
            properties_notebook.pack(fill=tk.BOTH, expand=True)
            
            # Create tabs for each property category
            self.create_subcatchment_identifier_tab(properties_notebook, identifier_data, i)
            self.create_subcatchment_general_tab(properties_notebook, subcatchment_data.get("general", {}), i)
            self.create_subcatchment_hydrology_tab(properties_notebook, subcatchment_data.get("hydrology", {}), i)
            
            # Add empty tabs for other categories
            self.create_empty_tab(properties_notebook, "Soil/Sediment")
            self.create_empty_tab(properties_notebook, "Chemistry")
            self.create_empty_tab(properties_notebook, "Random Stuff")
    
    def create_subcatchment_identifier_tab(self, parent_notebook, identifier_data, index):
        identifier_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(identifier_frame, text="Identifier")
        
        form_frame = ttk.Frame(identifier_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name and abbreviation
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.insert(0, identifier_data.get("name", [])[index] if len(identifier_data.get("name", [])) > index else "")
        self.entry_widgets[f"subcatchment.identifier.name[{index}]"] = name_entry
        
        ttk.Label(form_frame, text="Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        abbr_entry = ttk.Entry(form_frame, width=30)
        abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        abbr_entry.insert(0, identifier_data.get("abbreviation", [])[index] if len(identifier_data.get("abbreviation", [])) > index else "")
        self.entry_widgets[f"subcatchment.identifier.abbreviation[{index}]"] = abbr_entry
    
    def create_subcatchment_general_tab(self, parent_notebook, general_data, index):
        general_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(general_frame, text="General")
        
        form_frame = ttk.Frame(general_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Simple properties
        simple_props = ["area", "latitudeAtOutflow", "longitudeAtOutflow"]
        
        for i, prop in enumerate(simple_props):
            ttk.Label(form_frame, text=f"{prop}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            values = general_data.get(prop, [])
            value = values[index] if len(values) > index else ""
            
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"subcatchment.general.{prop}[{index}]"] = entry
        
        # Land cover percent (matrix)
        land_cover_frame = ttk.LabelFrame(form_frame, text="Land Cover Percent")
        land_cover_frame.grid(row=len(simple_props), column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        land_cover_percent = general_data.get("landCoverPercent", [])
        
        if len(land_cover_percent) > index:
            row_data = land_cover_percent[index]
            
            landcover_names = self.json_data.get("landCover", {}).get("identifier", {}).get("name", [])
            
            for i, value in enumerate(row_data):
                land_cover_label = landcover_names[i] if i < len(landcover_names) else f"Land Cover {i+1}"
                ttk.Label(land_cover_frame, text=f"{land_cover_label}:").grid(row=i, column=0, padx=5, pady=2, sticky="w")
                
                entry = ttk.Entry(land_cover_frame, width=10)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky="ew")
                entry.insert(0, str(value))
                
                self.entry_widgets[f"subcatchment.general.landCoverPercent[{index}][{i}]"] = entry
    
    def create_subcatchment_hydrology_tab(self, parent_notebook, hydrology_data, index):
        hydrology_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(hydrology_frame, text="Hydrology")
        
        form_frame = ttk.Frame(hydrology_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Hydrology properties
        props = ["rainfallMultiplier", "snowfallMultiplier", "snowfallTemperature", "snowmeltTemperature"]
        
        for i, prop in enumerate(props):
            ttk.Label(form_frame, text=f"{prop}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            values = hydrology_data.get(prop, [])
            value = values[index] if len(values) > index else ""
            
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"subcatchment.hydrology.{prop}[{index}]"] = entry
    
    def create_empty_tab(self, parent_notebook, tab_name):
        empty_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(empty_frame, text=tab_name)
        
        ttk.Label(empty_frame, text=f"No {tab_name} data available.").pack(padx=20, pady=20)
    
    def create_reach_tab(self):
        reach_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(reach_frame, text="Reach")
        
        reach_data = self.json_data.get("reach", {})
        identifier_data = reach_data.get("identifier", {})
        
        # Create notebook for reach identifiers
        reach_notebook = ttk.Notebook(reach_frame)
        reach_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Get reach names and abbreviations
        reach_names = identifier_data.get("name", [])
        reach_abbrs = identifier_data.get("abbreviation", [])
        
        # Create a tab for each reach
        for i, (name, abbr) in enumerate(zip(reach_names, reach_abbrs)):
            reach_tab = ttk.Frame(reach_notebook)
            reach_notebook.add(reach_tab, text=f"{name} ({abbr})")
            
            # Create nested notebook for reach properties
            properties_notebook = ttk.Notebook(reach_tab)
            properties_notebook.pack(fill=tk.BOTH, expand=True)
            
            # Create tabs for each property category
            self.create_reach_identifier_tab(properties_notebook, identifier_data, i)
            self.create_reach_general_tab(properties_notebook, reach_data.get("general", {}), i)
            self.create_reach_hydrology_tab(properties_notebook, reach_data.get("hydrology", {}), i)
            
            # Add empty tabs for other categories
            self.create_empty_tab(properties_notebook, "Soil/Sediment")
            self.create_empty_tab(properties_notebook, "Chemistry")
    
    def create_reach_identifier_tab(self, parent_notebook, identifier_data, index):
        identifier_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(identifier_frame, text="Identifier")
        
        form_frame = ttk.Frame(identifier_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name and abbreviation
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.insert(0, identifier_data.get("name", [])[index] if len(identifier_data.get("name", [])) > index else "")
        self.entry_widgets[f"reach.identifier.name[{index}]"] = name_entry
        
        ttk.Label(form_frame, text="Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        abbr_entry = ttk.Entry(form_frame, width=30)
        abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        abbr_entry.insert(0, identifier_data.get("abbreviation", [])[index] if len(identifier_data.get("abbreviation", [])) > index else "")
        self.entry_widgets[f"reach.identifier.abbreviation[{index}]"] = abbr_entry
    
    def create_reach_general_tab(self, parent_notebook, general_data, index):
        general_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(general_frame, text="General")
        
        form_frame = ttk.Frame(general_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Simple properties
        simple_props = ["length", "widthAtBottom", "slope"]
        
        for i, prop in enumerate(simple_props):
            ttk.Label(form_frame, text=f"{prop}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            values = general_data.get(prop, [])
            value = values[index] if len(values) > index else ""
            
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entry.insert(0, str(value))
            
            self.entry_widgets[f"reach.general.{prop}[{index}]"] = entry
        
        # Outflow and inflows
        row = len(simple_props)
        
        # Outflow
        ttk.Label(form_frame, text="Outflow:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        outflow_values = general_data.get("outflow", [])
        outflow_value = outflow_values[index] if len(outflow_values) > index else ""
        
        outflow_entry = ttk.Entry(form_frame, width=30)
        outflow_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        outflow_entry.insert(0, str(outflow_value) if outflow_value is not None else "None")
        
        self.entry_widgets[f"reach.general.outflow[{index}]"] = outflow_entry
        
        row += 1
        
        # Inflows
        ttk.Label(form_frame, text="Inflows:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        inflows_values = general_data.get("inflows", [])
        
        if len(inflows_values) > index:
            inflows = inflows_values[index]
            inflows_str = ", ".join(str(x) if x is not None else "None" for x in inflows)
            
            inflows_entry = ttk.Entry(form_frame, width=30)
            inflows_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            inflows_entry.insert(0, inflows_str)
            
            self.entry_widgets
            self.entry_widgets[f"reach.general.inflows[{index}]"] = inflows_entry
    
    def create_reach_hydrology_tab(self, parent_notebook, hydrology_data, index):
        hydrology_frame = ttk.Frame(parent_notebook)
        parent_notebook.add(hydrology_frame, text="Hydrology")
        
        # Create scrollable frame
        canvas = tk.Canvas(hydrology_frame)
        scrollbar = ttk.Scrollbar(hydrology_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Simple properties
        row = 0
        
        # Boolean properties
        bool_props = ["hasAbstraction", "hasEffluent"]
        for prop in bool_props:
            ttk.Label(scrollable_frame, text=f"{prop}:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
            
            values = hydrology_data.get(prop, [])
            value = values[index] if len(values) > index else False
            
            var = tk.BooleanVar(value=value)
            check = ttk.Checkbutton(scrollable_frame, variable=var)
            check.grid(row=row, column=1, padx=5, pady=5, sticky="w")
            
            self.entry_widgets[f"reach.hydrology.{prop}[{index}]"] = var
            
            row += 1
        
        # Manning parameters
        manning_data = hydrology_data.get("Manning", {})
        
        if manning_data:
            manning_frame = ttk.LabelFrame(scrollable_frame, text="Manning")
            manning_frame.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
            
            manning_row = 0
            for param, values in manning_data.items():
                ttk.Label(manning_frame, text=f"{param}:").grid(row=manning_row, column=0, padx=5, pady=2, sticky="w")
                
                value = values[index] if len(values) > index else ""
                
                entry = ttk.Entry(manning_frame, width=20)
                entry.grid(row=manning_row, column=1, padx=5, pady=2, sticky="ew")
                entry.insert(0, str(value))
                
                self.entry_widgets[f"reach.hydrology.Manning.{param}[{index}]"] = entry
                
                manning_row += 1
            
            row += 1
        
        # Initial flow
        ttk.Label(scrollable_frame, text="Initial Flow:").grid(row=row, column=0, padx=5, pady=5, sticky="w")
        
        initial_flow_values = hydrology_data.get("initialFlow", [])
        initial_flow_value = initial_flow_values[index] if len(initial_flow_values) > index else ""
        
        initial_flow_entry = ttk.Entry(scrollable_frame, width=30)
        initial_flow_entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        initial_flow_entry.insert(0, str(initial_flow_value))
        
        self.entry_widgets[f"reach.hydrology.initialFlow[{index}]"] = initial_flow_entry
    
    def collect_data(self):
        """Collect data from all entry widgets and update the JSON data structure"""
        updated_data = self.json_data.copy()
        
        # Process general section
        for key, widget in self.entry_widgets.items():
            if key.startswith("general."):
                parts = key.split(".")
                if len(parts) == 2:
                    # Simple case
                    updated_data["general"][parts[1]] = self._parse_value(widget.get())
                elif len(parts) == 3:
                    # Nested case (model)
                    if parts[1] not in updated_data["general"]:
                        updated_data["general"][parts[1]] = {}
                    updated_data["general"][parts[1]][parts[2]] = self._parse_value(widget.get())
        
        # Process bucket section
        for key, widget in self.entry_widgets.items():
            if key.startswith("bucket."):
                parts = key.split(".")
                if len(parts) == 3 and "[" in parts[2]:
                    # Array case
                    array_name, index_str = parts[2].split("[", 1)
                    index = int(index_str.split("]")[0])
                    
                    if parts[1] not in updated_data["bucket"]:
                        updated_data["bucket"][parts[1]] = {}
                    
                    if array_name not in updated_data["bucket"][parts[1]]:
                        updated_data["bucket"][parts[1]][array_name] = []
                    
                    # Ensure the array is large enough
                    while len(updated_data["bucket"][parts[1]][array_name]) <= index:
                        updated_data["bucket"][parts[1]][array_name].append("")
                    
                    updated_data["bucket"][parts[1]][array_name][index] = self._parse_value(widget.get())
        
        # Process landcover section
        for key, widget in self.entry_widgets.items():
            if key.startswith("landCover."):
                parts = key.split(".")
                
                if "[" in parts[-1]:
                    # Array case with simple path
                    array_part = parts[-1]
                    array_name, index_rest = array_part.split("[", 1)
                    indices = []
                    
                    # Extract all indices
                    for idx_part in index_rest.split("["):
                        idx = int(idx_part.split("]")[0])
                        indices.append(idx)
                    
                    # Navigate to the right location in the data structure
                    target = updated_data
                    for part in parts[:-1]:
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    # Ensure array exists
                    if array_name not in target:
                        target[array_name] = []
                    
                    # For complex nested arrays (like flowMatrix)
                    if len(indices) == 1:
                        # Simple array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append("")
                        
                        target[array_name][indices[0]] = self._parse_value(widget.get())
                    elif len(indices) == 2:
                        # 2D array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append([])
                        
                        while len(target[array_name][indices[0]]) <= indices[1]:
                            target[array_name][indices[0]].append("")
                        
                        target[array_name][indices[0]][indices[1]] = self._parse_value(widget.get())
                    elif len(indices) == 3:
                        # 3D array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append([])
                        
                        while len(target[array_name][indices[0]]) <= indices[1]:
                            target[array_name][indices[0]].append([])
                        
                        while len(target[array_name][indices[0]][indices[1]]) <= indices[2]:
                            target[array_name][indices[0]][indices[1]].append("")
                        
                        target[array_name][indices[0]][indices[1]][indices[2]] = self._parse_value(widget.get())
                else:
                    # Simple case (no arrays)
                    target = updated_data
                    for i, part in enumerate(parts[:-1]):
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    target[parts[-1]] = self._parse_value(widget.get())
        
        # Process subcatchment section
        for key, widget in self.entry_widgets.items():
            if key.startswith("subcatchment."):
                parts = key.split(".")
                
                if "[" in parts[-1]:
                    # Array case with simple path
                    array_part = parts[-1]
                    array_name, index_rest = array_part.split("[", 1)
                    indices = []
                    
                    # Extract all indices
                    for idx_part in index_rest.split("["):
                        idx = int(idx_part.split("]")[0])
                        indices.append(idx)
                    
                    # Navigate to the right location in the data structure
                    target = updated_data
                    for part in parts[:-1]:
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    # Ensure array exists
                    if array_name not in target:
                        target[array_name] = []
                    
                    # For complex nested arrays
                    if len(indices) == 1:
                        # Simple array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append("")
                        
                        target[array_name][indices[0]] = self._parse_value(widget.get())
                    elif len(indices) == 2:
                        # 2D array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append([])
                        
                        while len(target[array_name][indices[0]]) <= indices[1]:
                            target[array_name][indices[0]].append("")
                        
                        target[array_name][indices[0]][indices[1]] = self._parse_value(widget.get())
                else:
                    # Simple case (no arrays)
                    target = updated_data
                    for i, part in enumerate(parts[:-1]):
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    target[parts[-1]] = self._parse_value(widget.get())
        
        # Process reach section
        for key, widget in self.entry_widgets.items():
            if key.startswith("reach."):
                parts = key.split(".")
                
                if "[" in parts[-1]:
                    # Array case with simple path
                    array_part = parts[-1]
                    array_name, index_rest = array_part.split("[", 1)
                    indices = []
                    
                    # Extract all indices
                    for idx_part in index_rest.split("["):
                        idx = int(idx_part.split("]")[0])
                        indices.append(idx)
                    
                    # Navigate to the right location in the data structure
                    target = updated_data
                    for part in parts[:-1]:
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    # Ensure array exists
                    if array_name not in target:
                        target[array_name] = []
                    
                    # Handle special case for boolean values
                    value = None
                    if isinstance(widget, tk.BooleanVar):
                        value = widget.get()
                    else:
                        value = self._parse_value(widget.get())
                    
                    # For complex nested arrays
                    if len(indices) == 1:
                        # Simple array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append("")
                        
                        # Special case for inflows
                        if array_name == "inflows":
                            # Parse comma-separated list of values
                            inflows_str = widget.get()
                            inflows = []
                            for item in inflows_str.split(","):
                                item = item.strip()
                                if item.lower() == "none":
                                    inflows.append(None)
                                else:
                                    inflows.append(self._parse_value(item))
                            target[array_name][indices[0]] = inflows
                        # Special case for outflow that can be null
                        elif array_name == "outflow" and value == "None":
                            target[array_name][indices[0]] = None
                        else:
                            target[array_name][indices[0]] = value
                    elif len(indices) == 2:
                        # 2D array
                        while len(target[array_name]) <= indices[0]:
                            target[array_name].append([])
                        
                        while len(target[array_name][indices[0]]) <= indices[1]:
                            target[array_name][indices[0]].append("")
                        
                        target[array_name][indices[0]][indices[1]] = value
                else:
                    # Simple case (no arrays)
                    target = updated_data
                    for i, part in enumerate(parts[:-1]):
                        if part not in target:
                            target[part] = {}
                        target = target[part]
                    
                    target[parts[-1]] = self._parse_value(widget.get())
        
        return updated_data
    
    def _parse_value(self, value_str):
        """Parse a string value to the appropriate type"""
        if value_str.lower() == "true":
            return True
        elif value_str.lower() == "false":
            return False
        elif value_str.lower() == "null" or value_str.lower() == "none":
            return None
        else:
            try:
                # Try to convert to int
                return int(value_str)
            except ValueError:
                try:
                    # Try to convert to float
                    return float(value_str)
                except ValueError:
                    # Keep as string
                    return value_str
    
    def save_json(self):
        """Save the updated JSON data back to the original file"""
        updated_data = self.collect_data()
        
        try:
            with open("forClaude.json", "w") as f:
                json.dump(updated_data, f, indent=4)
            
            self.status_var.set("File saved successfully!")
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            self.status_var.set(f"Error saving file: {str(e)}")
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_json_as(self):
        """Save the updated JSON data to a new file"""
        updated_data = self.collect_data()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(updated_data, f, indent=4)
                
                self.status_var.set(f"File saved successfully to {file_path}!")
                messagebox.showinfo("Success", f"File saved successfully to {file_path}!")
            except Exception as e:
                self.status_var.set(f"Error saving file: {str(e)}")
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")


def main():
    # Load JSON data
    try:
        with open("forClaude.json", "r") as f:
            json_data = json.load(f)
    except FileNotFoundError:
        messagebox.showerror("Error", "File 'forClaude.json' not found.")
        return
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Invalid JSON format in 'forClaude.json'.")
        return
    except Exception as e:
        messagebox.showerror("Error", f"Error loading file: {str(e)}")
        return
    
    # Create and run the application
    root = tk.Tk()
    app = JSONEditorApp(root, json_data)
    root.mainloop()


if __name__ == "__main__":
    main()