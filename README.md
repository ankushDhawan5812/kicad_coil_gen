[![Demo Video](https://img.youtube.com/vi/CDhlx_VMpCc/0.jpg)](https://www.youtube.com/watch?v=CDhlx_VMpCc)

# KiCad Coil Plugins

Generate PCB spiral coil footprints for KiCad. Each coil generator produces a matplotlib preview and exports a JSON file that can be imported into KiCad via the coil plugin. A set of Biot-Savart simulations are also included to model and compare the magnetic fields and forces produced by different coil geometries.

## Coil Generators

Five coil shape generators are available. Each one plots a preview of the coil and saves a JSON file to `coil_json/` with a filename that encodes all parameters:

| Script | Shape | Key Parameters |
|---|---|---|
| `gen_circ_coil.py` | Circular spiral | center, radius, turns, spacing, track width |
| `gen_ellipse_coil.py` | Elliptical spiral | center, x/y radii, turns, spacing, track width |
| `gen_rect_coil.py` | Rectangular spiral | start, width, height, turns, spacing, track width |
| `gen_square_coil.py` | Square spiral | start, side length, turns, spacing, track width |
| `gen_star_coil.py` | 5-pointed star spiral | center, radius, turns, spacing, track width, points per turn |

To run a generator, edit the `coil` dictionary in `main()` to set your desired parameters, then:

```bash
python3 gen_circ_coil.py
```

The output JSON is saved to `coil_json/` and can be loaded into KiCad using the coil plugin.

## Helpers

`helpers.py` provides shared geometry utilities: arc drawing, point rotation/translation/scaling, coordinate flipping, point-count optimization (collinear removal), and Chaikin curve smoothing.
