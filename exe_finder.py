import os
import sys
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ExeFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EXE File Finder")
        self.root.geometry("400x150") # Set a fixed size for the window
        self.root.resizable(False, False) # Make window not resizable

        # --- Get the base path for saving files ---
        # This works correctly whether running as a .py script or a frozen .exe
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle/frozen executable
            self.application_path = os.path.dirname(sys.executable)
        else:
            # If the application is run as a .py script
            self.application_path = os.path.dirname(os.path.abspath(__file__))

        # --- Create GUI Widgets ---
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.scan_button = ttk.Button(
            self.main_frame,
            text="Select Folder & Start Scan",
            command=self.start_scan_thread
        )
        self.scan_button.pack(pady=5)

        self.status_label = ttk.Label(self.main_frame, text="Ready to start.")
        self.status_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            orient="horizontal",
            length=300,
            mode='indeterminate'
        )
        self.progress_bar.pack(pady=10)

    def start_scan_thread(self):
        """Handles the button click, gets the folder, and starts the search in a new thread."""
        folder_to_search = filedialog.askdirectory(title="Select a Folder to Search")

        if not folder_to_search:
            self.status_label.config(text="Scan cancelled. No folder selected.")
            return

        # Disable button and update UI to show work is starting
        self.scan_button.config(state=tk.DISABLED)
        self.status_label.config(text=f"Scanning: {os.path.basename(folder_to_search)}...")
        self.progress_bar.start(10) # Start the indeterminate progress bar

        # Run the actual file search in a separate thread to prevent the GUI from freezing
        scan_thread = threading.Thread(
            target=self.perform_scan,
            args=(folder_to_search,),
            daemon=True
        )
        scan_thread.start()

    def perform_scan(self, folder_path):
        """This function runs in the background to find files."""
        exe_files_found = []
        permission_errors = []

        for root, dirs, files in os.walk(folder_path, topdown=True, onerror=None):
            # Check for permission errors on directories
            # A bit of a workaround since onerror doesn't give us the path
            try:
                # This call will fail if we don't have list permissions
                os.listdir(root)
            except PermissionError:
                permission_errors.append(f"Directory: {root} (Could not access)")
                # Clear the 'dirs' list to prevent os.walk from trying to go deeper
                dirs[:] = [] 
                continue

            for file_name in files:
                if file_name.lower().endswith(".exe"):
                    try:
                        full_path = os.path.join(root, file_name)
                        exe_files_found.append(full_path)
                    except Exception as e:
                        # This is a fallback for other potential errors
                        permission_errors.append(f"File: {file_name} in {root} (Error: {e})")

        # When the scan is done, schedule the finalization task on the main GUI thread
        self.root.after(0, self.finalize_scan, folder_path, exe_files_found, permission_errors)

    def finalize_scan(self, folder_path, exe_list, error_list):
        """This function runs on the main thread to update the UI and write files."""
        # Stop the progress bar and reset the UI
        self.progress_bar.stop()
        self.status_label.config(text="Scan complete. Saving results...")

        # --- Write the results file ---
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"file_list_{timestamp}.txt"
        output_filepath = os.path.join(self.application_path, output_filename)

        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Search Results for folder: {folder_path}\n")
                f.write(f"Scan performed on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                if exe_list:
                    for path in exe_list:
                        f.write(path + "\n")
                else:
                    f.write("No .exe files were found in the specified directory.\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write results file: {e}")

        # --- Write the error log file, ONLY if there were errors ---
        if error_list:
            error_filename = f"error_log_{timestamp}.txt"
            error_filepath = os.path.join(self.application_path, error_filename)
            try:
                with open(error_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"The following folders or files could not be accessed due to permission errors:\n")
                    f.write("=" * 50 + "\n\n")
                    for error in error_list:
                        f.write(error + "\n")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write error log: {e}")

        # --- Final success message for the user ---
        summary_message = f"Found {len(exe_list)} .exe files.\n\n"
        summary_message += f"Results saved to:\n{output_filepath}"
        if error_list:
            summary_message += f"\n\nEncountered {len(error_list)} permission errors.\nSee error_log_{timestamp}.txt for details."
        
        messagebox.showinfo("Scan Complete", summary_message)

        # Reset the UI for the next scan
        self.status_label.config(text="Ready for next scan.")
        self.scan_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    app_root = tk.Tk()
    app = ExeFinderApp(app_root)
    app_root.mainloop()
