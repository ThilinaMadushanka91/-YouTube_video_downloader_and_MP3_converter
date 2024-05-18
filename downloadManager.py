import math
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pytube import YouTube
from pytube.exceptions import PytubeError
import threading
import os
import requests
import time

class DownloadManager:
    def __init__(self, root):
        self.root = root
        self.download_thread = None
        self.max_size = 0
        self.downloaded_size = 0
        self.start_time = 0
        self.average_speed = 0.0 
        self.cancel_download_flag = False
        self.pause_download_flag = False

    def download_video(self):
        url = self.url_entry.get()
        save_path = self.save_path_entry.get()

        if not url and not save_path:
            messagebox.showerror("Error", "URL and save path are empty.")
            return
        elif not url:
            messagebox.showerror("Error", "URL is empty.")
            return
        elif not save_path:
            messagebox.showerror("Error", "Save path is empty.")
            return

        try:
            self.yt = YouTube(url)
            self.cancel_download_flag = False
            self.pause_download_flag = False
            self.start_time = time.time()
            
            # Display file size
            self.max_size = self.yt.streams.get_highest_resolution().filesize
            self.file_size_label.config(text=f"File Size: {self.convert_file_size(self.max_size)}")
            
            self.download_thread = threading.Thread(target=self.start_download, args=(save_path,))
            self.download_thread.start()
        except PytubeError as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def start_download(self, save_path):
        try:
            video = self.yt.streams.get_highest_resolution()

            if video is None:
                messagebox.showerror("Error", "No suitable video stream found.")
                return

            self.max_size = video.filesize
            self.progress_bar['maximum'] = self.max_size
            
            # Generate a valid filename
            file_name = self.yt.title + '.mp4'
            file_name = "".join(c if c.isalnum() or c in ['_', '.'] else '_' for c in file_name)
            
            with requests.get(video.url, stream=True) as r:
                with open(os.path.join(save_path, file_name), 'wb') as f:
                    chunk_size = 1024 * 1024 
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            while self.pause_download_flag:
                                time.sleep(0.1)
                            f.write(chunk)
                            self.downloaded_size += len(chunk)
                            self.progress_bar['value'] = self.downloaded_size
                            remaining_size = self.max_size - self.downloaded_size
                            self.update_remaining_time(remaining_size)
                            self.update_remaining_size(remaining_size)
                            self.update_download_speed(len(chunk))

                        if self.cancel_download_flag:
                            messagebox.showinfo("Cancelled", "Download cancelled.")
                            return

            messagebox.showinfo("Success", "Video downloaded successfully!")
            self.clear_feilds()
            self.download_thread = None
            # shutil.rmtree(video.url)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
    def cancel_download(self):
        self.cancel_download_flag = True

    def pause_resume_download(self):
        self.pause_download_flag = not self.pause_download_flag
        if self.pause_download_flag:
            self.pause_start_button.config(text="Start")
        else:
            self.pause_start_button.config(text="Pause")

    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, path)

    def update_remaining_time(self, remaining_size):
        # elapsed_time = time.time() - self.start_time
        if self.average_speed is not None and self.average_speed > 0:
            remaining_time = remaining_size / self.average_speed
            remaining_hours = int(remaining_time // 3600)
            remaining_minutes = int((remaining_time % 3600) // 60)
            remaining_seconds = int(remaining_time % 60)
            remaining_time_str = f"{remaining_hours:02d}:{remaining_minutes:02d}:{remaining_seconds:02d}"
            self.remaining_time_label.config(text=f"Remaining Time: {remaining_time_str}")
            
    def update_remaining_size(self, remaining_size):
        remaining_size_str = self.convert_file_size(remaining_size)
        self.remaining_size_label.config(text=f"Remaining Size: {remaining_size_str}")
            
    def update_download_speed(self, chunk_size):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time > 0:
            current_speed = chunk_size / elapsed_time
            self.average_speed = (self.average_speed + current_speed) / 2
            download_speed_str = f"{self.average_speed / 1024:.2f} KB/s"
            self.download_speed_label.config(text=f"Download Speed: {download_speed_str}")
            
    def convert_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    
    def clear_feilds(self):
        self.url_entry.delete(0, 'end')
        self.save_path_entry.delete(0, 'end')

    def create_gui(self):
        # Download Tab
        url_label = tk.Label(self.root, text="Enter YouTube URL:", font=("Helvetica", 12), justify="left", anchor="w")
        url_label.grid(row=0, column=0, padx=10, pady=20, sticky="w")

        self.url_entry = tk.Entry(self.root, width=50, font=("Helvetica", 12), justify="left")
        self.url_entry.grid(row=0, column=1, padx=10, pady=20)

        download_button = tk.Button(self.root, text="Download", command=self.download_video, font=("Arial", 10),
                                    bg="lightblue", fg="black", relief="raised", borderwidth=2, width=10)
        download_button.grid(row=0, column=2, padx=10, pady=20)

        self.pause_start_button = tk.Button(self.root, text="Pause", command=self.pause_resume_download,
                                            font=("Arial", 10), bg="lightblue", fg="black", relief="raised",
                                            borderwidth=2, width=10)
        self.pause_start_button.grid(row=0, column=3, padx=10, pady=20)

        cancel_button = tk.Button(self.root, text="Cancel", command=self.cancel_download, font=("Arial", 10),
                                  bg="lightblue", fg="black", relief="raised", borderwidth=2, width=10)
        cancel_button.grid(row=0, column=4, padx=10, pady=20)

        save_path_label = tk.Label(self.root, text="Select save path:", font=("Helvetica", 12), justify="left",
                                   anchor="w")
        save_path_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.save_path_entry = tk.Entry(self.root, width=50, font=("Helvetica", 12), justify="left")
        self.save_path_entry.grid(row=1, column=1, padx=10, pady=10)

        browse_button = tk.Button(self.root, text="Browse", command=self.select_path, font=("Arial", 10),
                                  bg="lightblue", fg="black", relief="raised", borderwidth=2, width=10)
        browse_button.grid(row=1, column=2, padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=950, mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=5, padx=10, pady=30)
        
        self.file_size_label = tk.Label(self.root, text="")
        self.file_size_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.remaining_size_label = tk.Label(self.root, text="")
        self.remaining_size_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.remaining_time_label = tk.Label(self.root, text="")
        self.remaining_time_label.grid(row=3, column=1, columnspan=4, padx=10, pady=5)

        self.download_speed_label = tk.Label(self.root, text="")
        self.download_speed_label.grid(row=3, column=2, columnspan=4, padx=10, pady=5)
        
    def on_close(self):
        if self.download_thread and self.download_thread.is_alive():
            self.cancel_download()
            self.root.after(100, self.on_close)  # Check again after 100ms
        else:
            self.root.destroy()

# Main script to run the application
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    root.title("YouTube Video Downloader")

    app = DownloadManager(root)
    app.create_gui()

    root.mainloop()
