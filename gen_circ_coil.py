import matplotlib.pyplot as plt
import json
import numpy as np
import os


def ensure_coil_json_directory():
    """Ensure the coil_json directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json")
    if not os.path.exists(coil_json_dir):
        os.makedirs(coil_json_dir)
        print(f"Created coil_json directory: {coil_json_dir}")
    return coil_json_dir


def plot_circular_coil(center_x, center_y, initial_radius, turns, spacing):
    """
    Plot a circular spiral coil using Matplotlib with continuous angle progression.

    Args:
        center_x (float): X-coordinate of the coil's center.
        center_y (float): Y-coordinate of the coil's center.
        initial_radius (float): Radius of the initial circle.
        turns (int): Number of circular turns.
        spacing (float): Spacing between consecutive turns.

    Returns:
        None
    """
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Initialize the coil points
    points = []
    max_theta = 2 * np.pi * turns  # Total angle for the number of turns
    theta_values = np.linspace(0, max_theta, num=5000)  # Smooth continuous angles

    # Generate the circular spiral
    for theta in theta_values:
        radius = initial_radius + (spacing * theta / (2 * np.pi))  # Smoothly increase radius
        x = center_x + radius * np.cos(theta)
        y = center_y + radius * np.sin(theta)
        points.append((x, y))

    # Plot the spiral
    x_coords, y_coords = zip(*points)
    ax.plot(x_coords, y_coords, 'b-', linewidth=2)

    # Add labels and set aspect ratio
    ax.set_title("Connected Circular Spiral Coil")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    # Show the plot
    plt.show()


def generate_coil_json(center_x, center_y, initial_radius, turns, spacing, track_width=0.15, filename=None):
    """
    Generate a JSON file for a circular coil compatible with the KiCad plugin.

    Args:
        center_x (float): X-coordinate of the coil's center.
        center_y (float): Y-coordinate of the coil's center.
        initial_radius (float): Radius of the initial circle.
        turns (int): Number of circular turns.
        spacing (float): Spacing between consecutive turns.
        track_width (float): Width of the track in mm.
        filename (str): Name of the JSON file to save. If None, auto-generated.

    Returns:
        None
    """
    # Initialize the coil points
    points = []
    max_theta = 2 * np.pi * turns  # Total angle for the number of turns
    theta_values = np.linspace(0, max_theta, num=5000)  # Smooth continuous angles

    # Generate the circular spiral coordinates
    for theta in theta_values:
        radius = initial_radius + (spacing * theta / (2 * np.pi))  # Smoothly increase radius
        x = center_x + radius * np.cos(theta)
        y = center_y + radius * np.sin(theta)
        points.append({"x": x, "y": y})

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
        filename = f"circular_w{track_width:.2f}_s{spacing:.2f}_t{turns}.json"

    # Ensure coil_json directory exists and save file there
    coil_json_dir = ensure_coil_json_directory()
    file_path = os.path.join(coil_json_dir, filename)
    
    # Write to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Coil JSON saved to coil_json/{filename}")


def main():
    coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.5, "turns": 22, "spacing": 0.3, "track_width": 0.15}

    plot_circular_coil(
        center_x=coil["center_x"],
        center_y=coil["center_y"],
        initial_radius=coil["initial_radius"],
        turns=coil["turns"],
        spacing=coil["spacing"]
    )

    save_json_file = True
    if save_json_file:
        generate_coil_json(
            center_x=coil["center_x"],
            center_y=coil["center_y"],
            initial_radius=coil["initial_radius"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            track_width=coil["track_width"]
        )

if __name__ == '__main__':
    main()
