<div align="center">
  <h1><PRODUCT-MODEL></h1>
  <p><strong><One-line product description></strong></p>
  <p><strong>English</strong> | <a href="README_ZH.md">简体中文</a></p>
  <p>
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/actions/workflows/build.yml"><img alt="Build" src="https://github.com/waveshareteam/<PRODUCT-MODEL>/actions/workflows/build.yml/badge.svg"></a>
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest"><img alt="Latest Release" src="https://img.shields.io/github/v/release/waveshareteam/<PRODUCT-MODEL>"></a>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/waveshareteam/<PRODUCT-MODEL>"></a>
  </p>
  <p>
    <a href="https://www.waveshare.com/<product-page>.htm">🌐 Product</a> &middot;
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest">📦 Firmware</a> &middot;
    <a href="examples/esp-idf/">🧩 ESP-IDF</a> &middot;
    <a href="examples/arduino/examples/">🔧 Arduino</a> &middot;
    <a href="hardware/">📚 Documentation</a>
  </p>
  <p><img src="docs/images/<product-model>.jpg" alt="<PRODUCT-MODEL> development board"></p>
</div>

---

## ✨ Overview

<Two or three sentences: what the board is and what this repository provides.>

| Feature | Device / interface |
| --- | --- |
| MCU | <chip> |
| Display | <size, resolution, interface, controller> |
| Touch | <controller, interface> |
| Board support | Managed component: `<namespace/component>` |

## 📦 Quick Start

The fastest way to try an example is a ready-to-flash package from the
[latest release](https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest).

1. Download the `*-combined.zip` package for the example and framework version you need.
2. Extract the archive and install esptool with `python -m pip install esptool`.
3. Connect the board over USB.
4. Run `flash_combined.bat COMx` on Windows or `./flash_combined.sh /dev/ttyACM0` on Linux.
5. Reset the board if it does not restart automatically.

Factory firmware (restores the out-of-box demo): download the `FactoryOnly` file from the [Releases page](https://github.com/waveshareteam/<PRODUCT-MODEL>/releases).

## 🧪 Examples

### ESP-IDF

| Example | Main feature |
| --- | --- |
| [<01_example>](examples/esp-idf/<01_example>/) | <feature> |

### Arduino

| Example | Main feature |
| --- | --- |
| [<01_example>](examples/arduino/examples/<01_example>/) | <feature> |

Libraries used by the sketches are bundled in [`examples/arduino/libraries`](examples/arduino/libraries/).

## 🛠️ Development Environment

| Framework | Version | Examples |
| --- | --- | ---: |
| ESP-IDF | `<vX.Y.Z>` | <n> |
| Arduino-ESP32 | `<X.Y.Z>` | <n> |

## 📚 Resources

- [Schematic](hardware/)
- [Product page](https://www.waveshare.com/<product-page>.htm)
- [Wiki](<wiki URL>)

## 🤝 Support

- Example or repository problem: [open an issue](https://github.com/waveshareteam/<PRODUCT-MODEL>/issues/new/choose).
- Product usage, hardware or order questions: [Waveshare support](https://service.waveshare.com/).

## 📄 License

Apache License 2.0. See [LICENSE](LICENSE).
