import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress INFO, WARNING, and ERROR messages
import tifffile
import glob
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from compiler import read_tif_files_merge_z_and_t, read_tif_files_split_by_z, z_project_per_file
from motion_correction_2D import run_2D_motion_correction
from motion_correction_3D import run_3D_motion_correction
from downsampler import downsample_tiff



def run_selected_operation():
    main_mode = mode_var.get()
    sub_mode = sub_mode_var.get()

    dropped_items = listbox.get(0, tk.END)
    if not dropped_items:
        print("Error", "Please drop folders or .tif files to process")
        return

    for item in dropped_items:
        print(f"[INFO] Processing Folder: {item}")
        if os.path.isdir(item):
            tif_files = sorted(glob.glob(os.path.join(item, "*.tif")))
            print(f'{tif_files[0:10]}...')  # Show first 10 files for brevity
        elif item.lower().endswith('.tif'):
            tif_files = [item]
        else:
            print(f"[ERROR] Unsupported file type: {item}")
            continue

        if not tif_files:
            print(f"[ERROR] No Tiff files found in {item}")
            continue

        ## Compile Mode
        if main_mode == "compile":
            try:
                with tifffile.TiffFile(tif_files[0]) as tif:
                    zstack_len = len(tif.pages)
                print(f"[INFO] {tif_files} Detected Z-stack Length: {zstack_len}")
            except Exception as e:
                print(f"Error: Failed to read Tiff Files in {tif_files}: {e}")
                continue

            if sub_mode == "merge":
                read_tif_files_merge_z_and_t(tif_files, zstack_len)
            elif sub_mode == "split":
                read_tif_files_split_by_z(tif_files, zstack_len)
            elif sub_mode == "zproj":
                z_project_per_file(tif_files)
            else:
                print(f"Error:Invalid sub-mode selected")

        ## Motion Correction Mode
        elif main_mode == "motion":
            is_nonrigid = sub_sub_mode_var.get() == "nonrigid"
            for file in tif_files:
                print(f"[INFO] Processing file: {file}")

                if sub_mode == "2D":
                    run_2D_motion_correction(file, is_nonrigid)
                elif sub_mode == "3D":
                    run_3D_motion_correction(file, is_nonrigid)
                print(f"[INFO] Motion correction completed for {file}")

        ## Downsample Mode
        elif main_mode == "downsample":
            for file in tif_files:
                print(f"[INFO] Processing Item: {file}")
                downsample_tiff(file)

    root.destroy()

def drop(event):
    paths = event.data.strip().split()
    for path in paths:
        cleaned = path.strip("{}")
        if cleaned not in listbox.get(0, tk.END):
            listbox.insert(tk.END, cleaned)

def main():
    global root, mode_var, sub_mode_var, sub_sub_mode_var, listbox

    root = TkinterDnD.Tk()
    root.title("2P PreProcessor")
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.geometry("400x600")

    mode_var = tk.StringVar(value="compile")
    sub_mode_var = tk.StringVar(value="merge")
    sub_sub_mode_var = tk.StringVar(value="rigid")


    #Rest of UI
    tk.Label(root, text="Choose processing mode:").pack(pady=10)
    tk.Radiobutton(root, text="Compile Tiff", variable=mode_var, value="compile").pack(anchor='w',padx=20)
    tk.Radiobutton(root, text="Motion Correction)", variable=mode_var, value="motion").pack(anchor='w', padx=20)
    tk.Radiobutton(root, text="Downsample", variable=mode_var, value="downsample").pack(anchor='w',padx=20)

    listbox = tk.Listbox(root, width=60, height=15, selectmode=tk.SINGLE)
    listbox.drop_target_register(DND_FILES)
    listbox.dnd_bind('<<Drop>>', drop)

    sub_frame = tk.Frame(root)
    tk.Label(sub_frame, text="Select compiling operation:").pack(pady=10)
    tk.Radiobutton(sub_frame, text="Merge All Tiffs (T x Z x Y x X)", variable=sub_mode_var, value="merge").pack(anchor='w', padx=20)
    tk.Radiobutton(sub_frame, text="Split Tiffs by Z (Z*T x Y x X)", variable=sub_mode_var, value="split").pack(anchor='w', padx=20)
    tk.Radiobutton(sub_frame, text="Z-Project Tiffs ([Z]T x Y x X)", variable=sub_mode_var, value="zproj").pack(anchor='w', padx=20)

    sub_motion_frame = tk.Frame(root)
    tk.Label(sub_motion_frame, text="Select Motion Correction").pack(pady=10)
    tk.Radiobutton(sub_motion_frame, text="2D Motion Correction (CaImAn)", variable=sub_mode_var, value="2D").pack(anchor='w', padx=20)
    tk.Radiobutton(sub_motion_frame, text="3D Motion Correction (CaImAn)", variable=sub_mode_var, value="3D").pack(anchor='w', padx=20)

    motion_type_frame = tk.Frame(root)
    tk.Label(motion_type_frame, text="Select motion correction type:").pack(pady=10)
    tk.Radiobutton(motion_type_frame, text="Rigid", variable=sub_sub_mode_var, value="rigid").pack(anchor='w', padx=20)
    tk.Radiobutton(motion_type_frame, text="Non-Rigid", variable=sub_sub_mode_var, value="nonrigid").pack(anchor='w', padx=20)

    def update_visibility(*args):
        sub_frame.pack_forget()
        sub_motion_frame.pack_forget()
        motion_type_frame.pack_forget()
        listbox.pack_forget()

        if mode_var.get() == "compile":
            sub_frame.pack()
            listbox.pack(pady=10)

        elif mode_var.get() == "motion":
            sub_motion_frame.pack()
            motion_type_frame.pack()
            listbox.pack(pady=10)

        elif mode_var.get() == "downsample":
            listbox.pack(pady=10)


    mode_var.trace_add("write", update_visibility)
    update_visibility()
    tk.Button(root, text="Start Processing", command=run_selected_operation, bg="#FF6EC7", fg="white", pady=5).pack(pady=20)



    root.mainloop()



if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()

