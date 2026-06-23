import logging
import threading
import time
from typing import Optional, Tuple, Dict, Any
import tkinter as tk
from pypresence import Presence
from plugins import edsm
from config import appname, config
import myNotebook as nb

# locals
from settings import presence_settings
import configuration as const

"""TODO
    - SET STATUS SYSTEM AT STARTUP
"""

class This:
    """Holds globals."""

    def __init__(self):
        # Discord Activity Holders
        self.activity_state: str = ''
        self.activity_details: str = ''
        self.activity_buttons: list = []

        self.RPC = None
        self.DISCORD_THREAD: None
        self.DEFAULT_APP_ID: str = const.dis_application_id
        self.NAME: str = const.plugin_name
        self.VERSION: str = const.plugin_version
        self.SOURCE_OPTIONS = ['Inara', 'EDSM', 'Spansh']
        self.PADX = 10
        self.BUTTONX = 12  # indent Checkbuttons and Radiobuttons
        self.LISTX = 25  # indent listed items
        self.PADY = 1  # close spacing
        self.BOXY = 2  # box spacing
        self.SEPY = 10  # separator line spacing

this = This()

# ============================================================================
# LOGGING SETUP
# ============================================================================
logger = logging.getLogger(f'{appname}.{this.NAME}')

if not logger.hasHandlers():
    level = logging.INFO
    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(
        f'%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s'
    )
    logger_formatter.default_time_format = '%Y-%m-%d %H:%M:%S'
    logger_formatter.default_msec_format = '%s.%03d'
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)

# ============================================================================
# Load this plugin into EDMarketConnector.
#
# Args:
#     plugin_dir: The directory that your plugin is located in.
#
# Returns:
#     str: The name you want to be used for your plugin internally
# ============================================================================
def plugin_start3(plugin_dir: str) -> str:

    this.DISCORD_THREAD = threading.Thread(target=init_discord)
    this.DISCORD_THREAD.daemon = True
    this.DISCORD_THREAD.start()

    logger.info(f"Plugin loaded from: {plugin_dir}")
    logger.info(f"Plugin version: {this.VERSION}")
    
    return "Elite Presence"

# ============================================================================
# Return a TK Frame for adding to the EDMarketConnector settings dialog.
#
# Args:
#     parent: Root Notebook object the preferences window uses
#     cmdr: The current commander
#     is_beta: If the game is currently a beta version
#
# Returns:
#     Optional[tk.Frame]: The preferences frame for this plugin
# ============================================================================
def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:

    presence_settings.discord_app_id = tk.StringVar(value=config.get_str(key='elitepresence_discord_app_id', default=this.DEFAULT_APP_ID))
    presence_settings.system_url_provider = tk.StringVar(value=config.get_str(key='elitepresence_system_url_provider', default='EDSM'))
    presence_settings.station_url_provider = tk.StringVar(value=config.get_str(key='elitepresence_station_url_provider', default='EDSM'))

    frame = nb.Frame(parent)
    nb.Label(frame, text="Elite Presence Customization").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=this.PADX, pady=this.PADY)

    nb.Label(frame, text="Discord App ID:").grid(row=1, column=0, sticky=tk.W, padx=this.PADX, pady=this.PADY)
    discord_id_entry = nb.EntryMenu(frame, textvariable=presence_settings.discord_app_id, width=20)
    discord_id_entry.grid(row=1, column=1, sticky=tk.EW, padx=this.PADX, pady=this.PADY)

    # Data Source Configuration Section
    nb.Label(frame, text="Url Source Customization").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=this.PADX,
                                                           pady=(15, 5))

    # Primary Source Dropdown
    nb.Label(frame, text="System Url Provider:").grid(row=3, column=0, sticky=tk.W, padx=this.PADX, pady=this.PADY)
    system_provider = nb.OptionMenu(frame, presence_settings.system_url_provider, presence_settings.system_url_provider.get(),*this.SOURCE_OPTIONS)
    system_provider.grid(row=3, column=1, sticky=tk.EW, padx=this.PADX, pady=this.PADY)

    # Secondary Source Dropdown
    nb.Label(frame, text="Station Url Provider:").grid(row=4, column=0, sticky=tk.W, padx=this.PADX, pady=this.PADY)
    station_provider = nb.OptionMenu(frame, presence_settings.station_url_provider, presence_settings.station_url_provider.get(), *this.SOURCE_OPTIONS)
    station_provider.grid(row=4, column=1, sticky=tk.EW, padx=this.PADX, pady=this.PADY)

    return frame

# ============================================================================
# Called when the user dismisses the settings dialog.
# Save settings here.
#
# Args:
#     cmdr: The current commander
#     is_beta: If the game is currently a beta version
# ============================================================================
def prefs_changed(cmdr: str, is_beta: bool) -> None:

    config.set('elitepresence_discord_app_id', presence_settings.discord_app_id.get())
    config.set('elitepresence_system_url_provider', presence_settings.system_url_provider.get())
    config.set('elitepresence_station_url_provider', presence_settings.station_url_provider.get())

