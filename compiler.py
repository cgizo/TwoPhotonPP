import tifffile
import numpy as np
import glob
import os
from tkinter import filedialog, messagebox, simpledialog


def read_tif_files_merge_z_and_t(directory, zstack_len):

    files = sorted(glob.glob(os.path.join(directory, "*.tif")))
    all_zstacks = []


    print(f"Loaddd z stack:")
    for file in files:
        print(f"Processing: {file}")
        try:
            with tifffile.TiffFile(file) as tif:
                zstack = [page.asarray().astype(np.uint16) for page in tif.pages]
                if len(zstack) != zstack_len:
                    print(f"skipping {file}: expected {zstack_len} slices, found {len(zstack)}")
                    continue
                all_zstacks.append(np.stack(zstack))


        except Exception as e:
            print(f"Skipping {file} due to error: {e}")

    if not all_zstacks:
        print("no valid zstack found")
        return

    data = np.stack(all_zstacks)  # shape: [T, Z, Y, X]

    filename = os.path.basename(directory)
    base, ext = os.path.splitext(filename)
    if not ext:
        ext = ".tif"

    base_dir = filedialog.askdirectory(title="Select output base folder")
    folder_path = os.path.join(base_dir, base)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Ensured folder exists: {folder_path}")

    save_path = os.path.join(folder_path, f"{base}_TZYX{ext}")
    try:
        tifffile.imwrite(save_path,
                         data,  # Flatten t and z
                         bigtiff=True,
                         photometric='minisblack',
                         compression=None,
                         imagej=True,
                         metadata={'axes': 'TZYX'})
        print(f"saved merged file to : {save_path}")

    except Exception as e:
        print(f"Save failed: {e}")


def read_tif_files_split_by_z(directory, zstack_len):
    files = sorted(glob.glob(os.path.join(directory, "*.tif")))
    z_slices = [[] for _ in range(zstack_len)]

    for file in files:
        print(f"processing: {file}")
        try:
            with tifffile.TiffFile(file) as tif:
                if len(tif.pages) < zstack_len:
                    print(f"Skipping {file}: only {len(tif.pages)} pages (expected {zstack_len})")
                    continue
                for i in range(zstack_len):
                    img = tif.pages[i].asarray().astype(np.uint16)
                    z_slices[i].append(img)

        except Exception as e:
            print(f"Skipping {file} due to error: {e}")


    filename = os.path.basename(directory)
    base, ext = os.path.splitext(filename)
    if not ext:
        ext = ".tif"

    base_dir = filedialog.askdirectory(title="Select output base folder")
    folder_path = os.path.join(base_dir, base)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Ensured folder exists: {folder_path}")

    for z in range(zstack_len):
        zstack = np.stack(z_slices[z])
        out_path = os.path.join(folder_path, f"{base}_Z{z}.tif")
        tifffile.imwrite(out_path, zstack, bigtiff=True, photometric='minisblack', compression=None)
        print(f"Saved Z{z} file to :{folder_path}")






def z_project_per_file(directory):
    files = sorted(glob.glob(os.path.join(directory, "*.tif")))
    projections = []

    for file in files:
        print(f"Z-projection (avg): {file}")

        try:
            with tifffile.TiffFile(file) as tif:
                stack = np.stack([page.asarray().astype(np.uint16) for page in tif.pages])
                proj = np.mean(stack, axis=0).astype(np.uint16)
                projections.append(proj)

        except Exception as e:
            print(f"skipping {file} due to error: {e}")

    if not projections:
        print("no valid projections generated")
        return

    data = np.stack(projections)  # shape: [T, Y, X]

    filename = os.path.basename(directory)
    base, ext = os.path.splitext(filename)
    if not ext:
        ext = ".tif"

    base_dir = filedialog.askdirectory(title="Select output base folder")
    folder_path = os.path.join(base_dir, base)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Ensured folder exists: {folder_path}")

    save_path = os.path.join(folder_path, f"{base}_zproj{ext}")

    try:
        tifffile.imwrite(save_path,
                         data,
                         bigtiff=True,
                         photometric='minisblack',
                         compression=None)

        print(f"Saved average Z-projection time series {save_path}")

    except Exception as e:
        print(f"Save failed: {e}")


        