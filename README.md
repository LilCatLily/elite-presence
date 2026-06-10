DISCLAIMER: This plugin template was created using the copilot ai

# EDMarketConnector Template Plugin

A comprehensive template plugin project for EDMarketConnector with complete boilerplate code, best practices, and production-ready structure.

## Features

- ✅ Proper logging setup with EDMarketConnector integration
- ✅ Configuration/Preferences UI support
- ✅ Main window status display
- ✅ Journal entry event handling
- ✅ Dashboard (Status.json) event handling
- ✅ CAPI commander data handling
- ✅ Fleet carrier data handling
- ✅ Error handling and reporting
- ✅ Semantic versioning support
- ✅ Type hints throughout
- ✅ Comprehensive documentation

## Installation

1. Clone or download this plugin folder
2. Place it in your EDMarketConnector plugins directory:
   - **Windows**: `%LOCALAPPDATA%\EDMarketConnector\plugins`
   - **Mac**: `~/Library/Application Support/EDMarketConnector/plugins`
   - **Linux**: `$XDG_DATA_HOME/EDMarketConnector/plugins` or `~/.local/share/EDMarketConnector/plugins`

3. Restart EDMarketConnector

## Development Setup

### Prerequisites

- Python 3.9+ (check [EDMC Releasing.md](https://github.com/EDCD/EDMarketConnector/blob/main/docs/Releasing.md#environment) for the current required version)
- PyCharm (recommended) or other Python IDE
- EDMarketConnector source code or installed version

### PyCharm Project Setup

1. Clone this repository: `git clone https://github.com/LilCatLily/EDMC-Plugin-Template.git`
2. Open the folder as a PyCharm project
3. Configure the Python interpreter to match EDMarketConnector's version
4. If developing locally, mark the EDMarketConnector source root as a Library Root

### Testing Your Plugin

1. Run EDMarketConnector with this plugin in the plugins directory
2. Check the log file for debug output:
   - **Windows**: `%TMP%\EDMarketConnector.log`
   - **Mac**: `$TMPDIR/EDMarketConnector.log`
   - **Linux**: `$TMP/EDMarketConnector.log`

## Project Structure

```
EDMC-Plugin-Template/
├── load.py              # Main plugin file (required)
├── README.md            # This file
├── requirements.txt     # External dependencies (if any)
├── .gitignore           # Git ignore rules
└── L10n/                # Localization folder (optional)
    └── en.template      # English translation template
```

## Configuration

The plugin stores its settings using EDMarketConnector's config system:

```python
from config import config

# Save a setting
config.set('TemplatePluginSetting', value)

# Retrieve settings
int_value = config.get_int('TemplatePluginSetting')
str_value = config.get_str('TemplatePluginSetting')
bool_value = config.get_bool('TemplatePluginSetting')
list_value = config.get_list('TemplatePluginSetting')
```

**Always use a unique prefix** for your settings to avoid conflicts with core EDMC or other plugins.

## Logging

The plugin uses Python's standard logging module. Log messages are automatically integrated with EDMarketConnector's logging system:

```python
logger.info('Information message')
logger.debug('Debug message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')
logger.exception('Exception occurred')  # Includes stack trace
```

## Available Event Hooks

### `plugin_start3(plugin_dir: str) -> str`
Called when the plugin is loaded. Return the internal name of your plugin.

### `plugin_prefs(parent, cmdr, is_beta) -> Optional[tk.Frame]`
Return a configuration frame for the Settings dialog.

### `prefs_changed(cmdr, is_beta) -> None`
Called when the user closes the Settings dialog. Save your settings here.

### `plugin_app(parent) -> Union[tk.Widget, Tuple[tk.Widget, tk.Widget]]`
Return UI widgets for the main window.

### `journal_entry(cmdr, is_beta, system, station, entry, state) -> Optional[str]`
Called for each new journal entry. Return an error message or None.

### `dashboard_entry(cmdr, is_beta, entry) -> Optional[str]`
Called when Status.json is updated (typically ~1 second during flight).

### `cmdr_data(data, is_beta) -> Optional[str]`
Called when CAPI commander/market/shipyard data is fetched.

### `capi_fleetcarrier(data) -> Optional[str]`
Called when CAPI fleet carrier data is fetched.

### `plugin_stop() -> None`
Called when EDMarketConnector is closing. Clean up here.

## Important Notes

### Thread Safety
- **Never** perform blocking operations (HTTP requests, database queries, etc.) in the main thread
- Always use worker threads for long-running operations
- Only call `event_generate()` from worker threads to communicate back to the main thread
- **Never** manipulate tkinter UI elements from worker threads

### Tkinter
- All tkinter operations must happen on the main thread
- Do NOT call `event_generate()` during shutdown (`config.shutting_down` is True)
- Use `theme.update()` to apply the current theme to dynamically created widgets

### HTTP Requests
- Use `requests` library instead of `urllib` for better certificate handling
- Import `timeout_session` for automatic request timeouts:
  ```python
  from timeout_session import timeout_session
  session = timeout_session.new_session()
  ```

### Plugin Naming
- Use underscores, not hyphens or dots, in your plugin folder name when distributing
- Valid: `My_Plugin`, `PLUGIN_NAME`
- Invalid: `My-Plugin`, `My.Plugin`

## Version Management

Update the version in your `load.py`:

```python
__version__ = "1.0.0"
VERSION = "1.0.0"
```

Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

## Dependencies

If your plugin requires external Python modules, include them in your plugin folder:

```bash
pip install module_name
# Copy to your plugin folder
cp -r /path/to/module_name ./
```

List dependencies in `requirements.txt`:

```
requests>=2.28.0
```

## Packaging for Distribution

Create a `.zip` archive of your plugin folder:

**Windows**: Right-click folder → Send to → Compressed (zipped) folder

**Mac**: Right-click folder → Compress

**Linux**: 
```bash
zip -r my_plugin.zip my_plugin/
```

Optionally remove `.pyc`, `.pyo` files and `__pycache__` directories.

## Localization

To add translation support:

1. Run `l10n.py` in your plugin folder to generate `L10n/en.template`
2. Rename to `L10n/<language_code>.strings` (e.g., `de.strings` for German)
3. Edit the `.strings` file with translations
4. Use in code:
   ```python
   import l10n
   import functools
   plugin_tl = functools.partial(l10n.translations.tl, context=__file__)
   
   text = plugin_tl("Translatable string")
   ```

## Resources

- [EDMC Plugin Documentation](https://github.com/EDCD/EDMarketConnector/blob/main/PLUGINS.md)
- [EDMC Wiki](https://github.com/EDCD/EDMarketConnector/wiki)
- [EDMC Source Code](https://github.com/EDCD/EDMarketConnector)
- [Journal File Format](https://forums.frontier.co.uk/showthread.php/401661)
- [CAPI Documentation](https://github.com/Athanasius/fd-api)

## Getting Started

1. **Fork or Clone** this repository
2. **Rename** the plugin folder to your plugin name (use underscores)
3. **Edit** `load.py` and update:
   - `VERSION` - Your plugin version
   - `plugin_start3()` return value - Your plugin's display name
   - Plugin logic in event handlers
4. **Test** with EDMarketConnector
5. **Distribute** as a `.zip` file

## License

MIT License - Feel free to use this template for your own plugins

## Support

For issues with this template, refer to the official [EDMC documentation](https://github.com/EDCD/EDMarketConnector/blob/main/PLUGINS.md).
For plugin-specific issues, check your `EDMarketConnector.log` file.
