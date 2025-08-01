import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Suppress INFO, WARNING, and ERROR messages
import tifffile
import glob
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from compiler import read_tif_files_merge_z_and_t, read_tif_files_split_by_z, z_project_per_file
from motion_correction_2D import run_motion_correction_array
from motion_correction_3D import run_3D_motion_correction_array
from downsampler import downsample_tiff



def run_selected_operation():
    main_mode = mode_var.get()
    sub_mode = sub_mode_var.get()


    if main_mode == "compile":
        folder_list = listbox.get(0, tk.END)
        if not folder_list:
            messagebox.showerror("Error", "Please drop folders to process")
            return

        for folder in folder_list:
            print(f"[INFO] Processing Folder: {folder}")

        for directory in folder_list:
            files = sorted(glob.glob(os.path.join(directory, "*.tif")))

            try:
                with tifffile.TiffFile(files[0]) as tif:
                    zstack_len = len(tif.pages)
                print(f"[INFO] {directory} Detected Z-stack Length: {zstack_len}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read Tiff Files in {directory}: {e}")
                continue

            if sub_mode == "merge":
                read_tif_files_merge_z_and_t(directory, zstack_len)
            elif sub_mode == "split":
                read_tif_files_split_by_z(directory, zstack_len)
            elif sub_mode == "zproj":
                z_project_per_file(directory)
            else:
                messagebox.showerror("Error", "Invalid sub-mode selected")

    elif main_mode == "motion":

        folder_list = listbox.get(0, tk.END)
        if not folder_list:
            print("Error", "Please drop folders to process")
            return

        for folder in folder_list:
            print(f"[INFO] Processing Folder: {folder}")

        for files in folder_list:
            tif_file = sorted(glob.glob(os.path.join(files, "*.tif")))
            if not tif_file:
                print("Error", "No .tif files found in directory.")
                continue

            for file in tif_file:
                print(f"[INFO] Processing file: {file}")

                if sub_mode == "2D":
                    is_nonrigid = (sub_sub_mode_var.get() == "nonrigid")
                    run_motion_correction_array(file, is_nonrigid)

                elif sub_mode == "3D":
                    is_nonrigid = (sub_sub_mode_var.get() == "nonrigid")
                    run_3D_motion_correction_array(file, is_nonrigid)
                print(f"[INFO] Motion correction completed for {file}")


    elif main_mode == "downsample":
        folder_list = listbox.get(0, tk.END)
        if not folder_list:
            print("Error", "Please drop folders to process")
            return

        for folder in folder_list:
            print(f"[INFO] Processing Folder: {folder}")

        for files in folder_list:
            tif_file = sorted(glob.glob(os.path.join(files, "*.tif")))
            if not tif_file:
                print("Error", "No .tif files found in directory.")
                continue

            for file in tif_file:
                print(f"[INFO] Processing File: {file}")
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
    tk.Radiobutton(sub_motion_frame, text="2D Motion Correction", variable=sub_mode_var, value="2D").pack(anchor='w', padx=20)
    tk.Radiobutton(sub_motion_frame, text="3D Motion Correction", variable=sub_mode_var, value="3D").pack(anchor='w', padx=20)

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

