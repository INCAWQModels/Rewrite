import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
from dat_to_csv_processor import convert_dat_to_csv

class DatToCSVConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(".DAT to CSV Converter")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        
        # Create a main frame with padding
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a style
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TEntry", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # Add a header
        header = ttk.Label(self.main_frame, text=".DAT to CSV Converter", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Initialize variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.start_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.date_format = tk.StringVar(value="%Y-%m-%d %H:%M:%S")
        self.time_increment = tk.StringVar(value="3600")  # Default: 1 hour in seconds
        self.column_names = tk.StringVar()
        
        # Create form elements
        self.create_file_inputs()
        self.create_date_inputs()
        self.create_column_inputs()
        self.create_buttons()
        
        # Status message
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=600)
        status_label.grid(row=8, column=0, columnspan=3, pady=(15, 0), sticky="w")

    def create_file_inputs(self):
        # Input File
        row = 1
        ttk.Label(self.main_frame, text="Input File:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.input_file, width=50).grid(row=row, column=1, sticky="we", padx=5)
        ttk.Button(self.main_frame, text="Browse...", command=self.browse_input_file).grid(row=row, column=2, sticky="w")
        
        # Output File
        row += 1
        ttk.Label(self.main_frame, text="Output File:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.output_file, width=50).grid(row=row, column=1, sticky="we", padx=5)
        ttk.Button(self.main_frame, text="Browse...", command=self.browse_output_file).grid(row=row, column=2, sticky="w")

    def create_date_inputs(self):
        # Start Date
        row = 3
        ttk.Label(self.main_frame, text="Start Date:").grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.start_date, width=50).grid(row=row, column=1, sticky="we", padx=5)
        ttk.Button(self.main_frame, text="Now", command=self.set_current_date).grid(row=row, column=2, sticky="w")
        
        # Date Format
        row += 1
        ttk.Label(self.main_frame, text="Date Format:").grid(row=row, column=0, sticky="w", pady=5)
        
        # Create a combobox with common date formats
        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y"
        ]
        self.date_format_combo = ttk.Combobox(self.main_frame, textvariable=self.date_format, values=date_formats, width=48)
        self.date_format_combo.grid(row=row, column=1, sticky="we", padx=5)
        ttk.Label(self.main_frame, text="Format Info:", font=("Arial", 8)).grid(row=row, column=2, sticky="w")
        
        # Date Format Help
        row += 1
        format_help = "Format codes: %Y=year, %m=month, %d=day, %H=hour, %M=minute, %S=second"
        ttk.Label(self.main_frame, text=format_help, font=("Arial", 8)).grid(row=row, column=1, columnspan=2, sticky="w", padx=5)
            
        # Time Increment
        row += 1
        ttk.Label(self.main_frame, text="Time Increment (sec):").grid(row=row, column=0, sticky="w", pady=5)
        
        time_frame = ttk.Frame(self.main_frame)
        time_frame.grid(row=row, column=1, sticky="we", padx=5)
        
        ttk.Entry(time_frame, textvariable=self.time_increment, width=20).pack(side=tk.LEFT, padx=(0, 5))
        
        # Add convenient preset buttons
        ttk.Button(time_frame, text="1 min", command=lambda: self.time_increment.set("60")).pack(side=tk.LEFT, padx=2)
        ttk.Button(time_frame, text="1 hour", command=lambda: self.time_increment.set("3600")).pack(side=tk.LEFT, padx=2)
        ttk.Button(time_frame, text="1 day", command=lambda: self.time_increment.set("86400")).pack(side=tk.LEFT, padx=2)

    def create_column_inputs(self):
        # Column Names
        row = 7
        ttk.Label(self.main_frame, text="Column Names:").grid(row=row, column=0, sticky="nw", pady=5)
        
        column_frame = ttk.Frame(self.main_frame)
        column_frame.grid(row=row, column=1, columnspan=2, sticky="we", padx=5)
        
        self.column_text = tk.Text(column_frame, height=5, width=60, wrap=tk.WORD)
        self.column_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(column_frame, orient="vertical", command=self.column_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.column_text.config(yscrollcommand=scrollbar.set)
        
        # Column name help text
        row += 1
        help_text = "Enter column names separated by commas (e.g., Rain,Flow,Temperature)"
        ttk.Label(self.main_frame, text=help_text, font=("Arial", 8)).grid(row=row, column=1, columnspan=2, sticky="w", padx=5, pady=(0, 10))

    def create_buttons(self):
        # Buttons frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        # Run button
        run_button = ttk.Button(button_frame, text="Convert", command=self.run_conversion, width=15)
        run_button.pack(side=tk.LEFT, padx=10)
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear Fields", command=self.clear_fields, width=15)
        clear_button.pack(side=tk.LEFT, padx=10)
        
        # Quit button
        quit_button = ttk.Button(button_frame, text="Quit", command=self.root.destroy, width=15)
        quit_button.pack(side=tk.LEFT, padx=10)

    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Select DAT file",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Suggest an output filename
            base = os.path.splitext(filename)[0]
            self.output_file.set(f"{base}.csv")

    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)

    def set_current_date(self):
        self.start_date.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def clear_fields(self):
        self.input_file.set("")
        self.output_file.set("")
        self.start_date.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.date_format.set("%Y-%m-%d %H:%M:%S")
        self.time_increment.set("3600")
        self.column_text.delete("1.0", tk.END)
        self.status_var.set("")

    def validate_inputs(self):
        # Check if files are specified
        if not self.input_file.get():
            messagebox.showerror("Error", "Please specify an input file.")
            return False
        
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return False
        
        # Check if input file exists
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", f"Input file not found: {self.input_file.get()}")
            return False
        
        # Validate date format and start date
        try:
            datetime.strptime(self.start_date.get(), self.date_format.get())
        except ValueError:
            messagebox.showerror("Error", f"Invalid date or format.\nDate: {self.start_date.get()}\nFormat: {self.date_format.get()}")
            return False
        
        # Validate time increment
        try:
            increment = int(self.time_increment.get())
            if increment <= 0:
                raise ValueError("Time increment must be positive")
        except ValueError:
            messagebox.showerror("Error", "Time increment must be a positive integer.")
            return False
        
        return True

    def run_conversion(self):
        # Get column names from text widget
        column_names = self.column_text.get("1.0", tk.END).strip()
        
        if not self.validate_inputs():
            return
        
        try:
            # Call the conversion function from the processor module
            convert_dat_to_csv(
                self.input_file.get(),
                self.output_file.get(),
                self.start_date.get(),
                self.date_format.get(),
                self.time_increment.get(),
                column_names
            )
            
            self.status_var.set(f"Conversion completed successfully! Output saved to {self.output_file.get()}")
            messagebox.showinfo("Success", f"File converted successfully!\nOutput saved to: {self.output_file.get()}")
            
        except Exception as e:
            error_message = f"Error during conversion: {str(e)}"
            self.status_var.set(error_message)
            messagebox.showerror("Conversion Error", error_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = DatToCSVConverterGUI(root)
    root.wm_iconphoto(True,tk.PhotoImage(file="incaMan.png"))
    root.mainloop()