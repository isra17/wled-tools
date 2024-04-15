### Installation

```
poetry shell
poetry install
```

### Run

```bash
# Generate config file (This should be replaced with your own scripts or
# config files)
python -m wled_tools.dome

WLED_URL='http://192.168.1.32/' # Replace with your WLED url

# Apply the config to wled.
python -m wled_tools.api_client "${WLED_URL}" --scope cfg set --file settings/cfg.virtual.json
# Apply presets to wled
python -m wled_tools.api_client "${WLED_URL}" --scope presets set --file settings/presets.json

# Open the 2D viewer
python -m wled_tools.viewer settings/dome.json
```
