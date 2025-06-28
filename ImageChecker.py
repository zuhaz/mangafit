import requests
from PIL import Image
from io import BytesIO
import tkinter as tk
from tkinter import ttk

def fetch_and_show_image():
    image_url = url_entry.get()
    referer = referer_entry.get()

    try:
        headers = {
            'Referer': referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(image_url, headers=headers)
        response.raise_for_status() 

        image = Image.open(BytesIO(response.content))
        
        image.show()
        return image

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

root = tk.Tk()
root.title("Image Fetcher with Referer")
root.geometry("400x200")

url_label = ttk.Label(root, text="Image URL:")
url_label.pack(pady=5)

url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

referer_label = ttk.Label(root, text="Referer:")
referer_label.pack(pady=5)

referer_entry = ttk.Entry(root, width=50)
referer_entry.pack(pady=5)

fetch_button = ttk.Button(root, text="Fetch Image", command=fetch_and_show_image)
fetch_button.pack(pady=10)

result_label = ttk.Label(root, text="")
result_label.pack(pady=5)

root.mainloop()