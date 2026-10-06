import time
import random
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TwitchViewerBot:
    def __init__(self, master):
        self.master = master
        self.master.title("Twitch View Bot")
        self.master.geometry("600x500")
        self.master.resizable(False, False)
        self.style = ttk.Style(theme="darkly")  # 🌙 Mode sombre moderne

        # 📌 Cadre principal
        self.frame = ttk.Frame(master, padding=20)
        self.frame.pack(fill=BOTH, expand=True)

        # 🔹 Titre
        self.title_label = ttk.Label(self.frame, text="Twitch View Bot", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=10)

        # 🔗 Entrée du lien Twitch
        ttk.Label(self.frame, text="URL du stream Twitch:").pack(anchor=W, pady=2)
        self.stream_entry = ttk.Entry(self.frame, width=50)
        self.stream_entry.pack(pady=5)
        self.stream_entry.insert(0, "https://www.twitch.tv/nom_du_streamer")

        # 👀 Nombre de viewers
        ttk.Label(self.frame, text="Nombre de viewers:").pack(anchor=W, pady=2)
        self.viewer_entry = ttk.Entry(self.frame, width=10)
        self.viewer_entry.pack(pady=5)
        self.viewer_entry.insert(0, "10")

        # 🌍 Proxies optionnels
        ttk.Label(self.frame, text="Proxy (laisser vide pour aléatoire):").pack(anchor=W, pady=2)
        self.proxy_entry = ttk.Entry(self.frame, width=50)
        self.proxy_entry.pack(pady=5)
        self.proxy_entry.insert(0, "")

        # 🕹️ Boutons de contrôle
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)
        self.start_button = ttk.Button(self.button_frame, text="Lancer les bots", bootstyle=SUCCESS, command=self.start_bots)
        self.start_button.pack(side=LEFT, padx=5)
        self.stop_button = ttk.Button(self.button_frame, text="Arrêter les bots", bootstyle=DANGER, command=self.stop_bots, state=DISABLED)
        self.stop_button.pack(side=LEFT, padx=5)

        # 📜 Logs
        ttk.Label(self.frame, text="Logs:").pack(anchor=W, pady=2)
        self.log_area = scrolledtext.ScrolledText(self.frame, height=8, width=70, state=tk.DISABLED, wrap=tk.WORD)
        self.log_area.pack(pady=5)

        # 🔄 Barre de progression
        self.progress = ttk.Progressbar(self.frame, mode="indeterminate", length=300)
        self.progress.pack(pady=5)

        self.bots = []
        self.running = False
        self.twitch_proxies = [
            "185.199.230.3:8080",
            "185.200.122.9:3128",
            "193.107.237.28:8080",
        ]

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.yview(tk.END)

    def start_bots(self):
        try:
            nombre_de_bots = int(self.viewer_entry.get())
            if nombre_de_bots <= 0:
                raise ValueError("Le nombre de viewers doit être supérieur à 0.")
            url_du_stream = self.stream_entry.get().strip()
            if not url_du_stream.startswith("https://www.twitch.tv/"):
                raise ValueError("L'URL du stream Twitch est invalide.")
            proxy = self.proxy_entry.get().strip()
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        self.start_button.config(state=DISABLED)
        self.stop_button.config(state=NORMAL)
        self.running = True
        self.progress.start()
        self.log(f"📢 Démarrage de {nombre_de_bots} bots sur {url_du_stream}...")

        for i in range(nombre_de_bots):
            threading.Thread(target=self.launch_bot, args=(i, url_du_stream, proxy), daemon=True).start()

    def launch_bot(self, bot_id, url, proxy):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if proxy:
            chrome_options.add_argument(f"--proxy-server={proxy}")
        else:
            proxy = random.choice(self.twitch_proxies)
            chrome_options.add_argument(f"--proxy-server={proxy}")
        self.log(f"🔒 Bot {bot_id+1} → Proxy utilisé : {proxy}")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            self.bots.append(driver)
            self.log(f"✅ Bot {bot_id+1} en ligne sur {url}")
            while self.running:
                time.sleep(random.randint(30, 60))
                driver.execute_script("window.scrollBy(0, 100);")
        except Exception as e:
            self.log(f"❌ Bot {bot_id+1} crashé : {str(e)}")
            time.sleep(10)
            self.launch_bot(bot_id, url, proxy)

    def stop_bots(self):
        self.running = False
        self.log("🛑 Fermeture des bots...")
        for driver in self.bots:
            driver.quit()
        self.bots.clear()
        self.start_button.config(state=NORMAL)
        self.stop_button.config(state=DISABLED)
        self.progress.stop()
        self.log("✅ Tous les bots sont arrêtés.")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")  # 🌙 Interface moderne avec mode sombre
    app = TwitchViewerBot(root)
    root.mainloop()
