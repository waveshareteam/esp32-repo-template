# <示例名称>

[English](README.md) | [简体中文](README_ZH.md)

## 功能

<一两句话。>

## 硬件需求

- <PRODUCT-MODEL> 开发板
- <需要的外设或电池；没有时删除这一行。>

## 怎么运行

<!-- ESP-IDF 示例：保留这一段，删除 Arduino 那一段。 -->

```bash
idf.py set-target <esp-idf-target> build flash monitor
```

<!-- Arduino 示例：保留这一段，删除 ESP-IDF 那一段。 -->

1. 在开发板管理器中安装 `esp32`（Arduino-ESP32），版本见仓库 README。
2. 把项目文件夹位置设为 `examples/arduino/`，或把 `examples/arduino/libraries/` 复制到项目文件夹下的 `libraries` 文件夹。
3. 选择开发板，并按 `.github/product.json` 中的 FQBN 设置「工具」菜单：

   | 工具菜单 | 取值 |
   | --- | --- |
   | 开发板 | <开发板> |
   | <选项> | <取值> |

4. 打开 `.ino` 文件并上传。

## 预期现象

<用户在屏幕、串口监视器或喇叭上看到或听到什么。>

## 常见问题

暂无。
