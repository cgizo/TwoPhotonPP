import napari
from qtpy.QtWidgets import QApplication
from caiman.motion_correction import MotionCorrect
from caiman.source_extraction.cnmf import params as params
from caiman.base.movies import load
import tifffile
import cv2
try:
    cv2.setNumThreads(0)
except:
    pass



def preview_movie_napari(original, corrected):
    """ launch napari viewer
    """
    app = QApplication.instance() or QApplication([])

    viewer = napari.Viewer()

    viewer.add_image(original,
                     name='Original',
                     colormap='gray',
                     scale=[1, 1, 1, 1],
                     blending='additive',
                     rendering='mip',
                     cache=True)

    viewer.add_image(corrected,
                     name='Corrected',
                     colormap='magenta',
                     scale=[1, 1, 1, 1],
                     blending='additive',
                     rendering='mip',
                     cache=True)

    viewer.dims.link_scroll = True
    viewer.dims.order = (0, 1, 2, 3)  # T, X Y, X
    viewer.grid.enabled = True
    napari.run()

def run_3D_motion_correction_array(file_path, is_nonrigid=True):
    """
    Run motion correction directly on a [T, Z, Y, X] NumPy array.

    Parameters:
        data : np.ndarray
            4D time-series image stack (shape: [T, Z, Y, X])
        is_nonrigid : bool
            True = non-rigid (piecewise), False = rigid

    Returns:
        corrected : np.ndarray
            Motion-corrected array with same shape
    """
    print("Starting Motion Correction")

    # Setup motion correction parameters
    motion_params = params.CNMFParams(params_dict={
        'fnames': file_path,
        'pw_rigid': True,
        'max_deviation_rigid': 5,
        'max_shifts': (4, 4, 2),
        'strides': (24, 24, 6),
        'overlaps': (12, 12, 2),
        'is3D': True,
        'border_nan': False

    })

    print(f"[INFO] Running motion correction on file:{file_path}")

    mc = MotionCorrect(file_path, dview=None, **motion_params.get_group('motion'))

    print("MotionCorrect object created.")
    start = time.time()
    mc.motion_correct(save_movie=True)

    print(f"[INFO] Motion correction complete in {time.time() - start:.1f} seconds.")

    corrected_path = mc.fname_tot_els
    corrected = load(corrected_path)

    print("[INFO] Motion Correction Complete")


def start_motion_correction():
    file_path = filedialog.askopenfilename(title="Select Tiff Time Series",
                                           filetypes=[("TIFF files", "*.tif"), ("All Files", "*.*")])

    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected")
        return
    print(F"[INFO] Loading file: {file_path}")

    try:
        movie = load(file_path, is3D=True)  # returns a caiman movie object
        if movie.ndim != 4:
            raise ValueError("Expected 4D time series (T, Z, Y, X)")

        if movie.dtype != np.float32:
            raise(f"[WARNING] converting movie from {movie.dtype} to float32")
            movie = movie.astype(np.float32)

    except Exception as e:
        messagebox.showerror("Error", f"failed to load tiff: {e}")
        return

