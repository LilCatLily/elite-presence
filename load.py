import logging
import os
from typing import Optional, Tuple, Dict, Any
import tkinter as tk

from config import appname, config
from theme import theme
import myNotebook as nb

# ============================================================================
# LOGGING SETUP
# ============================================================================
plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

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
# PLUGIN METADATA
# ============================================================================
__version__ = "0.1.0"
VERSION = "0.1.0"

# ============================================================================
# GLOBAL STATE
# ============================================================================
status_label: Optional[tk.Label] = None
my_setting: Optional[tk.IntVar] = None


# ============================================================================
# PLUGIN STARTUP
# ============================================================================
def plugin_start3(plugin_dir: str) -> str:
    """
    Load this plugin into EDMarketConnector.
    
    Args:
        plugin_dir: The directory that your plugin is located in.
        
    Returns:
        str: The name you want to be used for your plugin internally
    """
    logger.info(f"Plugin loaded from: {plugin_dir}")
    logger.info(f"Plugin version: {VERSION}")
    
    return "Template Plugin"


# ============================================================================
# CONFIGURATION / PREFERENCES
# ============================================================================
def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """
    Return a TK Frame for adding to the EDMarketConnector settings dialog.
    
    Args:
        parent: Root Notebook object the preferences window uses
        cmdr: The current commander
        is_beta: If the game is currently a beta version
        
    Returns:
        Optional[tk.Frame]: The preferences frame for this plugin
    """
    global my_setting
    
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)
    
    # Retrieve saved value from config (or default to 0)
    saved_value = config.get_int("TemplatePluginSetting")
    my_setting = tk.IntVar(value=saved_value)
    
    # Add preference UI elements
    nb.Label(frame, text="Template Plugin Settings").grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10)
    
    nb.Label(frame, text="Enable Feature:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    nb.Checkbutton(frame, text="Enable custom feature", variable=my_setting).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
    
    nb.Label(frame, text="This plugin extends EDMarketConnector with custom functionality.").grid(
        row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=10
    )
    
    return frame


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Called when the user dismisses the settings dialog.
    Save settings here.
    
    Args:
        cmdr: The current commander
        is_beta: If the game is currently a beta version
    """
    global my_setting
    
    if my_setting:
        config.set('TemplatePluginSetting', my_setting.get())
        logger.info(f"Preferences saved. Feature enabled: {my_setting.get()}")


# ============================================================================
# DISPLAY / UI
# ============================================================================
def plugin_app(parent: tk.Frame) -> Tuple[tk.Label, tk.Label]:
    """
    Create UI widgets for the EDMarketConnector main window.
    
    Args:
        parent: The root EDMarketConnector window
        
    Returns:
        Tuple[tk.Label, tk.Label]: A pair of widgets to add to the main window
    """
    global status_label
    
    label = tk.Label(parent, text="Template Status:")
    status_label = tk.Label(parent, text="Ready", foreground="green")
    
    logger.info("UI widgets created")
    
    return label, status_label


def update_status(text: str, color: str = "green") -> None:
    """
    Update the status label in the main window.
    
    Args:
        text: The status text to display
        color: The color of the text
    """
    global status_label
    
    if status_label:
        status_label["text"] = text
        status_label["foreground"] = color


# ============================================================================
# EVENT HANDLERS
# ============================================================================
def journal_entry(
    cmdr: str,
    is_beta: bool,
    system: Optional[str],
    station: Optional[str],
    entry: Dict[str, Any],
    state: Dict[str, Any]
) -> Optional[str]:
    """
    Handle a new entry in the game's journal.
    
    Args:
        cmdr: Current commander name
        is_beta: Is the game currently in beta
        system: Current system, if known
        station: Current station, if any
        entry: The journal event
        state: More info about the commander, their ship, and their cargo
        
    Returns:
        Optional[str]: An error message, or None
    """
    try:
        event_type = entry.get('event', 'Unknown')
        logger.debug(f"Journal entry: {event_type}")
        
        if event_type == 'FSDJump':
            star_system = entry.get('StarSystem', 'Unknown')
            logger.info(f"Jumped to system: {star_system}")
            update_status(f"In {star_system}", "green")
            
        elif event_type == 'Docked':
            station_name = entry.get('StationName', 'Unknown')
            logger.info(f"Docked at: {station_name}")
            update_status(f"Docked at {station_name}", "blue")
            
        elif event_type == 'Undocked':
            logger.info("Undocked")
            update_status("Undocked", "yellow")
            
        return None
        
    except Exception as e:
        logger.exception("Error processing journal entry")
        return f"Plugin error: {str(e)}"


def dashboard_entry(cmdr: str, is_beta: bool, entry: Dict[str, Any]) -> Optional[str]:
    """
    Handle the latest data from the Status.json file.
    
    This is called when an update to Status.json is detected (typically about once
    a second when in orbital flight).
    
    Args:
        cmdr: Current commander name
        is_beta: If the game is currently in beta
        entry: Data from status.json
        
    Returns:
        Optional[str]: An error message, or None
    """
    try:
        logger.debug("Dashboard entry received")
        # Add your dashboard event handling here
        return None
        
    except Exception as e:
        logger.exception("Error processing dashboard entry")
        return f"Plugin error: {str(e)}"


def cmdr_data(data: Any, is_beta: bool) -> Optional[str]:
    """
    Handle fresh CMDR, station, and shipyard data from Frontier's CAPI servers.
    
    Args:
        data: /profile API response, with /market and /shipyard added
        is_beta: If the game is currently in beta
        
    Returns:
        Optional[str]: An error message, or None
    """
    try:
        if data.get('commander') is None or data['commander'].get('name') is None:
            logger.error("Invalid CAPI data")
            return None
        
        cmdr_name = data['commander']['name']
        logger.info(f"CAPI data received for commander: {cmdr_name}")
        
        return None
        
    except Exception as e:
        logger.exception("Error processing CAPI commander data")
        return f"Plugin error: {str(e)}"


def capi_fleetcarrier(data: Any) -> Optional[str]:
    """
    Handle fresh Fleet Carrier data from Frontier's CAPI servers.
    
    Args:
        data: /fleetcarrier API response
        
    Returns:
        Optional[str]: An error message, or None
    """
    try:
        if data.get('name') is None or data['name'].get('callsign') is None:
            logger.error("Invalid fleet carrier data")
            return None
        
        callsign = data['name']['callsign']
        logger.info(f"Fleet carrier data received: {callsign}")
        
        return None
        
    except Exception as e:
        logger.exception("Error processing fleet carrier data")
        return f"Plugin error: {str(e)}"


# ============================================================================
# PLUGIN SHUTDOWN
# ============================================================================
def plugin_stop() -> None:
    """
    Called when EDMarketConnector is closing.
    
    Clean up resources, save state, and stop any running threads here.
    """
    logger.info("Plugin shutting down")
    # Add cleanup code here
