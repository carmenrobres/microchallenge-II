import argparse
import csv
from datetime import datetime, timedelta
from PIL import Image, ImageDraw


# THIS SCRIPT TAKES THE .CSV FILE AS AN ARGUMENT COMMAND. THIS MEANS THAT TO USE THE LANGUAGE SCRIPT WITH A CSV WE HAVE TO TYPE THAT ON THE RASPBERRY PI TERMINAL:
# python language.py ("csv_file")   // Replace csv_file with your csv file.
# python language.py data_20240307105352_20240307105543.csv 


# Define constants
CANVAS_WIDTH = 210  # in mm
CANVAS_HEIGHT = 290  # in mm
LINE_THICKNESS_FACTOR = 4  # Adjust the line thickness factor for visibility and thickness
CIRCLE_RADIUS_FACTOR = 2  # Adjust the circle radius factor for visibility
SQUARE_SIZE_FACTOR = 1  # Adjust the square size factor for the area where elements are drawn
CIRCLE_Y_RANGE = (0.25, 0.75)  # Range for y position of circles (relative to canvas height)

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

def main(csv_filename):
    # Read CSV file and populate messages list
    messages = []

    with open(csv_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            timestamp_str, sender, message = row
            timestamp = parse_date(timestamp_str)
            messages.append((timestamp, sender, message))

    # Sort messages by timestamp
    messages.sort(key=lambda x: x[0])

    # Calculate time elapsed
    start_time = messages[0][0]
    end_time = messages[-1][0]
    time_elapsed = end_time - start_time

    # Convert mm to pixels
    CANVAS_WIDTH_PX = int(CANVAS_WIDTH * 3.779528)  # 1 mm = 3.779528 pixels
    CANVAS_HEIGHT_PX = int(CANVAS_HEIGHT * 3.779528)  # 1 mm = 3.779528 pixels

    # Calculate square size
    square_size = min(CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX) * SQUARE_SIZE_FACTOR

    # Calculate square position
    square_x = (CANVAS_WIDTH_PX - square_size) / 2
    square_y = (CANVAS_HEIGHT_PX - square_size) / 2

    # Create a new image with transparent background
    image = Image.new('RGBA', (CANVAS_WIDTH_PX, CANVAS_HEIGHT_PX), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Process messages
    lines = []
    circles = []
    num_messages = len(messages)
    LINE_SPACING = square_size / (num_messages + 1)  # Adjust line spacing

    for i in range(num_messages):
        timestamp, sender, message = messages[i]

        # Calculate y position (time)
        y_position = square_y + (i + 1) * LINE_SPACING

        # Process lab/mdef/anna messages
        if sender == 'lab/mdef/anna':
            try:
                message_value = int(message)
                if message_value != 0:
                    if message_value > 400:
                        message_value = 400
                    if message_value < 5:
                        message_value = 5
                    # Calculate line length
                    line_length = square_size / (message_value / LINE_THICKNESS_FACTOR) * 0.6

                    # Adjust line thickness based on distance
                    line_thickness = 4

                    # Calculate x position (start from the middle)
                    x_position = square_x + square_size / 2

                    # Add line to the list of lines
                    lines.append((x_position - line_length / 2, y_position, x_position + line_length / 2, y_position, line_thickness))
            except ValueError:
                print(f"Invalid message value: {message}")

        # Process lab/mdef/carmen messages
        elif sender == 'lab/mdef/carmen':
            # If it's an 'on' message, record the start time
            if message == 'on':
                start_circle_time = timestamp
            # If it's an 'off' message, calculate the time elapsed and generate a circle
            elif message == 'off':
                time_difference = timestamp - start_circle_time
                circle_radius = time_difference.total_seconds() * CIRCLE_RADIUS_FACTOR

                # Calculate x position (start from the middle)
                x_position = square_x + square_size / 2

                # Add circle to the list of circles
                circles.append((timestamp, x_position, circle_radius))

    # Draw lines
    for line in lines:
        x1, y1, x2, y2, thickness = line
        draw.line([(x1, y1), (x2, y2)], fill='red', width=int(thickness))

    # Draw circles and crosses
    for circle_time, circle_x, circle_radius in circles:
        y_position = (circle_time - start_time).total_seconds() / time_elapsed.total_seconds() * square_size + square_y

        # Draw circle with adjusted thickness
        circle_line_thickness = 4  # Adjust the line thickness for the circles
        draw.ellipse([(circle_x - circle_radius, y_position - circle_radius), 
                      (circle_x + circle_radius, y_position + circle_radius)], 
                     outline='red', width=circle_line_thickness)

        # Draw cross
        cross_size = 2
        draw.line([(circle_x - cross_size, y_position), (circle_x + cross_size, y_position)], fill='red', width=line_thickness)
        draw.line([(circle_x, y_position - cross_size), (circle_x, y_position + cross_size)], fill='red', width=line_thickness)

    # Print time elapsed
    time_elapsed_text = str(time_elapsed)
    text_width, text_height = draw.textsize(time_elapsed_text)
    text_position = ((CANVAS_WIDTH_PX - text_width) / 2, CANVAS_HEIGHT_PX - text_height - 10)
    draw.text(text_position, time_elapsed_text, fill='red')

    # Save the PNG file
    PNG_FILE = 'output.png'
    image.save(PNG_FILE)

    # Print time elapsed
    print(f'Time elapsed: {time_elapsed}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a CSV file and generate an image.')
    parser.add_argument('csv_file', type=str, help='Path to the input CSV file')
    args = parser.parse_args()

    main(args.csv_file)
