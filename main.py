import tkinter as tk
from tkinter import ttk
from downloadManager import DownloadManager
from convertManager import ConvertManager


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    root.title("YouTube Downloader and Converter")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    download_tab = ttk.Frame(notebook)
    convert_tab = ttk.Frame(notebook)

    notebook.add(download_tab, text='Download Video')
    notebook.add(convert_tab, text='Convert to MP3')

    download_manager = DownloadManager(download_tab)
    download_manager.create_gui()

    convert_manager = ConvertManager(convert_tab)
    convert_manager.create_gui()

    root.mainloop()
