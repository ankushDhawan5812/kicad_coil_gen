import matplotlib.pyplot as plt
import json
import math
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


def generate_coil_json(center_x, center_y, initial_radius_x, initial_radius_y, turns, spacing, track_width=0.1, filename=None, project_name="default"):
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

    # Prepare points for JSON (spiral only, inner to outer)
    points = [{"x": float(xi), "y": float(yi)} for xi, yi in zip(x, y)]

    # DRC checks against manufacturer constraints
    via_hole_diameter = 0.3   # mm
    via_hole_to_track = 0.2   # mm (via hole edge to track edge)
    same_net_spacing = 0.15   # mm (track edge to track edge, trace coils)
    min_track_width = 0.15    # mm (trace coil min width)

    errors = []

    # Via hole to track: center to nearest trace must fit via hole + clearance
    min_inner_radius = min(initial_radius_x, initial_radius_y)
    min_required = via_hole_diameter / 2 + via_hole_to_track + track_width / 2
    if min_inner_radius < min_required:
        errors.append(
            f"Inner clearance too small for via.\n"
            f"  Min inner radius: {min_inner_radius:.3f} mm\n"
            f"  Minimum required: {min_required:.3f} mm  "
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

    # Prepend center point so front trace runs from via through spiral to outer pad
    points.insert(0, {"x": float(center_x), "y": float(center_y)})

    # Back layer: mirror in X and reverse so trace runs from mirrored outer end to via
    back_points = [{"x": -p["x"], "y": p["y"]} for p in reversed(points)]

    # Prepare the JSON data
    json_data = {
        "parameters": {
            "trackWidth": track_width,
            "pinDiameter": track_width,
            "pinDrillDiameter": 0.8,
            "viaDiameter": 0.4,
            "viaDrillDiameter": 0.3,
        },
        "tracks": {
            "f": [{"width": track_width, "pts": points}],  # Front layer: center -> spiral outward -> outer pad
            "b": [{"width": track_width, "pts": back_points}],  # Back layer: mirrored outer end -> spiral inward -> center
            "in": []  # Internal layers (empty in this example)
        },
        "vias": [
            {
                "x": float(center_x),
                "y": float(center_y),
                "diameter": 0.4,
                "drill": 0.3
            }
        ],
        "pads": [
            {
                "x": points[-1]["x"],
                "y": points[-1]["y"],
                "width": track_width,
                "height": track_width,
                "clearance": 0.1,
                "layer": "f"
            },
            {
                "x": back_points[0]["x"],
                "y": back_points[0]["y"],
                "width": track_width,
                "height": track_width,
                "clearance": 0.1,
                "layer": "b"
            }
        ],
        "silk": [],  # Define silk screen elements if needed
        "edgeCuts": [],  # Define edge cuts if needed
        "components": []  # Define components if needed
    }

    # Print final coil dimensions
    outer_radius_x = initial_radius_x + spacing * turns
    outer_radius_y = initial_radius_y + spacing * turns
    print(f"\n--- Elliptical Coil Dimensions ---")
    print(f"  Turns:            {turns}")
    print(f"  Track width:      {track_width} mm")
    print(f"  Spacing:          {spacing} mm")
    print(f"  Inner radii:      x={initial_radius_x:.3f} mm,  y={initial_radius_y:.3f} mm")
    print(f"  Outer radii:      x={outer_radius_x:.3f} mm,  y={outer_radius_y:.3f} mm")
    print(f"  Overall size:     {2 * outer_radius_x:.3f} x {2 * outer_radius_y:.3f} mm (W x H)")
    print(f"---------------------------------\n")

    # Generate filename if not provided
    if filename is None:
        filename = f"ellipse_cx{center_x}_cy{center_y}_rx{initial_radius_x}_ry{initial_radius_y}_t{turns}_s{spacing}_w{track_width}.json"

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
    coil = {
        "center_x": 0,
        "center_y": 0,
        "initial_radius_x": 0.7,  # Semi-major axis
        "initial_radius_y": 0.35,  # Semi-minor axis
        "turns": 4,
        "spacing": 0.3,
        "track_width": 0.15,
        "project_name": "small_scale_designs"
    }

    show_plot = True
    if show_plot:
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
            track_width=coil["track_width"],
            project_name=coil["project_name"]
        )

if __name__ == '__main__':
    main()
