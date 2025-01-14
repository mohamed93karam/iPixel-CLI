# iPixel Color CLI

Various reverse engineering tools and rewrite of the "iPixel Color" application in CLI Python for LED Matrix displays manufactured by Taizhou Yumo Lighting Co., Ltd.
Tested only on a 96x16 display, but should work on other sizes (if not please open an issue).

⚠️ Still experimental, some commands might change in the future. ⚠️

## Features

- [x] 🔗 Connect to the device
- [x] 🔆 Set brightness
- [x] 🟥 Set pixels on screen
- [x] ⏲️ Set clock mode
- [x] 🎉 Set the display mode to fun mode (do not save display)
- [x] ✏️ Write text on the screen (with custom font support)
- [x] 💥 Clear memory
- [x] 🔒 Set password (UNTESTED !)
- [x] 🎢 Send animations
- [x] 🖼️ Write frames to EEPROM
- [x] ✅ Maintain connection to the device (WebSocket server)

- [ ] 🔧 Set the clock and date
- [ ] 🔧 Change orientation
- [ ] 🔈 Audio mode

## Installation

Clone the repository and install the required packages.

```bash
git clone https://github.com/lucagoc/LED-Matrix-BLE-Tools
cd LED-Matrix-BLE-Tools
```

Then use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages.

```bash
pip install -r requirements.txt
```

## Usage

### ⚠️ WARNING ⚠️
Invalid data sent to the device can lead to BOOTLOOPS

While it is possible to recover from a bootloop by sending a clear command before the device tries to read the EEPROM, it is a little bit tricky and the timing is very short.
This tool is still experimental, use at your own risk.

### Syntax

Send a command to the device with the following command:

```bash
python ipixelcli.py -a <bt_address> -c <command>
```

Available commands are:

- `send_text <text> [rainbow_mode/animation/color/speed]`
- `send_animation <GIF hex or file path>`
- `set_clock_mode <0-8>`

- `set_fun_mode <true|false>`
- `set_pixel <x> <y> <color>`

- `clear`
- `set_brightness <0-100>`

Example:

```bash
python ipixelcli.py -a 4B:1E:2E:35:73:A3 -c send_text "Hello World !" rainbow_mode=5 speed=50
```

You can also start a basic WebSocket server using the following command :

```bash
python ipixelcli.py -a <bt_address> --server -p <port>
```

Then, send a request to the server with the following content:

```json
{
    "command": "<command>",
    "params": ["<param1>", "<param2>", "<param3>"]
}
```

For example :
```json
{
    "command": "send_text",
    "params": ["Hello World !", "rainbow_mode=1", "speed=50"]
}
```

## Font generation

Edit the `all.png` file in the font folder to change characters. Then run `gen_font.py` to the trimmed characters.
