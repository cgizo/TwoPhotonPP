# 2Pprocessing

Python tools for reading, merging, motion-correcting, and downsampling `.tif` image stacks from 2-photon microscopy.

---

##  Features

- Load and stack multiple `.tif` files into 4D arrays (T, Z, Y, X)
- Average Z-projection across time series
- Split image stacks by Z-slice into independent time series
- Downsample large TIFF files (optional)
- Motion correction (2D only for now) using [CaImAn](https://github.com/flatironinstitute/CaImAn):
  - `rigid` and `pwrigid` motion correction supported
  - 3D motion correction planned (trying to figure out file input issues)
- Output saved as new TIFF files
- GUI folder selection using `tkinter.filedialog`

---

## Limitations

- Only `.tif` files are supported as input (no `.lsm`, `.czi`, etc.)
- 3D motion correction is **not yet implemented**
- Still in development, but **core functionality is working**

---

##  How to Use

1. Clone this repo
2. (Optional but recommended) create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows

## Author
Claire Gizowski, Calico Life Sciences
