import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
from generateJSONparameterFile import generate_json_files

class JSONGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Parameter File Generator")
        self.root.geometry("600x500")
        
        # Variables
        self.identifiers_path = tk.StringVar()
        self.schema_precursor_path = tk.StringVar()
        self.output_schema_path = tk.StringVar(value="generated_schema.json")
        self.output_data_path = tk.StringVar(value="generated_data.json")
        
        # Create the UI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input Files Section
        file_frame = ttk.LabelFrame(main_frame, text="Input Files", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        # Identifiers file
        ttk.Label(file_frame, text="Identifiers JSON:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.identifiers_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_identifiers).grid(row=0, column=2, padx=5, pady=5)
        
        # Schema precursor file
        ttk.Label(file_frame, text="Schema Precursor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.schema_precursor_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_schema_precursor).grid(row=1, column=2, padx=5, pady=5)
        
        # Output Files Section
        output_frame = ttk.LabelFrame(main_frame, text="Output Files", padding="10")
        output_frame.pack(fill=tk.X, pady=5)
        
        # Output schema file
        ttk.Label(output_frame, text="Output Schema:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_schema_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_schema).grid(row=0, column=2, padx=5, pady=5)
        
        # Output data file
        ttk.Label(output_frame, text="Output Data:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_data_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_data).grid(row=1, column=2, padx=5, pady=5)
        
        # Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Preview text area with scrollbar
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=10)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Load Preview", command=self.load_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Files", command=self.generate_files).pack(side=tk.RIGHT, padx=5)
        
    def browse_identifiers(self):
        filename = filedialog.askopenfilename(
            title="Select Identifiers JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.identifiers_path.set(filename)
            
    def browse_schema_precursor(self):
        filename = filedialog.askopenfilename(
            title="Select Schema Precursor File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.schema_precursor_path.set(filename)
            
    def browse_output_schema(self):
        filename = filedialog.asksaveasfilename(
            title="Save Schema Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_schema_path.set(filename)
            
    def browse_output_data(self):
        filename = filedialog.asksaveasfilename(
            title="Save Data Output File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_data_path.set(filename)
    
    def load_preview(self):
        """Load and preview identifiers file"""
        identifiers_path = self.identifiers_path.get()
        if not identifiers_path:
            messagebox.showerror("Error", "Please select an identifiers file.")
            return
            
        try:
            with open(identifiers_path, 'r') as f:
                identifiers = json.load(f)
                
            # Calculate counts
            counts = {
                "landcover_count": len(identifiers.get("landCover", {}).get("identifier", {}).get("name", [])),
                "bucket_count": len(identifiers.get("bucket", {}).get("identifier", {}).get("name", [])),
                "subcatchment_count": len(identifiers.get("subcatchment", {}).get("identifier", {}).get("name", [])),
                "reach_count": len(identifiers.get("reach", {}).get("identifier", {}).get("name", []))
            }
            
            # Clear preview text
            self.preview_text.delete(1.0, tk.END)
            
            # Add identifiers overview
            self.preview_text.insert(tk.END, "Identifiers Overview:\n\n")
            
            for category, count in counts.items():
                self.preview_text.insert(tk.END, f"{category.replace('_', ' ').title()}: {count}\n")
                
            # Show some identifiers
            self.preview_text.insert(tk.END, "\nLand Cover Names:\n")
            for name in identifiers.get("landCover", {}).get("identifier", {}).get("name", [])[:5]:
                self.preview_text.insert(tk.END, f"- {name}\n")
            if counts["landcover_count"] > 5:
                self.preview_text.insert(tk.END, f"... and {counts['landcover_count'] - 5} more\n")
                
            self.preview_text.insert(tk.END, "\nBucket Names:\n")
            for name in identifiers.get("bucket", {}).get("identifier", {}).get("name", [])[:5]:
                self.preview_text.insert(tk.END, f"- {name}\n")
            if counts["bucket_count"] > 5:
                self.preview_text.insert(tk.END, f"... and {counts['bucket_count'] - 5} more\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load identifiers file: {str(e)}")
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error: {str(e)}")
            
    def generate_files(self):
        """Generate JSON files using the module"""
        identifiers_path = self.identifiers_path.get()
        schema_precursor_path = self.schema_precursor_path.get()
        output_schema_path = self.output_schema_path.get()
        output_data_path = self.output_data_path.get()
        
        # Validate inputs
        if not identifiers_path or not schema_precursor_path:
            messagebox.showerror("Error", "Please select both identifiers and schema precursor files.")
            return
            
        if not os.path.exists(identifiers_path) or not os.path.exists(schema_precursor_path):
            messagebox.showerror("Error", "One or more input files do not exist.")
            return
            
        try:
            # Update preview with progress
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Generating files...\n")
            self.root.update()
            
            # Generate files
            schema_path, data_path = generate_json_files(
                identifiers_path,
                schema_precursor_path,
                output_schema_path,
                output_data_path
            )
            
            # Update preview with success message
            self.preview_text.insert(tk.END, f"Schema generated and saved to: {schema_path}\n")
            self.preview_text.insert(tk.END, f"Data generated and saved to: {data_path}\n")
            
            messagebox.showinfo("Success", "JSON files generated successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate files: {str(e)}")
            self.preview_text.insert(tk.END, f"Error: {str(e)}")

def main():
    root = tk.Tk()
    root.wm_iconphoto(True,tk.PhotoImage(file="incaMan.png"))
    app = JSONGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()