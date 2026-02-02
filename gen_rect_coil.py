import matplotlib.pyplot as plt
import json
import os


def ensure_coil_json_directory():
    """Ensure the coil_json directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json")
    if not os.path.exists(coil_json_dir):
        os.makedirs(coil_json_dir)
        print(f"Created coil_json directory: {coil_json_dir}")
    return coil_json_dir


def plot_rect_coil(start_x, start_y, initial_width, initial_height, turns, spacing):
    """
    Plot a connected spiral-in rectangular coil using Matplotlib.

    Args:
        start_x (float): X-coordinate of the starting point.
        start_y (float): Y-coordinate of the starting point.
        initial_width (float): Width of the initial rectangle.
        initial_height (float): Height of the initial rectangle.
        turns (int): Number of turns in the spiral.
        spacing (float): Spacing between consecutive turns.

    Returns:
        None
    """
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Initialize the coil points
    points = []
    current_x, current_y = start_x, start_y
    current_width, current_height = initial_width, initial_height

    # Generate the rectangular spiral
    for turn in range(turns):
        # Right
        for i in range(int(current_width / spacing)):
            points.append((current_x, current_y))
            current_x += spacing
        # Up
        for i in range(int(current_height / spacing)):
            points.append((current_x, current_y))
            current_y += spacing
        # Left
        for i in range(int(current_width / spacing)):
            points.append((current_x, current_y))
            current_x -= spacing
        # Down
        for i in range(int(current_height / spacing)):
            points.append((current_x, current_y))
            current_y -= spacing

        # Reduce size for next turn
        current_width -= 2 * spacing
        current_height -= 2 * spacing
        current_x += spacing
        current_y += spacing

    # Plot the spiral
    x_coords, y_coords = zip(*points)
    ax.plot(x_coords, y_coords, 'b-', linewidth=2)

    # Add labels and set aspect ratio
    ax.set_title("Connected Rectangular Spiral Coil")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    # Show the plot
    plt.show()


def generate_coil_json(start_x, start_y, initial_width, initial_height, turns, spacing, track_width=0.15, filename=None):
    """
    Generate a JSON file for a rectangular coil compatible with the KiCad plugin.

    Args:
        start_x (float): X-coordinate of the starting point.
        start_y (float): Y-coordinate of the starting point.
        initial_width (float): Width of the initial rectangle.
        initial_height (float): Height of the initial rectangle.
        turns (int): Number of turns in the spiral.
        spacing (float): Spacing between consecutive turns.
        track_width (float): Width of the track in mm.
        filename (str): Name of the JSON file to save. If None, auto-generated.

    Returns:
        None
    """
    # Initialize the coil points
    points = []
    current_x, current_y = start_x, start_y
    current_width, current_height = initial_width, initial_height

    # Generate the rectangular spiral coordinates
    for turn in range(turns):
        # Right
        for i in range(int(current_width / spacing)):
            points.append({"x": current_x, "y": current_y})
            current_x += spacing
        # Up
        for i in range(int(current_height / spacing)):
            points.append({"x": current_x, "y": current_y})
            current_y += spacing
        # Left
        for i in range(int(current_width / spacing)):
            points.append({"x": current_x, "y": current_y})
            current_x -= spacing
        # Down
        for i in range(int(current_height / spacing)):
            points.append({"x": current_x, "y": current_y})
            current_y -= spacing

        # Reduce size for next turn
        current_width -= 2 * spacing
        current_height -= 2 * spacing
        current_x += spacing
        current_y += spacing

    # Prepare the JSON data
    json_data = {
        "parameters": {
            "trackWidth": track_width,  # Use provided track width
            "pinDiameter": 1.0,
            "pinDrillDiameter": 0.8,
            "viaDiameter": 0.8,
            "viaDrillDiameter": 0.4,
        },
        "tracks": {
            "f": [{"width": track_width, "pts": points}],  # Front layer tracks
            "b": [],  # Back layer tracks (empty in this example)
            "in": []  # Internal layers (empty in this example)
        },
        "vias": [],  # Define vias if needed
        "pads": [],  # Define pads if needed
        "silk": [],  # Define silk screen elements if needed
        "edgeCuts": [],  # Define edge cuts if needed
        "components": []  # Define components if needed
    }

    # Generate filename if not provided
    if filename is None:
        filename = f"rect_w{track_width:.2f}_s{spacing:.2f}_t{turns}.json"

    # Ensure coil_json directory exists and save file there
    coil_json_dir = ensure_coil_json_directory()
    file_path = os.path.join(coil_json_dir, filename)
    
    # Write to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Coil JSON saved to coil_json/{filename}")


def main():
    coil = {
        "start_x": 0,
        "start_y": 0,
        "initial_width": 10,
        "initial_height": 8,
        "turns": 5,
        "spacing": 0.3,
        "track_width": 0.15
    }

    plot_rect_coil(
        start_x=coil["start_x"],
        start_y=coil["start_y"],
        initial_width=coil["initial_width"],
        initial_height=coil["initial_height"],
        turns=coil["turns"],
        spacing=coil["spacing"]
    )

    save_json_file = True
    if save_json_file:
        generate_coil_json(
            start_x=coil["start_x"],
            start_y=coil["start_y"],
            initial_width=coil["initial_width"],
            initial_height=coil["initial_height"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            track_width=coil["track_width"]
        )

if __name__ == '__main__':
    main()