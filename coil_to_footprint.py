#!/usr/bin/env python3
"""
Standalone script to convert coil JSON files to KiCad footprint files (.kicad_mod)
Usage: python coil_to_footprint.py [input.json] [output.kicad_mod]
       python coil_to_footprint.py --batch [input_dir] [output_dir]
"""

import json
import sys
import os
import argparse


def generate_footprint_file(coil_data, output_path):
    """Generate a KiCad footprint file (.kicad_mod) from coil data"""
    
    # Extract parameters
    track_width = coil_data["parameters"]["trackWidth"]
    via_diameter = coil_data["parameters"]["viaDiameter"]
    via_drill_diameter = coil_data["parameters"]["viaDrillDiameter"]
    
    # Get footprint name from filename
    footprint_name = os.path.splitext(os.path.basename(output_path))[0]
    
    # Start building the footprint file content
    lines = []
    lines.append("(footprint \"{}\"".format(footprint_name))
    lines.append("  (version 20211014)")
    lines.append("  (generator pcbnew)")
    lines.append("  (generator_version \"7.0.0\")")
    lines.append("  (layer \"F.Cu\")")
    lines.append("  (descr \"Custom coil footprint generated from JSON\")")
    lines.append("  (tags \"coil custom\")")
    lines.append("  (attr smd)")
    lines.append("  (fp_text reference \"REF**\" (at 0 -2.5) (layer \"F.SilkS\")")
    lines.append("    (effects (font (size 1 1) (thickness 0.15)))")
    lines.append("  )")
    lines.append("  (fp_text value \"{}\" (at 0 2.5) (layer \"F.Fab\")".format(footprint_name))
    lines.append("    (effects (font (size 1 1) (thickness 0.15)))")
    lines.append("  )")
    
    # Add tracks from front layer
    for track in coil_data["tracks"]["f"]:
        points = track["pts"]
        if len(points) >= 2:
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                lines.append("  (fp_line (start {} {}) (end {} {}) (stroke (width {}) (type solid)) (layer \"F.Cu\"))".format(
                    start["x"], start["y"], end["x"], end["y"], track["width"]
                ))
    
    # Add tracks from back layer
    for track in coil_data["tracks"]["b"]:
        points = track["pts"]
        if len(points) >= 2:
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                lines.append("  (fp_line (start {} {}) (end {} {}) (stroke (width {}) (type solid)) (layer \"B.Cu\"))".format(
                    start["x"], start["y"], end["x"], end["y"], track["width"]
                ))
    
    # Add internal layer tracks
    internal_layers = ["In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "In5.Cu", "In6.Cu"]
    for i, track_list in enumerate(coil_data["tracks"]["in"]):
        if i < len(internal_layers):
            layer_name = internal_layers[i]
            for track in track_list:
                points = track["pts"]
                if len(points) >= 2:
                    for j in range(len(points) - 1):
                        start = points[j]
                        end = points[j + 1]
                        lines.append("  (fp_line (start {} {}) (end {} {}) (stroke (width {}) (type solid)) (layer \"{}\"))".format(
                            start["x"], start["y"], end["x"], end["y"], track["width"], layer_name
                        ))
    
    # Add vias
    for via in coil_data["vias"]:
        lines.append("  (pad \"\" np_thru_hole circle (at {} {}) (size {} {}) (drill {}) (layers \"*.Cu\" \"*.Mask\"))".format(
            via["x"], via["y"], via_diameter, via_diameter, via_drill_diameter
        ))
    
    # Add pads
    for i, pad in enumerate(coil_data["pads"]):
        pad_num = str(i + 1)  # Simple numbering
        if pad.get("layer", "f") == "b":
            layers = "\"B.Cu\" \"B.Paste\" \"B.Mask\""
        else:
            layers = "\"F.Cu\" \"F.Paste\" \"F.Mask\""
        lines.append("  (pad \"{}\" smd rect (at {} {}) (size {} {}) (layers {}))".format(
            pad_num, pad["x"], pad["y"], pad["width"], pad["height"], layers
        ))
    
    # Add silk screen elements
    for text in coil_data["silk"]:
        layer = "F.SilkS" if text["layer"] == "f" else "B.SilkS"
        lines.append("  (fp_text user \"{}\" (at {} {}) (layer \"{}\")".format(
            text["text"], text["x"], text["y"], layer
        ))
        lines.append("    (effects (font (size {} {}) (thickness 0.15)))".format(text["size"], text["size"]))
        if "angle" in text and text["angle"] != 0:
            lines.append("    (t_justify (angle {}))".format(text["angle"]))
        lines.append("  )")
    
    # Add edge cuts
    for edge_cut in coil_data["edgeCuts"]:
        if len(edge_cut) >= 2:
            for i in range(len(edge_cut) - 1):
                start = edge_cut[i]
                end = edge_cut[i + 1]
                lines.append("  (fp_line (start {} {}) (end {} {}) (stroke (width 0.1) (type solid)) (layer \"Edge.Cuts\"))".format(
                    start["x"], start["y"], end["x"], end["y"]
                ))
            # Close the polygon if it's not already closed
            if len(edge_cut) > 2:
                start = edge_cut[-1]
                end = edge_cut[0]
                lines.append("  (fp_line (start {} {}) (end {} {}) (stroke (width 0.1) (type solid)) (layer \"Edge.Cuts\"))".format(
                    start["x"], start["y"], end["x"], end["y"]
                ))
    
    lines.append(")")
    
    # Write the footprint file
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def ensure_coil_footprints_directory(project_name=None):
    """Ensure the coil_footprints[/<project_name>] directory exists, create it if it doesn't"""
    if project_name:
        coil_footprints_dir = os.path.join(os.getcwd(), "coil_footprints", project_name)
    else:
        coil_footprints_dir = os.path.join(os.getcwd(), "coil_footprints")
    if not os.path.exists(coil_footprints_dir):
        os.makedirs(coil_footprints_dir)
        print(f"Created coil_footprints directory: {coil_footprints_dir}")
    return coil_footprints_dir


def ensure_coil_json_directory():
    """Ensure the coil_json directory exists, create it if it doesn't"""
    coil_json_dir = os.path.join(os.getcwd(), "coil_json")
    if not os.path.exists(coil_json_dir):
        os.makedirs(coil_json_dir)
        print(f"Created coil_json directory: {coil_json_dir}")
    return coil_json_dir


def main():
    parser = argparse.ArgumentParser(description='Convert coil JSON files to KiCad footprint files')
    parser.add_argument('input', help='Input coil JSON file, or a directory when using --batch')
    parser.add_argument('output', nargs='?', help='Output footprint file (.kicad_mod) or directory (optional, defaults to coil_footprints/)')
    parser.add_argument('--batch', action='store_true', help='Process all files in a directory')

    args = parser.parse_args()
    
    if args.batch:
        # Batch processing
        if not os.path.isdir(args.input):
            print("Error: Input must be a directory when using --batch")
            sys.exit(1)

        total_converted = 0

        # Walk through input dir: process JSON files at top level and in project subfolders
        for entry in sorted(os.listdir(args.input)):
            entry_path = os.path.join(args.input, entry)

            if os.path.isfile(entry_path) and entry.endswith('.json'):
                # JSON directly in coil_json/ (no project subfolder)
                output_dir = ensure_coil_footprints_directory()
                output_filename = os.path.splitext(entry)[0] + '.kicad_mod'
                output_path = os.path.join(output_dir, output_filename)
                try:
                    with open(entry_path, 'r') as f:
                        coil_data = json.load(f)
                    generate_footprint_file(coil_data, output_path)
                    print(f"Converted: {entry} -> coil_footprints/{output_filename}")
                    total_converted += 1
                except Exception as e:
                    print(f"Error processing {entry}: {str(e)}")

            elif os.path.isdir(entry_path):
                # Project subfolder
                project_name = entry
                json_files = [f for f in os.listdir(entry_path) if f.endswith('.json')]
                if not json_files:
                    continue
                output_dir = ensure_coil_footprints_directory(project_name)
                print(f"Processing project: {project_name}/ ({len(json_files)} files)")
                for json_file in sorted(json_files):
                    input_path = os.path.join(entry_path, json_file)
                    output_filename = os.path.splitext(json_file)[0] + '.kicad_mod'
                    output_path = os.path.join(output_dir, output_filename)
                    try:
                        with open(input_path, 'r') as f:
                            coil_data = json.load(f)
                        generate_footprint_file(coil_data, output_path)
                        print(f"  Converted: {json_file} -> coil_footprints/{project_name}/{output_filename}")
                        total_converted += 1
                    except Exception as e:
                        print(f"  Error processing {json_file}: {str(e)}")

        if total_converted == 0:
            print(f"No JSON files found in {args.input}/")
            sys.exit(1)
        print(f"\nConverted {total_converted} file(s) total.")

    else:
        # Single file processing
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found")
            sys.exit(1)

        try:
            with open(args.input, 'r') as f:
                coil_data = json.load(f)

            # Determine output path
            if args.output:
                output_path = args.output
            else:
                # Infer project subfolder if input is coil_json/<project>/<file>.json
                input_filename = os.path.basename(args.input)
                output_filename = os.path.splitext(input_filename)[0] + '.kicad_mod'
                parent_dir = os.path.basename(os.path.dirname(args.input))
                grandparent_dir = os.path.basename(os.path.dirname(os.path.dirname(args.input)))
                if grandparent_dir == "coil_json":
                    # Input is inside a project subfolder
                    project_name = parent_dir
                    coil_footprints_dir = ensure_coil_footprints_directory(project_name)
                else:
                    coil_footprints_dir = ensure_coil_footprints_directory()
                output_path = os.path.join(coil_footprints_dir, output_filename)

            generate_footprint_file(coil_data, output_path)
            print(f"Successfully converted {args.input} to {output_path}")

        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)


if __name__ == '__main__':
    main()
