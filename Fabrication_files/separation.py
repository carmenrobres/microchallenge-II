import csv
from datetime import datetime, timedelta

# Function to parse date string to datetime object
def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

# Function to calculate time difference in minutes
def time_diff_minutes(start_time, end_time):
    return (end_time - start_time).total_seconds() / 60

# Function to split data into separate CSV files based on time gaps
def split_data_by_time_gaps(input_file):
    with open(input_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header

        # Initialize variables
        current_start_time = None
        previous_end_time = None
        current_data = []

        for row in reader:
            timestamp = parse_date(row[0])

            if current_start_time is None:
                current_start_time = timestamp

            if previous_end_time is not None and time_diff_minutes(previous_end_time, timestamp) > 60:
                # If time gap is more than 60 minutes, create a new CSV file
                output_file_name = f"data_{current_start_time.strftime('%Y%m%d%H%M%S')}_{previous_end_time.strftime('%Y%m%d%H%M%S')}.csv"
                write_data_to_csv(current_data, header, output_file_name)
                current_start_time = timestamp
                current_data = []

            current_data.append(row)
            previous_end_time = timestamp

        # Write the last set of data to a CSV file
        if current_data:
            output_file_name = f"data_{current_start_time.strftime('%Y%m%d%H%M%S')}_{previous_end_time.strftime('%Y%m%d%H%M%S')}.csv"
            write_data_to_csv(current_data, header, output_file_name)

# Function to write data to a CSV file
def write_data_to_csv(data, header, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

# Main function
if __name__ == "__main__":
    input_file = 'log.csv'
    split_data_by_time_gaps(input_file)