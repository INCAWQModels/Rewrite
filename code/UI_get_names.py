import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class create_new_parameter_set:
    def __init__(self, root):
        self.root = root
        self.root.title("New parameter set properties")
        self.root.geometry("800x500")
        
        # Create mapping between UI tab names and JSON keys
        self.tab_to_json_key = {
            "Buckets": "bucket",
            "Land Cover Types": "landCover",
            "Reaches": "reach",
            "Subcatchments": "subcatchment"
        }
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create button frame at the top
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add load and save buttons
        self.load_button = tk.Button(
            button_frame,
            text="Load from JSON",
            command=self.load_from_json,
            font=("Arial", 12, "bold")
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = tk.Button(
            button_frame,
            text="Save All Lists to JSON",
            command=self.save_to_json,
            font=("Arial", 12, "bold")
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Add generate parameter set button
        self.generate_button = tk.Button(
            button_frame,
            text="Generate Parameter Set",
            command=self.generate_parameter_set,
            font=("Arial", 12, "bold")
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Ready",
            font=("Arial", 10),
            anchor="e"
        )
        self.status_label.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for each listbox
        self.tabs = {}
        self.listboxes = {}
        self.scrollbars = {}
        
        for tab_name in ["Buckets", "Land Cover Types", "Reaches", "Subcatchments"]:
            # Create tab
            tab = ttk.Frame(self.notebook)
            self.tabs[tab_name] = tab
            self.notebook.add(tab, text=f"{tab_name}")
            
            # Create listbox with scrollbar in each tab
            listbox_frame = tk.Frame(tab)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Add column headers
            headers_frame = tk.Frame(listbox_frame)
            headers_frame.pack(fill=tk.X)
            
            name_header = tk.Label(headers_frame, text="Name", font=("Arial", 12, "bold"), width=30, anchor='w')
            name_header.pack(side=tk.LEFT, padx=(5, 0))
            
            abbr_header = tk.Label(headers_frame, text="Abbreviation", font=("Arial", 12, "bold"), anchor='w')
            abbr_header.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            # Create scrollbar
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Create listbox
            listbox = tk.Listbox(
                listbox_frame, 
                selectmode=tk.SINGLE,
                yscrollcommand=scrollbar.set,
                font=("Arial", 12)
            )
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            self.listboxes[tab_name] = listbox
            self.scrollbars[tab_name] = scrollbar
            
            # Buttons for this tab
            buttons_frame = tk.Frame(tab)
            buttons_frame.pack(fill=tk.X, pady=10)
            
            # Add buttons
            add_button = tk.Button(
                buttons_frame, 
                text=f"Add to List {tab_name}",
                command=lambda t=tab_name: self.add_item(t)
            )
            add_button.pack(side=tk.LEFT, padx=5)
            
            edit_button = tk.Button(
                buttons_frame, 
                text="Edit Item",
                command=lambda t=tab_name: self.edit_item(t)
            )
            edit_button.pack(side=tk.LEFT, padx=5)
            
            delete_button = tk.Button(
                buttons_frame, 
                text="Delete Item",
                command=lambda t=tab_name: self.delete_item(t)
            )
            delete_button.pack(side=tk.LEFT, padx=5)
            
            clear_button = tk.Button(
                buttons_frame, 
                text="Clear List",
                command=lambda t=tab_name: self.clear_list(t)
            )
            clear_button.pack(side=tk.LEFT, padx=5)
        
        # Track the currently loaded file
        self.current_file = None
    
    def update_status(self, message):
        """Update the status label with a message"""
        self.status_label.config(text=message)
    
    def format_display_text(self, name, abbreviation):
        """Format the name and abbreviation for display in the listbox"""
        # Format with fixed width for name column
        return f"{name:<30} | {abbreviation}"
    
    def parse_display_text(self, display_text):
        """Parse the display text back into name and abbreviation"""
        parts = display_text.split(" | ")
        if len(parts) == 2:
            name = parts[0].strip()
            abbreviation = parts[1].strip()
            return name, abbreviation
        return display_text, ""  # fallback
    
    def generate_parameter_set(self):
        """Generate parameter set based on the current lists"""
        # Check if there are items in all lists
        has_items = True
        empty_lists = []
        
        for list_name in self.listboxes:
            if self.listboxes[list_name].size() == 0:
                has_items = False
                empty_lists.append(list_name)
        
        if not has_items:
            messagebox.showwarning(
                "Empty Lists", 
                f"The following lists are empty: {', '.join(empty_lists)}.\n"
                "Please ensure all lists have at least one item."
            )
            return
        
        # Create a dialog to confirm generating the parameter set
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Parameter Set")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Add a label explaining what will happen
        tk.Label(
            dialog,
            text="This will generate a parameter set using all the items\n"
                 "currently in your lists. Do you want to proceed?",
            font=("Arial", 12),
            pady=20
        ).pack()
        
        # Add an entry field for optional parameter set name
        name_frame = tk.Frame(dialog)
        name_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            name_frame,
            text="Parameter Set Name (optional):",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)
        
        name_var = tk.StringVar()
        name_entry = tk.Entry(name_frame, textvariable=name_var, width=25)
        name_entry.pack(side=tk.LEFT, padx=5)
        
        # Add buttons
        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=20)
        
        def on_confirm():
            param_name = name_var.get().strip()
            if not param_name:
                param_name = "Default Parameter Set"
                
            # Get the current items
            all_items = self.get_all_items_for_json()
            
            # Here you would implement the actual parameter set generation
            # For now, just show a confirmation message
            dialog.destroy()
            messagebox.showinfo(
                "Parameter Set Generated",
                f"Parameter Set '{param_name}' has been generated.\n"
                f"Items included: {sum([len(cat['identifier']['name']) for cat in all_items.values()])} total items."
            )
            self.update_status(f"Parameter set '{param_name}' generated")
            
        def on_cancel():
            dialog.destroy()
        
        tk.Button(
            buttons_frame,
            text="Generate",
            command=on_confirm,
            font=("Arial", 11, "bold"),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            buttons_frame,
            text="Cancel",
            command=on_cancel,
            font=("Arial", 11),
            width=10
        ).pack(side=tk.LEFT, padx=10)
        
    def add_item(self, list_name):
        """Add a new item with name and abbreviation to the specified listbox"""
        # Create a custom dialog for two fields
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add Item to List {list_name}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Set to be on top of the main window
        dialog.grab_set()  # Modal
        
        # Name field
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_var = tk.StringVar()
        name_entry = tk.Entry(dialog, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.focus_set()
        
        # Abbreviation field
        tk.Label(dialog, text="Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        abbr_var = tk.StringVar()
        abbr_entry = tk.Entry(dialog, textvariable=abbr_var, width=10)
        abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Variables to store result
        result = {"confirmed": False, "name": "", "abbreviation": ""}
        
        def on_ok():
            result["confirmed"] = True
            result["name"] = name_var.get().strip()
            result["abbreviation"] = abbr_var.get().strip()
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        buttons_frame = tk.Frame(dialog)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        self.root.wait_window(dialog)
        
        # Process the result
        if result["confirmed"] and result["name"]:
            display_text = self.format_display_text(result["name"], result["abbreviation"])
            self.listboxes[list_name].insert(tk.END, display_text)
            self.update_status(f"Added item to List {list_name}")
    
    def edit_item(self, list_name):
        """Edit the selected item in the specified listbox"""
        listbox = self.listboxes[list_name]
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", f"Please select an item in {list_name} to edit")
            return
        
        current_item = listbox.get(selected_index)
        current_name, current_abbr = self.parse_display_text(current_item)
        
        # Create a custom dialog for two fields
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Item in List {list_name}")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Set to be on top of the main window
        dialog.grab_set()  # Modal
        
        # Name field
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_var = tk.StringVar(value=current_name)
        name_entry = tk.Entry(dialog, textvariable=name_var, width=25)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        name_entry.focus_set()
        
        # Abbreviation field
        tk.Label(dialog, text="Abbreviation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        abbr_var = tk.StringVar(value=current_abbr)
        abbr_entry = tk.Entry(dialog, textvariable=abbr_var, width=10)
        abbr_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Variables to store result
        result = {"confirmed": False, "name": "", "abbreviation": ""}
        
        def on_ok():
            result["confirmed"] = True
            result["name"] = name_var.get().strip()
            result["abbreviation"] = abbr_var.get().strip()
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        buttons_frame = tk.Frame(dialog)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(buttons_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Make dialog modal
        self.root.wait_window(dialog)
        
        # Process the result
        if result["confirmed"] and result["name"]:
            listbox.delete(selected_index)
            display_text = self.format_display_text(result["name"], result["abbreviation"])
            listbox.insert(selected_index, display_text)
            self.update_status(f"Edited item in {list_name}")
    
    def delete_item(self, list_name):
        """Delete the selected item from the specified listbox"""
        listbox = self.listboxes[list_name]
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", f"Please select an item in {list_name} to delete")
            return
        
        listbox.delete(selected_index)
        self.update_status(f"Deleted item from List {list_name}")
    
    def clear_list(self, list_name):
        """Clear all items from the specified listbox"""
        if messagebox.askyesno("Confirm Clear", f"Are you sure you want to clear all {list_name}?"):
            self.listboxes[list_name].delete(0, tk.END)
            self.update_status(f"Cleared all items from List {list_name}")
    
    def get_all_items_for_json(self):
        """Get all items from all listboxes in the format matching inputMockUps.json"""
        output_data = {}
        
        for list_name, json_key in self.tab_to_json_key.items():
            listbox = self.listboxes[list_name]
            
            # Initialize the structure for this category
            output_data[json_key] = {
                "identifier": {
                    "name": [],
                    "abbreviation": []
                }
            }
            
            # Fill in the names and abbreviations
            for i in range(listbox.size()):
                display_text = listbox.get(i)
                name, abbreviation = self.parse_display_text(display_text)
                output_data[json_key]["identifier"]["name"].append(name)
                output_data[json_key]["identifier"]["abbreviation"].append(abbreviation)
                
        return output_data
    
    def load_from_json(self):
        """Load data from a JSON file into the listboxes"""
        # Ask the user to select a file
        file_path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
            # Validate the data structure
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON format: Expected a dictionary")
                
            # Clear existing data
            for list_name in self.listboxes:
                self.listboxes[list_name].delete(0, tk.END)
                
            # Populate listboxes with data using the expected structure
            for list_name, json_key in self.tab_to_json_key.items():
                if json_key in data and "identifier" in data[json_key]:
                    names = data[json_key]["identifier"].get("name", [])
                    abbreviations = data[json_key]["identifier"].get("abbreviation", [])
                    
                    # Make sure we have matching lengths
                    for i in range(min(len(names), len(abbreviations))):
                        display_text = self.format_display_text(names[i], abbreviations[i])
                        self.listboxes[list_name].insert(tk.END, display_text)
            
            # Store the current file path
            self.current_file = file_path
            self.update_status(f"Loaded data from {os.path.basename(file_path)}")
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file format")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def save_to_json(self):
        """Save all listbox items to a single JSON file with the correct structure"""
        all_items = self.get_all_items_for_json()
        
        # Check if there are items in any of the lists
        has_items = False
        for category in all_items.values():
            if category["identifier"]["name"]:
                has_items = True
                break
        
        if not has_items:
            messagebox.showwarning("Warning", "No items to save")
            return
        
        # If we have a current file, offer to save to it by default
        if self.current_file:
            save_to_current = messagebox.askyesno(
                "Save File", 
                f"Save to current file ({os.path.basename(self.current_file)})?\nClick 'No' to save to a new file."
            )
            if save_to_current:
                filename = self.current_file
            else:
                filename = self.get_save_filename()
                if not filename:
                    return
        else:
            filename = self.get_save_filename()
            if not filename:
                return
            
        try:
            with open(filename, 'w') as file:
                json.dump(all_items, file, indent=4)
                
            self.current_file = filename
            self.update_status(f"All lists saved to {os.path.basename(filename)}")
            messagebox.showinfo("Success", f"All lists saved to {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def get_save_filename(self):
        """Get a filename for saving with a file dialog"""
        filename = filedialog.asksaveasfilename(
            title="Save JSON File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        return filename


def main():
    root = tk.Tk()
    app = create_new_parameter_set(root)
    root.mainloop()

if __name__ == "__main__":
    main()