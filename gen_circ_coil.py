import matplotlib.pyplot as plt
import json
import numpy as np
import os
from coil_to_footprint import generate_footprint_file, ensure_coil_footprints_directory


def ensure_coil_json_directory(project_name):
    """Ensure the coil_json/<project_name> directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json", project_name)
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


def generate_coil_json(center_x, center_y, initial_radius, turns, spacing, track_width=0.15, filename=None, project_name="default"):
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

    # DRC checks against manufacturer constraints
    via_hole_diameter = 0.3   # mm
    via_hole_to_track = 0.2   # mm (via hole edge to track edge)
    same_net_spacing = 0.15   # mm (track edge to track edge, trace coils)
    min_track_width = 0.15    # mm (trace coil min width)

    errors = []

    # Via hole to track: center to first trace must fit via hole + clearance
    min_inner_radius = via_hole_diameter / 2 + via_hole_to_track + track_width / 2
    if initial_radius < min_inner_radius:
        errors.append(
            f"Inner clearance too small for via.\n"
            f"  Inner radius: {initial_radius:.3f} mm\n"
            f"  Minimum required: {min_inner_radius:.3f} mm  "
            f"(via_hole/2={via_hole_diameter/2} + hole_to_track={via_hole_to_track} + track_width/2={track_width/2})"
        )

    # Same-net track spacing
    track_gap = spacing - track_width
    if track_gap < same_net_spacing:
        errors.append(
            f"Same-net track spacing too small.\n"
            f"  Track gap (spacing - track_width): {track_gap:.3f} mm\n"
            f"  Minimum required: {same_net_spacing} mm"
        )

    # Minimum track width check
    if track_width < min_track_width:
        errors.append(
            f"Track width too small.\n"
            f"  Track width: {track_width} mm\n"
            f"  Minimum required: {min_track_width} mm"
        )

    if errors:
        print("ERROR: DRC violations detected:")
        for i, e in enumerate(errors, 1):
            print(f"  [{i}] {e}")
        print("  Fix parameters before generating the coil.")

    # Prepend center point so the front trace runs from the via to the spiral
    points.insert(0, {"x": center_x, "y": center_y})

    # Back layer: mirror in X and reverse point order so current flows from
    # via outward in the same winding sense as the front (both layers produce
    # B-field in the same direction by the right-hand rule).
    back_points = [{"x": -p["x"], "y": p["y"]} for p in reversed(points)]

    # Front outer pad at the end of the front spiral; back outer pad at the
    # start of the back trace (the X-mirrored front outer end).
    pad_front = points[-1]
    pad_back = back_points[0]

    via_outer_diameter = 0.4   # mm
    via_drill_diameter = 0.3   # mm

    # Prepare the JSON data
    json_data = {
        "parameters": {
            "trackWidth": track_width,
            "pinDiameter": track_width,
            "pinDrillDiameter": 0.8,
            "viaDiameter": via_outer_diameter,
            "viaDrillDiameter": via_drill_diameter,
        },
        "tracks": {
            "f": [{"width": track_width, "pts": points}],       # Front: via -> spiral outward -> outer pad
            "b": [{"width": track_width, "pts": back_points}],  # Back:  mirrored outer pad -> via
            "in": []
        },
        "vias": [
            {"x": center_x, "y": center_y, "net": ""}
        ],
        "pads": [
            {"x": pad_front["x"], "y": pad_front["y"], "width": track_width, "height": track_width, "layer": "f", "angle": 0, "net": "", "clearance": 0.1},
            {"x": pad_back["x"],  "y": pad_back["y"],  "width": track_width, "height": track_width, "layer": "b", "angle": 0, "net": "", "clearance": 0.1}
        ],
        "silk": [],
        "edgeCuts": [],
        "components": []
    }

    # Print final coil dimensions
    outer_radius = initial_radius + spacing * turns
    print(f"\n--- Circular Coil Dimensions ---")
    print(f"  Turns:          {turns}")
    print(f"  Track width:    {track_width} mm")
    print(f"  Spacing:        {spacing} mm")
    print(f"  Inner radius:   {initial_radius:.3f} mm")
    print(f"  Outer radius:   {outer_radius:.3f} mm")
    print(f"  Overall diam:   {2 * outer_radius:.3f} mm")
    print(f"--------------------------------\n")

    # Generate filename if not provided
    if filename is None:
        filename = f"circular_cx{center_x}_cy{center_y}_r{initial_radius}_t{turns}_s{spacing}_w{track_width}.json"

    # Ensure coil_json/<project_name> directory exists and save file there
    coil_json_dir = ensure_coil_json_directory(project_name)
    file_path = os.path.join(coil_json_dir, filename)

    # Prompt user before saving
    save = input(f"Save to coil_json/{project_name}/{filename}? (y/n): ").strip().lower()
    if save == 'y':
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Coil JSON saved to coil_json/{project_name}/{filename}")

        # Optionally generate footprint immediately
        gen_fp = input("Generate footprint (.kicad_mod) now? (y/n): ").strip().lower()
        if gen_fp == 'y':
            fp_dir = ensure_coil_footprints_directory(project_name)
            fp_filename = os.path.splitext(filename)[0] + '.kicad_mod'
            fp_path = os.path.join(fp_dir, fp_filename)
            generate_footprint_file(json_data, fp_path)
            print(f"Footprint saved to coil_footprints/{project_name}/{fp_filename}")
    else:
        print("Skipped saving.")


def main():
    coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.4, "turns": 4, "spacing": 0.3, "track_width": 0.15, "project_name": "small_scale_designs"}

    show_plot = False
    if show_plot:
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
            track_width=coil["track_width"],
            project_name=coil["project_name"]
        )

if __name__ == '__main__':
    main()
