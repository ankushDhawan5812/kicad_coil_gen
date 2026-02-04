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

def distance_btw_points(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def generate_star_spiral_points(center_x, center_y, initial_radius, turns, spacing, num_star_points, inner_ratio):
    """
    Generate a continuous outward star spiral.
    Each point advances by pi/num_star_points radians. Tips (even indices) are at
    outer_r, valleys (odd) at inner_r = outer_r * inner_ratio. Both radii grow
    linearly so the spiral expands smoothly turn by turn.
    """
    points_per_star = num_star_points * 2  # 10 for a 5-pointed star
    total_points = turns * points_per_star
    pts = []
    for i in range(total_points):
        frac_turn = i / points_per_star  # 0.0 .. turns-0.1
        outer_r = initial_radius + spacing * (frac_turn + 1)
        inner_r = outer_r * inner_ratio
        r = outer_r if i % 2 == 0 else inner_r
        angle = i * math.pi / num_star_points + math.radians(18)  # continuous, never wraps; offset 18° so star is upright
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        pts.append((x, y))
    return pts


def plot_star_coil(center_x, center_y, initial_radius, turns, spacing, points_per_turn=10, track_width=0.15, inner_ratio=0.60):
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    num_star_points = points_per_turn // 2  # 5 for a 5-pointed star

    points = generate_star_spiral_points(center_x, center_y, initial_radius, turns, spacing, num_star_points, inner_ratio)

    print(f"Inner radius (turn 1): {(initial_radius + spacing) * inner_ratio:.3f} mm")
    print(f"Outer radius (turn {turns}): {initial_radius + spacing * turns:.3f} mm")

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


def generate_star_coil_json(center_x, center_y, initial_radius, turns, spacing, track_width=0.1, filename=None, points_per_turn=10, project_name="default", inner_ratio=0.60):
    num_star_points = points_per_turn // 2  # 5 for a 5-pointed star

    raw_pts = generate_star_spiral_points(center_x, center_y, initial_radius, turns, spacing, num_star_points, inner_ratio)
    points = []
    for p in raw_pts:
        print(f"  ({p[0]:.3f}, {p[1]:.3f})")
        points.append({"x": p[0], "y": p[1]})

    # Print final coil dimensions
    outer_radius = initial_radius + spacing * turns
    print(f"\n--- Star Coil Dimensions ---")
    print(f"  Turns:          {turns}")
    print(f"  Track width:    {track_width} mm")
    print(f"  Spacing:        {spacing} mm")
    print(f"  Points/turn:    {points_per_turn}")
    print(f"  Inner radius:   {initial_radius:.3f} mm")
    print(f"  Outer radius:   {outer_radius:.3f} mm")
    print(f"  Overall diam:   {2 * outer_radius:.3f} mm")
    print(f"----------------------------\n")

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

    # Prepend center point so trace connects from via at center to inner end of spiral
    points.insert(0, {"x": center_x, "y": center_y})

    # Back layer: mirror X and reverse
    # points[0] is center, points[-1] is outer end (front layer: center -> outward)
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
            "f": [{"width": track_width, "pts": points}],  # Front layer: center (via) -> spiral outward -> outer pad
            "b": [{"width": track_width, "pts": back_points}],  # Back layer: mirrored X, reversed
            "in": []  # Internal layers (empty in this example)
        },
        "vias": [
            {
                "x": center_x,
                "y": center_y,
                "d": 0.4,
                "drill": 0.3
            }
        ],
        "pads": [
            {
                "x": points[-1]["x"],
                "y": points[-1]["y"],
                "width": track_width,
                "height": track_width,
                "layer": "f",
                "clearance": 0.1
            },
            {
                "x": back_points[0]["x"],
                "y": back_points[0]["y"],
                "width": track_width,
                "height": track_width,
                "layer": "b",
                "clearance": 0.1
            }
        ],
        "silk": [],  # Define silk screen elements if needed
        "edgeCuts": [],  # Define edge cuts if needed
        "components": []  # Define components if needed
    }

    # Generate filename if not provided
    if filename is None:
        filename = f"star_cx{center_x}_cy{center_y}_r{initial_radius}_t{turns}_s{spacing}_w{track_width}_ppt{points_per_turn}.json"

    # Ensure coil_json/<project_name> directory exists and save file there
    coil_json_dir = ensure_coil_json_directory(project_name)
    file_path = os.path.join(coil_json_dir, filename)

    # Prompt user before saving
    save = input(f"Save to coil_json/{project_name}/{filename}? (y/n): ").strip().lower()
    if save == 'y':
        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"Star coil JSON saved to coil_json/{project_name}/{filename}")

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
    # coil = {"center_x": 0, "center_y": 0, "initial_radius": 0.5, "turns": 10, "spacing": 0.6, "points_per_turn": 10}
    coil = {"center_x": 0, 
            "center_y": 0, 
            "initial_radius": 0.5, 
            "turns": 4, 
            "spacing": 0.6, 
            "track_width": 0.15, 
            "points_per_turn": 10, 
            "inner_ratio": 0.55, 
            "project_name": "small_scale_designs"}

    show_plot = True
    if show_plot:
        plot_star_coil(
            center_x=coil["center_x"],
            center_y=coil["center_y"],
            initial_radius=coil["initial_radius"],
            turns=coil["turns"],
            spacing=coil["spacing"],
            points_per_turn=coil["points_per_turn"],
            track_width=coil["track_width"],
            inner_ratio=coil["inner_ratio"]
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
            points_per_turn=coil["points_per_turn"],
            project_name=coil["project_name"],
            inner_ratio=coil["inner_ratio"]
        )


if __name__ == '__main__':
    main()
