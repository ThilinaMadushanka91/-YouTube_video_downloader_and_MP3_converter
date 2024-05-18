import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from pytube import YouTube
import threading
import os
import shutil
import tempfile

class ConvertManager:
    def __init__(self, root):
        self.root = root
        self.convert_thread = None
        self.cancel_convert_flag = False

    def select_save_path(self):
        save_path = filedialog.askdirectory()
        if save_path:
            self.convert_save_path_entry.delete(0, tk.END)
            self.convert_save_path_entry.insert(0, save_path)

    def sanitize_filename(self, filename):
        # Replace invalid characters with underscore
        return "".join(c if c.isalnum() or c in ' .-_()' else '_' for c in filename)

    def convert_to_mp3(self):
        url = self.convert_url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        if self.convert_thread and self.convert_thread.is_alive():
            messagebox.showinfo("Info", "Conversion is already in progress.")
            return

        self.cancel_convert_flag = False
        self.convert_thread = threading.Thread(target=self._convert_to_mp3_thread, args=(url,))
        self.convert_thread.start()

    def cancel_convert(self):
        self.cancel_convert_flag = True

    def _convert_to_mp3_thread(self, url):
        try:
            tmp_dir = tempfile.mkdtemp()
            yt = YouTube(url, on_progress_callback=self._on_progress)
            stream = yt.streams.filter(only_audio=True).first()
            video_path = os.path.join(tmp_dir, "temp_video.mp4")
            stream.download(output_path=tmp_dir, filename="temp_video.mp4")

            if self.cancel_convert_flag:
                shutil.rmtree(tmp_dir)
                self.convert_progress_bar["value"] = 0
                self.convert_thread = None
                return

            sanitized_title = self.sanitize_filename(yt.title)
            mp3_path = os.path.join(tmp_dir, f"{sanitized_title}.mp3")

            save_path = self.convert_save_path_entry.get()
            if not save_path:
                messagebox.showerror("Error", "Please select a save path.")
                shutil.rmtree(tmp_dir)
                return

            final_mp3_path = os.path.join(save_path, f"{sanitized_title}.mp3")
            os.rename(video_path, mp3_path)
            shutil.move(mp3_path, final_mp3_path)
            shutil.rmtree(tmp_dir)

            messagebox.showinfo("Success", "Video converted to MP3 successfully!")
            self._clear_feilds()
            self.convert_thread = None
        except Exception as e:
            if not self.cancel_convert_flag:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            else:
                messagebox.showinfo("Info", "Conversion cancelled.")
        finally:
            self.convert_progress_bar["value"] = 0
            self.convert_thread = None

    def _on_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress = (bytes_downloaded / total_size) * 100
        self._update_progress_bar(progress, self.convert_progress_bar)

    def _update_progress_bar(self, progress, progress_bar):
        progress_bar["value"] = progress
        self.root.update_idletasks()
        
    def _clear_feilds(self):
        self.convert_url_entry.delete(0, 'end')
        self.convert_save_path_entry.delete(0, 'end')

    def create_gui(self):
        convert_label = tk.Label(self.root, text="Enter YouTube URL to convert to MP3:", font=("Helvetica", 12))
        convert_label.grid(row=0, column=0, padx=10, pady=20, sticky="w")

        self.convert_url_entry = tk.Entry(self.root, width=50, font=("Helvetica", 10))
        self.convert_url_entry.grid(row=0, column=1, padx=10, pady=20)

        convert_button = tk.Button(self.root, text="Convert to MP3", font=("Arial", 10), bg="lightblue", fg="black",
                                   relief="raised", borderwidth=2, width=15, command=self.convert_to_mp3)
        convert_button.grid(row=0, column=2, padx=10, pady=20)

        cancel_button = tk.Button(self.root, text="Cancel", command=self.cancel_convert, font=("Arial", 10),
                                  bg="lightblue", fg="black", relief="raised", borderwidth=2, width=10)
        cancel_button.grid(row=0, column=4, padx=10, pady=20)

        convert_save_path_label = tk.Label(self.root, text="Select save path:", font=("Helvetica", 12), justify="left",
                                           anchor="w")
        convert_save_path_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.convert_save_path_entry = tk.Entry(self.root, width=50, font=("Helvetica", 10), justify="left")
        self.convert_save_path_entry.grid(row=1, column=1, padx=10, pady=10)

        convert_browse_button = tk.Button(self.root, text="Save mp3", command=self.select_save_path,
                                          font=("Arial", 10), bg="lightblue", fg="black", relief="raised",
                                          borderwidth=2, width=10)
        convert_browse_button.grid(row=1, column=2, padx=10, pady=10)

        self.convert_progress_bar = ttk.Progressbar(self.root, orient="horizontal", length=1000, mode="determinate")
        self.convert_progress_bar.grid(row=2, column=0, columnspan=5, padx=10, pady=30)

        self.remaining_time_label = tk.Label(self.root, text="")
        self.remaining_time_label.grid(row=3, column=1, columnspan=4, padx=10, pady=5)
        
    def on_close(self):
        if self.convert_thread and self.convert_thread.is_alive():
            self.cancel_convert()
            self.root.after(100, self.on_close)
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    root.title("YouTube Video Converter")

    app = ConvertManager(root)
    app.create_gui()

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
