from tkinter import filedialog, messagebox, simpledialog
import subprocess
import napari
import tifffile
import numpy as np
import os
from PyQt5.QtWidgets import QApplication
import glob

def preview_stack(stack, downsample_factor = None):
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    viewer = napari.Viewer()

    name = f'Downsampled (ds{downsample_factor})' if downsample_factor else ('Preview'
                                                                             '')
    viewer.add_image(stack,
                     name = name,
                     colormap = 'gray',
                     scale = [1] * stack.ndim,
                     blending = 'additive',
                     rendering = 'mip',
                     cache=True,
                     axis_labels = ['t', 'y', 'x'] if stack.ndim == 3 else ['t', 'z', 'y', 'x'])

    viewer.dims.current_step = (0,) * stack.ndim  # Set initial step to 0 for all dimensions
    viewer.window.qt_viewer.dims.play()(axis = 0, interval = 10)
    napari.run()


def downsample_tiff(file):
    downsample_factor = simpledialog.askinteger("Downsample factor", "Average every how many frames?",
                                                minvalue=1, initialvalue=5)
    try:
        with tifffile.TiffFile(file) as tif:
            data = tif.asarray()

    except Exception as e:
        print("Error", f"Failed to read TIFF file {file}: {e}")
        return

    if data.ndim != 3:
        print("Error", "Expected a 3D TIFF (T, Y, X)")
        return

    print(f"[INFO] Downsampling {file}")

    num_frames = data.shape[0]
    downsample_frames = []

    for i in range(0, num_frames, downsample_factor):
        end_idx = min(i + downsample_factor, num_frames)
        frame_group = data[i:end_idx]

        averaged_frame = np.mean(frame_group, axis=0)
        downsample_frames.append(averaged_frame)

    downsample_frames = np.stack(downsample_frames, axis = 0)

    output_dir = filedialog.askdirectory(title=f"Select Output Folder for downsampled File {file}")

    if not output_dir:
        print("[INFO] No output directory selected")
        return

    filename = os.path.basename(file)
    name, ext = os.path.splitext(filename)
    save_path = os.path.join(output_dir, f"{name}_DS{downsample_factor}{ext}")

    tifffile.imwrite(save_path, downsample_frames, bigtiff=True, photometric='minisblack', compression=None)

    print("Success", f"All DS files saved to: :\n{output_dir}")



    # def open_in_imagej(output_path):
    #     fiji_path = r"C:\Users\imageanalysis\Documents\Fiji.app\ImageJ-win64.exe"
    #
    #     if not os.path.exists(fiji_path):
    #         raise FileNotFoundError("Fiji.app not found")
    #
    #     subprocess.run([fiji_path, output_path])
    #
    # open_in_imagej(output_path)