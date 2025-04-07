import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os

class create_new_parameter_set:
    def __init__(self, root):
        self.root = root
        self.root.title("New parameter set properties")
        self.root.geometry("800x500")
        
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
    
    def get_all_items(self):
        """Get all items from all listboxes as a dictionary"""
        items = {}
        for list_name, listbox in self.listboxes.items():
            items[list_name] = []
            for i in range(listbox.size()):
                display_text = listbox.get(i)
                name, abbreviation = self.parse_display_text(display_text)
                items[list_name].append({
                    "name": name,
                    "abbreviation": abbreviation
                })
        return items
    
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
                
            # Populate listboxes with data
            for list_name in self.listboxes:
                if list_name in data and isinstance(data[list_name], list):
                    for item in data[list_name]:
                        if isinstance(item, dict) and "name" in item and "abbreviation" in item:
                            display_text = self.format_display_text(item["name"], item["abbreviation"])
                            self.listboxes[list_name].insert(tk.END, display_text)
                        elif isinstance(item, str):
                            # Try to handle old format or plain strings
                            self.listboxes[list_name].insert(tk.END, self.format_display_text(item, ""))
            
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
        """Save all listbox items to a single JSON file"""
        all_items = self.get_all_items()
        
        # Check if there are items in any of the lists
        if not any(all_items.values()):
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