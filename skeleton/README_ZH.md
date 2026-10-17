<div align="center">
  <h1><PRODUCT-MODEL></h1>
  <p><strong><一句话产品描述></strong></p>
  <p><a href="README.md">English</a> | <strong>简体中文</strong></p>
  <p>
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/actions/workflows/build.yml"><img alt="构建" src="https://github.com/waveshareteam/<PRODUCT-MODEL>/actions/workflows/build.yml/badge.svg"></a>
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest"><img alt="最新版本" src="https://img.shields.io/github/v/release/waveshareteam/<PRODUCT-MODEL>"></a>
    <a href="LICENSE"><img alt="许可证" src="https://img.shields.io/github/license/waveshareteam/<PRODUCT-MODEL>"></a>
  </p>
  <p>
    <a href="https://www.waveshare.com/<product-page>.htm">🌐 产品</a> &middot;
    <a href="https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest">📦 固件</a> &middot;
    <a href="examples/esp-idf/">🧩 ESP-IDF</a> &middot;
    <a href="examples/arduino/examples/">🔧 Arduino</a> &middot;
    <a href="hardware/">📚 文档</a>
  </p>
  <p><img src="docs/images/<product-model>.jpg" alt="<PRODUCT-MODEL> 开发板" width="500"></p>
</div>

---

## ✨ 概述

<两三句话：这块板是什么，本仓库提供什么。>

| 功能 | 器件或接口 |
| --- | --- |
| MCU | <芯片> |
| 存储器 | <N> MB Flash，<N> MB PSRAM |
| 显示 | <尺寸、分辨率、接口、控制器> |
| 触摸 | <控制器、接口> |
| 板级支持 | 托管组件 `<namespace/component>` |

## 📦 快速开始

体验示例最快的方法是使用[最新版本](https://github.com/waveshareteam/<PRODUCT-MODEL>/releases/latest)中打包好的可烧录固件。

1. 下载所需示例和框架版本对应的 `*-combined.zip`。
2. 解压后通过 `python -m pip install esptool` 安装 esptool。
3. 通过 USB 连接开发板。
4. Windows 运行 `flash_combined.bat COMx`，Linux 运行 `./flash_combined.sh /dev/ttyACM0`。
5. 如果开发板未自动重启，请手动复位。

出厂固件（恢复开箱演示）：在 [Releases 页面](https://github.com/waveshareteam/<PRODUCT-MODEL>/releases)下载文件名带 `FactoryOnly` 的文件。

## 🧪 示例

### ESP-IDF

| 示例 | 主要功能 |
| --- | --- |
| [<01_example>](examples/esp-idf/<01_example>/) | <功能> |

### Arduino

| 示例 | 主要功能 |
| --- | --- |
| [<01_example>](examples/arduino/examples/<01_example>/) | <功能> |

草图使用的库随仓库提供，位于 [`examples/arduino/libraries`](examples/arduino/libraries/)。

## 🛠️ 开发环境

| 开发框架 | 版本 | 示例数 |
| --- | --- | ---: |
| ESP-IDF | `<vX.Y.Z>` | <n> |
| Arduino-ESP32 | `<X.Y.Z>` | <n> |

## 📚 资料

- [原理图](hardware/)
- [产品页](https://www.waveshare.com/<product-page>.htm)
- [Wiki](https://docs.waveshare.net/<PRODUCT-MODEL>/)

## 🤝 支持

- 示例或仓库问题：[提交 issue](https://gitee.com/waveshare/<PRODUCT-MODEL>/issues)。
- 产品使用、硬件或订单问题：[微雪技术支持](https://docs.waveshare.net/<PRODUCT-MODEL>/Technical-Support/)。

## 📄 许可证

Apache License 2.0，详见 [LICENSE](LICENSE)。
