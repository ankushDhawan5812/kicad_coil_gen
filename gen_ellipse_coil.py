import matplotlib.pyplot as plt
import json
import math
import numpy as np
import os


def ensure_coil_json_directory():
    """Ensure the coil_json directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json")
    if not os.path.exists(coil_json_dir):
        os.makedirs(coil_json_dir)
        print(f"Created coil_json directory: {coil_json_dir}")
    return coil_json_dir


def plot_elliptical_coil(center_x, center_y, initial_radius_x, initial_radius_y, turns, spacing):
    """
    Plot an elliptical spiral coil using Matplotlib.

    Args:
        center_x (float): X-coordinate of the coil's center.
        center_y (float): Y-coordinate of the coil's center.
        initial_radius_x (float): Initial radius along the x-axis.
        initial_radius_y (float): Initial radius along the y-axis.
        turns (int): Number of turns in the spiral.
        spacing (float): Spacing between consecutive turns.

    Returns:
        None
    """
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Generate the elliptical spiral
    theta_max = 2 * math.pi * turns
    theta = np.linspace(0, theta_max, num=1000 * turns)  # Adjust num points for smoothness
    # theta = theta * -1
    # Radii increase with spacing
    r_x = initial_radius_x + (spacing * theta) / (2 * math.pi)
    r_y = initial_radius_y + (spacing * theta) / (2 * math.pi)

    # Elliptical coordinates
    x = center_x + r_x * np.cos(theta)
    y = center_y - r_y * np.sin(theta)

    # Plot the spiral
    ax.plot(x, y, 'b-', linewidth=2)

    # Add labels and set aspect ratio
    ax.set_title("Connected Elliptical Spiral Coil")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    # Show the plot
    plt.show()


def generate_coil_json(center_x, center_y, initial_radius_x, initial_radius_y, turns, spacing, track_width=0.1, filename=None):
    """
    Generate a JSON file for an elliptical coil compatible with the KiCad plugin.

    Args:
        center_x (float): X-coordinate of the coil's center.
        center_y (float): Y-coordinate of the coil's center.
        initial_radius_x (float): Initial radius along the x-axis.
        initial_radius_y (float): Initial radius along the y-axis.
        turns (int): Number of turns in the spiral.
        spacing (float): Spacing between consecutive turns.
        track_width (float): Width of the track in mm.
        filename (str): Name of the JSON file to save. If None, auto-generated.

    Returns:
        None
    """
    # Generate the elliptical spiral coordinates
    theta_max = 2 * math.pi * turns
    theta = np.linspace(0, theta_max, num=1000 * turns)
    # theta = theta * -1a.
    # Radii increase with spacing
    r_x = initial_radius_x + (spacing * theta) / (2 * math.pi)
    r_y = initial_radius_y + (spacing * theta) / (2 * math.pi)

    # Elliptical coordinates
    x = center_x + r_x * np.cos(theta)
    y = center_y - r_y * np.sin(theta)

    # Prepare points for JSON
    points = [{"x": float(xi), "y": float(yi)} for xi, yi in zip(x, y)]

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
        filename = f"ellipse_w{track_width:.2f}_s{spacing:.2f}_t{turns}.json"

    # Ensure coil_json directory exists and save file there
    coil_json_dir = ensure_coil_json_directory()
    file_path = os.path.join(coil_json_dir, filename)
    
    # Write to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Coil JSON saved to coil_json/{filename}")


def main():
    coil = {
        "center_x": 0,
        "center_y": 0,
        "initial_radius_x": 1.4,  # Semi-major axis
        "initial_radius_y": 0.4,  # Semi-minor axis
        "turns": 10,
        "spacing": 0.3,
        "track_width": 0.15
    }

    plot_elliptical_coil(
        center_x=coil["center_x"],
        center_y=coil["center_y"],
        initial_radius_x=coil["initial_radius_x"],
        initial_radius_y=coil["initial_radius_y"],
        turns=coil["turns"],
        spacing=coil["spacing"]
    )

    save_json_file = True
    if save_json_file:
        generate_coil_json(
            center_x=coil["center_x"],
            center_y=coil["center_y"],
            initial_radius_x=coil["initial_radius_x"],
            initial_radius_y=coil["initial_radius_y"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            track_width=coil["track_width"]
        )

if __name__ == '__main__':
    main()
