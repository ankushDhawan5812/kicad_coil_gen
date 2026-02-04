import matplotlib.pyplot as plt
import json
import os
from coil_to_footprint import generate_footprint_file, ensure_coil_footprints_directory


def ensure_coil_json_directory(project_name):
    """Ensure the coil_json/<project_name> directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json", project_name)
    if not os.path.exists(coil_json_dir):
        os.makedirs(coil_json_dir)
        print(f"Created coil_json directory: {coil_json_dir}")
    return coil_json_dir


def plot_square_coil(start_x, start_y, initial_side, turns, spacing):
    """
    Plot a connected spiral-in square coil using Matplotlib.

    Args:
        start_x (float): X-coordinate of the starting point.
        start_y (float): Y-coordinate of the starting point.
        initial_side (float): Length of the initial square's side.
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
    current_side = initial_side

    # Generate the square spiral
    for turn in range(turns):
        steps = int(round(current_side / spacing))
        # Right
        for i in range(steps):
            points.append((current_x, current_y))
            current_x += spacing
        # Up
        for i in range(steps):
            points.append((current_x, current_y))
            current_y += spacing
        # Left
        for i in range(steps):
            points.append((current_x, current_y))
            current_x -= spacing
        # Down (one step short to leave room for the inward step)
        for i in range(steps - 1):
            points.append((current_x, current_y))
            current_y -= spacing
        # Step inward to connect to next turn
        points.append((current_x, current_y))
        current_x += spacing

        current_side -= 2 * spacing

    # Plot the spiral
    x_coords, y_coords = zip(*points)
    ax.plot(x_coords, y_coords, 'b-', linewidth=2)

    # Add labels and set aspect ratio
    ax.set_title("Connected Square Spiral Coil")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_aspect('equal', 'box')
    ax.grid(True)

    # Show the plot
    plt.show()


def generate_coil_json(start_x, start_y, initial_side, turns, spacing, track_width=0.15, filename=None, project_name="default"):
    """
    Generate a JSON file for a square coil compatible with the KiCad plugin.

    Args:
        start_x (float): X-coordinate of the starting point.
        start_y (float): Y-coordinate of the starting point.
        initial_side (float): Length of the initial square's side.
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
    current_side = initial_side

    # Generate the square spiral coordinates
    for turn in range(turns):
        steps = int(round(current_side / spacing))
        # Right
        for i in range(steps):
            points.append({"x": current_x, "y": current_y})
            current_x += spacing
        # Up
        for i in range(steps):
            points.append({"x": current_x, "y": current_y})
            current_y += spacing
        # Left
        for i in range(steps):
            points.append({"x": current_x, "y": current_y})
            current_x -= spacing
        # Down (one step short to leave room for the inward step)
        for i in range(steps - 1):
            points.append({"x": current_x, "y": current_y})
            current_y -= spacing
        # Step inward to connect to next turn
        points.append({"x": current_x, "y": current_y})
        current_x += spacing

        current_side -= 2 * spacing

    # DRC checks against manufacturer constraints
    via_hole_diameter = 0.3   # mm
    via_hole_to_track = 0.2   # mm (via hole edge to track edge)
    same_net_spacing = 0.15   # mm (track edge to track edge, trace coils)
    min_track_width = 0.15    # mm (trace coil min width)

    errors = []

    # Via hole to track: inner open side must fit via hole + clearance on each side
    # Each side: via_hole_radius + via_hole_to_track + track_width/2
    min_inner_side = via_hole_diameter + 2 * (via_hole_to_track + track_width / 2)
    if current_side < min_inner_side:
        errors.append(
            f"Inner clearance too small for via.\n"
            f"  Innermost open side: {current_side:.3f} mm\n"
            f"  Minimum required:    {min_inner_side:.3f} mm  "
            f"(via_hole={via_hole_diameter} + 2*(hole_to_track={via_hole_to_track} + track_width/2={track_width/2}))"
        )

    # Same-net track spacing: gap between adjacent turns must be >= 0.25mm
    # Gap = spacing - track_width (spacing is center-to-center)
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

    # Print final coil dimensions
    inner_side = initial_side - 2 * spacing * turns
    print(f"\n--- Square Coil Dimensions ---")
    print(f"  Turns:          {turns}")
    print(f"  Track width:    {track_width} mm")
    print(f"  Spacing:        {spacing} mm")
    print(f"  Outer side:     {initial_side:.3f} mm")
    print(f"  Inner side:     {inner_side:.3f} mm")
    print(f"  Overall size:   {initial_side:.3f} x {initial_side:.3f} mm")
    print(f"------------------------------\n")

    # Extend the trace from the inner end to the center for the via
    center_x = start_x + initial_side / 2
    center_y = start_y + initial_side / 2
    points.append({"x": center_x, "y": center_y})

    # Back layer: mirror in X and reverse point order so current flows from
    # via outward in the same winding sense as the front (both layers produce
    # B-field in the same direction by the right-hand rule).
    back_points = [{"x": -p["x"], "y": p["y"]} for p in reversed(points)]

    # Front outer pad and back outer pad (X-mirrored)
    pad_front = points[0]
    pad_back = back_points[-1]

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
            "f": [{"width": track_width, "pts": points}],       # Front: outer pad -> via
            "b": [{"width": track_width, "pts": back_points}],  # Back:  via -> outer pad (mirrored)
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

    # Generate filename if not provided
    if filename is None:
        filename = f"square_sx{start_x}_sy{start_y}_side{initial_side}_t{turns}_s{spacing}_tw{track_width}.json"

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
    initial_side = 3
    coil = {
        "start_x": -initial_side / 2,  # offset so coil is centered at origin
        "start_y": -initial_side / 2,
        "initial_side": initial_side,
        "turns": 4,
        "spacing": 0.3,
        "track_width": 0.15,
        "project_name": "small_scale_designs"
    }

    show_plot = True
    if show_plot:
        plot_square_coil(
            start_x=coil["start_x"],
            start_y=coil["start_y"],
            initial_side=coil["initial_side"],
            turns=coil["turns"],
            spacing=coil["spacing"]
        )

    save_json_file = True
    if save_json_file:
        generate_coil_json(
            start_x=coil["start_x"],
            start_y=coil["start_y"],
            initial_side=coil["initial_side"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            track_width=coil["track_width"],
            project_name=coil["project_name"]
        )

if __name__ == '__main__':
    main()