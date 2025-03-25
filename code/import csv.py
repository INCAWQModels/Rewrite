import csv
from datetime import datetime, timedelta

# Function to read CSV into a dictionary
def read_csv_to_dict(input_filename):
    with open(input_filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

# Function to add a date column starting from a user-specified start date
def add_date_column(data, start_date):
    current_date = start_date
    for row in data:
        row['date'] = current_date.strftime('%Y-%m-%d')  # Add the date column
        current_date += timedelta(days=1)  # Increment the date by one day
    return data

# Function to write the dictionary back to CSV
def write_dict_to_csv(output_filename, data, fieldnames):
    with open(output_filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header
        writer.writerows(data)  # Write the data rows

# Main script
input_filename = 'input.csv'  # Replace with your input file
output_filename = 'output.csv'  # Replace with your desired output file

# Get user input for start date
start_date_input = input("Enter the start date (YYYY-MM-DD): ")
start_date = datetime.strptime(start_date_input, '%Y-%m-%d')

# Read data from CSV file
data = read_csv_to_dict(input_filename)

# Get fieldnames (columns) from the first row and add 'date' column
if data:
    fieldnames = data[0].keys()
    fieldnames = list(fieldnames) + ['date']

# Add the date column to the data
data_with_date = add_date_column(data, start_date)

# Write the updated data to a new CSV file
write_dict_to_csv(output_filename, data_with_date, fieldnames)

print(f"Data with incrementing date column has been written to {output_filename}")
