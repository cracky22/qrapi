import tkinter as tk
from tkcalendar import DateEntry
import requests
from datetime import datetime
import qrcode
from PIL import Image, ImageTk
import os
from tkinter import messagebox, filedialog

class LinkManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Link Manager")
        self.root.geometry("600x500")

        self.api_url = "https://cracky.ddns.net/services/linkApi.php"

        self.label_url = tk.Label(root, text="URL eingeben:")
        self.label_url.pack(pady=5)
        self.entry_url = tk.Entry(root, width=50)
        self.entry_url.pack(pady=5)

        self.label_expire = tk.Label(root, text="Ablaufdatum wählen:")
        self.label_expire.pack(pady=5)
        self.date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(pady=5)

        self.create_button = tk.Button(root, text="Link erstellen", command=self.create_link)
        self.create_button.pack(pady=10)

        self.result_label = tk.Label(root, text="", wraplength=500)
        self.result_label.pack(pady=5)

        self.qr_label = tk.Label(root)
        self.qr_label.pack(pady=5)

        self.save_button = tk.Button(root, text="QR-Code speichern", command=self.save_qr_code, state=tk.DISABLED)
        self.save_button.pack(pady=5)

        self.qr_image = None

    def create_link(self):
        url = self.entry_url.get()
        expire_date = self.date_entry.get()

        expire = f"{expire_date},23:59"

        try:
            response = requests.get(self.api_url, params={
                'action': 'create',
                'link': url,
                'expire': expire
            })
            response.raise_for_status()
            data = response.json()

            if 'linkID' in data:
                link_id = data['linkID']
                open_url = f"{self.api_url}?action=open&linkID={link_id}"
                self.result_label.config(text=f"Generierter Link: {open_url}\nLink-ID: {link_id}")

                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(open_url)
                qr.make(fit=True)
                self.qr_image = qr.make_image(fill_color="black", back_color="white")

                tk_image = ImageTk.PhotoImage(self.qr_image)
                self.qr_label.config(image=tk_image)
                self.qr_label.image = tk_image
                self.save_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Fehler", data.get('error', 'Unbekannter Fehler'))
        except requests.RequestException as e:
            messagebox.showerror("Fehler", f"API-Aufruf fehlgeschlagen: {str(e)}")

    def save_qr_code(self):
        if self.qr_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                self.qr_image.save(file_path)
                messagebox.showinfo("Erfolg", "QR-Code erfolgreich gespeichert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = LinkManagerApp(root)
    root.mainloop()