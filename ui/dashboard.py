from rich.panel import Panel

class StatsDisplay:
    def __init__(self, monitor):
        self.monitor = monitor
        self.active_component = "Initializing"

    def __rich__(self):
        snapshot = self.monitor.get_latest_snapshot()
        if not snapshot:
            return Panel("Initializing sensors...", title="System Stats", border_style="dim")
        
        content = ""
        if self.active_component == "CPU":
            c = snapshot['cpu']
            content = f"Usage: [bold cyan]{c['usage']}%[/] | Clock: [bold yellow]{c['frequency']:.0f} MHz[/] | Temp: [bold red]{c['temp']:.1f}°C[/]"
        elif self.active_component == "MEMORY":
            m = snapshot['memory']
            content = f"Usage: [bold magenta]{m['usage']}%[/] | Used: {m['used']:.0f} MB / Available: {m['available']:.0f} MB"
        elif self.active_component == "DISK":
            d = snapshot['disk']
            content = f"Read: [bold green]{d['read_speed']/(1024**2):.2f} MB/s[/] | Write: [bold green]{d['write_speed']/(1024**2):.2f} MB/s[/]"
        elif self.active_component == "GPU":
            g = snapshot['gpu'][0] if snapshot['gpu'] else {"usage":0, "temp":0, "vram_used":0}
            content = f"Usage: [bold green]{g['usage']}%[/] | Temp: [bold red]{g['temp']}°C[/] | VRAM: {g['vram_used']:.0f} MB"
        else:
            content = "Waiting for benchmark to start..."
        
        return Panel(content, title=f"📊 {self.active_component} Real-time Monitoring", border_style="bright_blue", expand=False)