# ============================================================================
# EVENT HANDLERS
# ============================================================================
def journal_entry(cmdr: str, is_beta: bool, system: Optional[str], station: Optional[str], entry: Dict[str, Any], state: Dict[str, Any]) -> Optional[str]:
    # Cache local references to avoid repeating 'this.' attribute lookups
    a_state = this.activity_state
    a_details = this.activity_details

    match entry:
        # Combined matching for identical logic paths
        case {"event": "StartUp" | "Location" | "Docked"}:
            a_state = 'In system {system}'.format(system=system)
            a_details = 'Flying in normal space' if station is None else 'Docked at {station}'.format(
                station=station)

        # Nested property matching for 'StartJump'
        case {"event": "StartJump", "JumpType": "Hyperspace"}:
            a_state = 'Jumping'
            a_details = 'Jumping to system {system}'.format(system=entry.get('StarSystem', ''))

        case {"event": "StartJump", "JumpType": "Supercruise"}:
            a_state = 'Jumping'
            a_details = 'Preparing for supercruise'

        case {"event": "SupercruiseEntry" | "FSDJump"}:
            a_state = 'In system {system}'.format(system=system)
            a_details = 'Supercruising'

        case {"event": "SupercruiseExit"}:
            a_state = 'In system {system}'.format(system=system)
            a_details = 'Flying in normal space'

        # Bugfix: Combined original Undocked paths and alternatives into a clean layout
        case {"event": "Undocked" | "DockingCancelled" | "DockingTimeout"}:
            # If standard Undocked logic applies first, handle details change cleanly
            if entry["event"] == "Undocked":
                a_state = 'In system {system}'.format(system=system)
            a_details = 'Flying near {station}'.format(station=entry.get('StationName', station))

        case {"event": "ShutDown"} | {"event": "Music", "MusicTrack": "MainMenu"}:
            a_state = 'Connecting CMDR Interface'
            a_details = ''

        case {"event": "ApproachBody"}:
            planet = entry.get('Body')
            a_details = 'Approaching {body}'.format(body=entry.get('Body'))

        case {"event": "Touchdown", "PlayerControlled": True}:
            a_details = 'Landed on {body}'.format(body=entry.get('Body'))

        # Fixed logic error: your original had nested 'if entry['PlayerControlled']' twice
        case {"event": "Liftoff"}:
            if entry.get('PlayerControlled'):
                a_details = 'Flying around {body}'.format(body=entry.get('Body'))
            else:
                a_details = 'In SRV on {body}, ship in orbit'.format(body=entry.get('Body'))

        case {"event": "LeaveBody"}:
            a_details = 'Supercruising'

        case {"event": "LaunchSRV"}:
            a_details = 'In SRV on {body}'.format(body=entry.get('Body'))

        case {"event": "DockSRV"}:
            a_details = 'Landed on {body}'.format(body=entry.get('Body'))

        case _:
            pass  # Fallback for unhandled Elite Dangerous journal events

    # Only fire updating engine if a structural value actually shifted
    if a_state != this.presence_state or a_details != this.activity_details:
        this.presence_state = a_state
        this.activity_details = a_details
        update_presence()


# ============================================================================
# Handle the latest data from the Status.json file.
#
# This is called when an update to Status.json is detected (typically about once
# a second when in orbital flight).
#
# Args:
#     cmdr: Current commander name
#     is_beta: If the game is currently in beta
#     entry: Data from status.json
#
# Returns:
#     Optional[str]: An error message, or None
# ============================================================================
def dashboard_entry(cmdr: str, is_beta: bool, entry: Dict[str, Any]) -> Optional[str]:

    return None

# ============================================================================
# PLUGIN SHUTDOWN
# - Called when EDMarketConnector is closing.
# - Clean up resources, save state, and stop any running threads here
# ============================================================================
def plugin_stop() -> None:
    logger.info("Plugin shutting down")
    # Add cleanup code here

def init_discord():
    this.RPC = Presence(this.DEFAULT_APP_ID)
    this.RPC.connect()

    this.RPC_THREAD = threading.Thread(target=run_rpc)
    this.RPC_THREAD.daemon = True
    this.RPC_THREAD.start()

    this.RPC.update(state="Connecting CMDR Interface")

    update_presence()

def update_presence():
    if not this.activity_details:
        this.RPC.update(
            state=this.activity_state,
            buttons=this.activity_buttons
        )
    else:
        this.RPC.update(
            state=this.activity_state,
            details=this.activity_details,
            buttons=this.activity_buttons
        )

def clearButton():
    this.RPC.update(buttons=this.activity_buttons.clear())

def run_rpc():
    while True:
        update_presence()
        time.sleep(15)