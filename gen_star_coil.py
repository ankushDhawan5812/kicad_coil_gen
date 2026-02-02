import matplotlib.pyplot as plt
import json
import math
import numpy as np

def distance_btw_points(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def plot_star_coil(center_x, center_y, initial_radius, turns, spacing, points_per_turn=10):
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    # Starting point
    radius = initial_radius
    points = []
    angle_step = 2 * math.pi / points_per_turn * -1

    print(f"Inner radius: {radius}, Outer radius: {radius + spacing}")

    for turn in range(turns):
        radius += spacing
        spac_inc = spacing + 0.1 * turn

        for i in range(points_per_turn):
            # Alternate between inner and outer radius
            current_radius = radius - spac_inc if i % 2 == 0 else radius + spac_inc
            # print(f"Turn {turn + 1}, current radius: {current_radius}")
            angle = i * angle_step + turn * 2 * math.pi / points_per_turn

            x = center_x + current_radius * math.cos(angle - (turn) * math.pi/5 - (math.pi/10)) # rotate by offset since there are 5 points on star
            y = center_y + current_radius * math.sin(angle - (turn) * math.pi/5 - (math.pi/10))
        
            print(f"Turn {turn + 1}, point {i + 1}: ({x}, {y})")
            points.append((x, y))
    
    print(f"Radius" , radius)
 
    # Plot the spiral
    x_coords, y_coords = zip(*points)
    ax.plot(x_coords, y_coords, 'b-', linewidth=2)

    # Add labels and set aspect ratio
    ax.set_title("Connected Spiral-In Star Coil")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    # Show the plot
    plt.show()


def generate_star_coil_json(center_x, center_y, initial_radius, turns, spacing, filename="star_coil.json", points_per_turn=10):
    radius = initial_radius
    points = []
    angle_step = 2 * math.pi / points_per_turn * -1

    for turn in range(turns):
        radius += spacing
        spac_inc = spacing + 0.1 * turn

        for i in range(points_per_turn):
            # Alternate between inner and outer radius
            current_radius = radius - spac_inc if i % 2 == 0 else radius + spac_inc
            # print(f"Turn {turn + 1}, current radius: {current_radius}")
            angle = i * angle_step + turn * 2 * math.pi / points_per_turn
            x = center_x + current_radius * math.cos(angle - (turn) * math.pi/5 - (math.pi/10)) # rotate by offset since there are 5 points on star
            y = center_y + current_radius * math.sin(angle - (turn) * math.pi/5 - (math.pi/10))
        
            print(f"Turn {turn + 1}, point {i + 1}: ({x}, {y})")
            points.append({"x": x, "y": y})

    # Prepare the JSON data
    json_data = {
        "parameters": {
            "trackWidth": 0.1,  # Example width in mm
            "pinDiameter": 1.0,
            "pinDrillDiameter": 0.8,
            "viaDiameter": 0.8,
            "viaDrillDiameter": 0.4,
        },
        "tracks": {
            "f": [{"width": 0.1, "pts": points}],  # Front layer tracks
            "b": [],  # Back layer tracks (empty in this example)
            "in": []  # Internal layers (empty in this example)
        },
        "vias": [],  # Define vias if needed
        "pads": [],  # Define pads if needed
        "silk": [],  # Define silk screen elements if needed
        "edgeCuts": [],  # Define edge cuts if needed
        "components": []  # Define components if needed
    }

    # Write to a JSON file
    with open(filename, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Star coil JSON saved to {filename}")

def main():
    # coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.5, "turns": 10, "spacing": 0.6, "points_per_turn": 10}
    coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.7, "turns": 8, "spacing": 0.35, "points_per_turn": 10}

    plot_star_coil(
        center_x=coil["center_x"],
        center_y=coil["center_y"],
        initial_radius=coil["initial_radius"],
        turns=coil["turns"],
        spacing=coil["spacing"],
        points_per_turn=coil["points_per_turn"]
    )

    save_json_file = True
    fn = "star_coil_13_turns_wider.json"
    if save_json_file:
        generate_star_coil_json(
            center_x=coil["center_x"],
            center_y=coil["center_y"],
            initial_radius=coil["initial_radius"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            filename=fn,
            points_per_turn=coil["points_per_turn"]
        )


if __name__ == '__main__':
    main()

    
    # Write to a JSON file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    print(f"Star coil JSON saved to coil_json/{filename}")


def main():
    # coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.5, "turns": 10, "spacing": 0.6, "points_per_turn": 10}
    coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.7, "turns": 8, "spacing": 0.35, "track_width": 0.1, "points_per_turn": 10}

    plot_star_coil(
        center_x=coil["center_x"],
        center_y=coil["center_y"],
        initial_radius=coil["initial_radius"],
        turns=coil["turns"],
        spacing=coil["spacing"],
        points_per_turn=coil["points_per_turn"]
    )

    save_json_file = True
    if save_json_file:
        generate_star_coil_json(
            center_x=coil["center_x"],
            center_y=coil["center_y"],
            initial_radius=coil["initial_radius"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            track_width=coil["track_width"],
            points_per_turn=coil["points_per_turn"]
        )


if __name__ == '__main__':
    main()
