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
        w_steps = int(round(current_width / spacing))
        h_steps = int(round(current_height / spacing))
        # Right
        for i in range(w_steps):
            points.append((current_x, current_y))
            current_x += spacing
        # Up
        for i in range(h_steps):
            points.append((current_x, current_y))
            current_y += spacing
        # Left
        for i in range(w_steps):
            points.append((current_x, current_y))
            current_x -= spacing
        # Down (one step short to leave room for the inward step)
        for i in range(h_steps - 1):
            points.append((current_x, current_y))
            current_y -= spacing
        # Step inward to connect to next turn
        points.append((current_x, current_y))
        current_x += spacing

        current_width -= 2 * spacing
        current_height -= 2 * spacing

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


def generate_coil_json(start_x, start_y, initial_width, initial_height, turns, spacing, track_width=0.15, filename=None, project_name="default"):
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
        w_steps = int(round(current_width / spacing))
        h_steps = int(round(current_height / spacing))
        # Right
        for i in range(w_steps):
            points.append({"x": current_x, "y": current_y})
            current_x += spacing
        # Up
        for i in range(h_steps):
            points.append({"x": current_x, "y": current_y})
            current_y += spacing
        # Left
        for i in range(w_steps):
            points.append({"x": current_x, "y": current_y})
            current_x -= spacing
        # Down (one step short to leave room for the inward step)
        for i in range(h_steps - 1):
            points.append({"x": current_x, "y": current_y})
            current_y -= spacing
        # Step inward to connect to next turn
        points.append({"x": current_x, "y": current_y})
        current_x += spacing

        current_width -= 2 * spacing
        current_height -= 2 * spacing

    # DRC checks against manufacturer constraints
    via_hole_diameter = 0.3   # mm
    via_hole_to_track = 0.2   # mm (via hole edge to track edge)
    same_net_spacing = 0.15   # mm (track edge to track edge, trace coils)
    min_track_width = 0.15    # mm (trace coil min width)

    errors = []

    # Via hole to track: inner open area must fit via hole + clearance
    min_inner_dim = min(current_width, current_height)
    min_required = via_hole_diameter + 2 * (via_hole_to_track + track_width / 2)
    if min_inner_dim < min_required:
        errors.append(
            f"Inner clearance too small for via.\n"
            f"  Innermost open dimensions: {current_width:.3f} x {current_height:.3f} mm\n"
            f"  Minimum required: {min_required:.3f} mm  "
            f"(via_hole={via_hole_diameter} + 2*(hole_to_track={via_hole_to_track} + track_width/2={track_width/2}))"
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

    # Print final coil dimensions
    inner_width = initial_width - 2 * spacing * turns
    inner_height = initial_height - 2 * spacing * turns
    print(f"\n--- Rectangular Coil Dimensions ---")
    print(f"  Turns:          {turns}")
    print(f"  Track width:    {track_width} mm")
    print(f"  Spacing:        {spacing} mm")
    print(f"  Outer size:     {initial_width:.3f} x {initial_height:.3f} mm (W x H)")
    print(f"  Inner size:     {inner_width:.3f} x {inner_height:.3f} mm (W x H)")
    print(f"  Overall size:   {initial_width:.3f} x {initial_height:.3f} mm")
    print(f"-----------------------------------\n")

    # Extend the trace from the inner end to the center for the via
    center_x = start_x + initial_width / 2
    center_y = start_y + initial_height / 2
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
        filename = f"rect_sx{start_x}_sy{start_y}_w{initial_width}_h{initial_height}_t{turns}_s{spacing}_tw{track_width}.json"

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
    initial_width = 4
    initial_height = 3
    coil = {
        "start_x": -initial_width / 2,
        "start_y": -initial_height / 2,
        "initial_width": initial_width,
        "initial_height": initial_height,
        "turns": 4,
        "spacing": 0.3,
        "track_width": 0.15,
        "project_name": "small_scale_designs"
    }

    show_plot = False
    if show_plot:
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
            track_width=coil["track_width"],
            project_name=coil["project_name"]
        )

if __name__ == '__main__':
    main()
