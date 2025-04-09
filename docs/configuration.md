# Configuration
In order to configure what PlanningCenter roles are displayed in PCBoard, you need to setup a few things:
1. Add roles you want displayed to the `config.json` file
2. Put environment variables in `.env`


## Configuration File

PCBoard pulls its configuration from the `config.json` at startup. In this file, you specify what columns you would like to see on the board. You define the role name in PlanningCenter and a label for that section on the board. An example configuration file would look like this:
```
{
    "sections": [
        {
            "label": "HH1",
            "role": "Vocal 1"
        },
        {
            "label": "HH2",
            "role": "Vocal 2"
        },
        {
            "label": "AG",
            "role": "Acoustic Guitar"
        }
    ]
}
```


## Keyboard Shortcuts
PCBoard does not currently support live configuration, but this is in the works.

<!-- * <kbd>?</kbd> - Show keyboard shortcuts
* <kbd>0</kbd> - Show all slots
* <kbd>1</kbd>...<kbd>9</kbd> - Load group
* <kbd>d</kbd> - Start demo mode
* <kbd>e</kbd> - Open group editor
* <kbd>t</kbd> - Toggle TV view
* <kbd>i</kbd> - Change tv display mode
* <kbd>f</kbd> - Toggle fullscreen
* <kbd>g</kbd> - Toggle image backgrounds
* <kbd>v</kbd> - Toggle video backgrounds
* <kbd>n</kbd> - Extended Name editor
* <kbd>s</kbd> - Device configuration editor
* <kbd>q</kbd> - Show QR code
* <kbd>esc</kbd> - reload micboard -->

