# <Example name>

[English](README.md) | [简体中文](README_ZH.md)

## What It Does

<One or two sentences.>

## Hardware Required

- <PRODUCT-MODEL> development board
- <Peripherals or battery, if any. Otherwise delete this line.>

## How to Run

<!-- ESP-IDF example, no board_manager in product.json: keep this block, delete the other two. -->

```bash
idf.py set-target <esp-idf-target> build flash monitor
```

<!-- ESP-IDF example, board_manager in product.json: keep this block, delete the other two. -->

```bash
pip install esp-bmgr-assist
idf.py bmgr -b <board-name>
idf.py build flash monitor
```

<!-- Arduino example: keep this block, delete the other two. -->

1. Install the `esp32` board package (Arduino-ESP32) in the version listed in the repository README.
2. Set the sketchbook location to `examples/arduino/`, or copy `examples/arduino/libraries/` into
   your sketchbook `libraries` folder.
3. Select the board and the **Tools** menu options that match the FQBN in `.github/product.json`:

   | Tools menu | Value |
   | --- | --- |
   | Board | <board> |
   | <option> | <value> |

4. Open the `.ino` file and upload.

## Expected Result

<What the user sees on the display, serial monitor or speaker.>

## Troubleshooting

None yet.
