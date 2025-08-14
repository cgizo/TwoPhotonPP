import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress INFO, WARNING, and ERROR messages
import glob

from tkinter import filedialog, messagebox
import tifffile
import numpy as np

import sys

try:
    cv2.setNumThreads(0)
except:
    pass

from caiman.base.movies import load
import caiman as cm
from caiman.motion_correction import MotionCorrect, motion_correction_piecewise
from caiman.source_extraction.cnmf import params as params


def run_2D_motion_correction(data_path, is_nonrigid=False):

    """
    Run motion correction directly on a [T, Y, X] NumPy array.

    Parameters:
        data : np.ndarray
            3D time-series image stack (shape: [T, Y, X])
        is_nonrigid : bool
            True = non-rigid (piecewise), False = rigid

    Returns:
        corrected : np.ndarray
            Motion-corrected array with same shape
    """


    # Setup motion correction parameters
    parameter_dict={
        'data': {
            'fnames': data_path
        },
        'motion': {
            'pw_rigid': is_nonrigid,
            'max_shifts': (25, 25),
            'strides': (32, 32),
            'overlaps': (32, 32),
            'max_deviation_rigid': 3,
            'border_nan': 'copy'
        }
    }


    parameters = params.CNMFParams(params_dict=parameter_dict)


    if 'cluster' in locals():
        print('Closing Previous Cluster')
        cm.stop_server(dview=cluster)
    print ('setting up cluster')

    _, cluster, n_processes =cm.cluster.setup_cluster(backend='multiprocessing',
                                                    n_processes=20,
                                                    single_thread=False)
    print(f"[INFO] Using {n_processes} processes for motion correction")


    print(f"[INFO] Running {'non-rigid' if is_nonrigid else 'rigid'} motion correction on data ...")





    mc = MotionCorrect(data_path, dview=cluster, **parameters.motion)
    mc.motion_correct(save_movie=False)

    corrected = mc.apply_shifts_movie(fname=data_path)
    print("[INFO] Motion Correction Complete")

    corr_norm = (corrected - corrected.min()) / (corrected.max() - corrected.min())
    corrected_16 = (corr_norm * 65535).astype(np.uint16)

    output_dir = filedialog.askdirectory(title=f"Select Output Folder for Motion Corrected {data_path}")
    if not output_dir:
        print("[INFO] No output directory selected")
        return

    filename = os.path.basename(data_path)
    base, ext = os.path.splitext(filename)
    save_path = os.path.join(output_dir, f"{base}_MC2D{ext}")

    tifffile.imwrite(save_path, corrected_16, bigtiff=True, photometric='minisblack', compression=None)



    cm.stop_server(dview=cluster)
    print(f"Success", f"All Motion corrected files saved to: :\n{output_dir}")
    return corrected


def main():
    #handle command line arguments
    data_path = sys.argv[1]
    is_nonrigid = sys.argv[2].lower() == "nonrigid" if len(sys.argv) > 2 else False
    run_2D_motion_correction(data_path, is_nonrigid)

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()