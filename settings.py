import tkinter as tk

class Settings:
    def __init__(self):
        self.discord_app_id: tk.StringVar | None = None
        self.system_url_provider: tk.StringVar | None = None
        self.station_url_provider: tk.StringVar | None = None

presence_settings = Settings()