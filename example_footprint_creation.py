#!/usr/bin/env python3
"""
Example script demonstrating how to create footprints from coil JSON files
"""

import json
import os
from coil_to_footprint import generate_footprint_file


def ensure_coil_footprints_directory():
    """Ensure the coil_footprints directory exists, create it if it doesn't"""
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


def create_footprint_from_existing_coil():
    """Example: Create a footprint from an existing coil JSON file"""
    
    # Check coil_json directory first
    coil_json_dir = ensure_coil_json_directory()
    
    # Look for JSON files in coil_json directory
    json_files = [f for f in os.listdir(coil_json_dir) if f.endswith('.json')]
    
    if json_files:
        # Use the first JSON file found
        coil_file = json_files[0]
        print(f"Creating footprint from coil_json/{coil_file}")
        
        # Read the coil data
        with open(os.path.join(coil_json_dir, coil_file), 'r') as f:
            coil_data = json.load(f)
        
        # Generate footprint filename in coil_footprints directory
        coil_footprints_dir = ensure_coil_footprints_directory()
        footprint_file = os.path.join(coil_footprints_dir, os.path.splitext(coil_file)[0] + '.kicad_mod')
        
        # Create the footprint
        generate_footprint_file(coil_data, footprint_file)
        print(f"Created footprint: coil_footprints/{os.path.basename(footprint_file)}")
    else:
        print("No coil JSON files found in coil_json/ directory")


def create_custom_coil_footprint():
    """Example: Create a footprint from a custom coil definition"""
    
    # Define a simple custom coil
    custom_coil = {
        "parameters": {
            "trackWidth": 0.2,
            "pinDiameter": 1.0,
            "pinDrillDiameter": 0.8,
            "viaDiameter": 0.8,
            "viaDrillDiameter": 0.4
        },
        "tracks": {
            "f": [
                {
                    "width": 0.2,
                    "pts": [
                        {"x": 0, "y": 0},
                        {"x": 1, "y": 0},
                        {"x": 1, "y": 1},
                        {"x": 0, "y": 1},
                        {"x": 0, "y": 0}
                    ]
                }
            ],
            "b": [],
            "in": []
        },
        "vias": [],
        "pads": [
            {"x": -1, "y": 0, "width": 0.5, "height": 0.5},
            {"x": 2, "y": 0, "width": 0.5, "height": 0.5}
        ],
        "silk": [
            {"text": "COIL", "x": 0.5, "y": -0.5, "size": 0.5, "layer": "f", "angle": 0}
        ],
        "edgeCuts": [],
        "components": []
    }
    
    # Save custom coil as JSON in coil_json directory
    coil_json_dir = ensure_coil_json_directory()
    custom_coil_path = os.path.join(coil_json_dir, 'custom_coil.json')
    with open(custom_coil_path, 'w') as f:
        json.dump(custom_coil, f, indent=2)
    
    # Create footprint in coil_footprints directory
    coil_footprints_dir = ensure_coil_footprints_directory()
    footprint_path = os.path.join(coil_footprints_dir, 'custom_coil.kicad_mod')
    generate_footprint_file(custom_coil, footprint_path)
    print(f"Created custom coil JSON: coil_json/custom_coil.json")
    print(f"Created custom coil footprint: coil_footprints/custom_coil.kicad_mod")


if __name__ == '__main__':
    print("Coil to Footprint Conversion Examples")
    print("=" * 40)
    
    print("\n1. Creating footprint from existing coil file:")
    create_footprint_from_existing_coil()
    
    print("\n2. Creating custom coil footprint:")
    create_custom_coil_footprint()
    
    print("\nDone! You can now import the .kicad_mod files from the coil_footprints/ directory into KiCad's footprint editor.")
