# Release notes example

The text below is the original v1.0.1 release body of the ESP32-S3-Touch-AMOLED-1.75C pilot repository, kept as a reference for writing GitHub Release notes. Release notes belong in the GitHub Release body, not in the product repository.

---

## ESP32-S3-Touch-AMOLED-1.75C v1.0.1

[English](v1.0.1.md) | [简体中文](v1.0.1_ZH.md)

This release modernizes the example layout, validates current ESP-IDF and Arduino toolchains, and
publishes CI-built firmware for every first-party demo.

### Firmware Assets

At the time of the v1.0.1 release, the release contained 17 `*-combined.zip`
firmware packages built with the following then-validated versions:

- Five ESP-IDF examples built with ESP-IDF `v5.5.4`.
- Five ESP-IDF examples built with ESP-IDF `v6.0.2`.
- Seven Arduino examples built with Arduino-ESP32 `3.3.10`.

Every package includes a single `*-combined.bin` image for offset `0x0`, the original split
binaries, flash scripts for shell and Windows, and a manifest with checksums. The
`manifest-combined-assets.json` asset contains SHA256 checksums and source metadata for all packages.

### Highlights

- All 12 first-party demos are built, packaged, and checksum-verified by CI.
- `03_esp-brookesia` keeps its 40 KB LVGL task stack and large allocations in PSRAM to
  prevent stack overflow and transform-buffer exhaustion.
- `04_Immersive_block` bounds shape generation and calibration work, and reduces frame workload to
  avoid watchdog resets.
- ESP-IDF examples use the online Waveshare BSP and Espressif LVGL adapter components.
- ESP-IDF projects build on both supported release lines.
- Arduino examples build with the latest validated Arduino-ESP32 core and bundled libraries.
- Repository setup, example, firmware, CI, release, and troubleshooting documentation is now
  available under `docs/`.

### Flashing

Extract the package for the desired example, install esptool, and run:

```bash
./flash_combined.sh /dev/ttyACM0
```

On Windows:

```bat
flash_combined.bat COMx
```

The script flashes the combined image at `0x0`. Do not mix binaries from different
packages. If a monitor reports a checksum mismatch, reflash the complete package and use symbols from
the same CI build.

The factory firmware package is attached to this Release next to the example packages.

---

## ESP32-S3-Touch-AMOLED-1.75C v1.0.1

[English](v1.0.1.md) | [简体中文](v1.0.1_ZH.md)

此版本更新了示例目录，验证了当时的 ESP-IDF 和 Arduino 工具链，并为每个第一方演示
发布由 CI 构建的固件。

### 固件资源

在 v1.0.1 发布时，该版本包含 17 个 `*-combined.zip` 固件包，使用当时验证的版本构建：

- 五个 ESP-IDF 示例使用 ESP-IDF `v5.5.4`；
- 五个 ESP-IDF 示例使用 ESP-IDF `v6.0.2`；
- 七个 Arduino 示例使用 Arduino-ESP32 `3.3.10`。

每个固件包都包含从偏移 `0x0` 烧录的单个 `*-combined.bin`、原始分段二进制、shell
和 Windows 烧录脚本，以及带校验和的清单。`manifest-combined-assets.json` 包含全部
固件包的 SHA256 校验和和源码元数据。

### 主要更新

- 12 个第一方演示全部由 CI 构建、打包并验证校验和。
- `03_esp-brookesia` 保留 40 KB LVGL 任务栈，并在 PSRAM 中进行大块分配，以避免栈溢出
  和变换缓冲区耗尽。
- `04_Immersive_block` 限制图形生成和校准工作量，并降低每帧负载以避免看门狗复位。
- ESP-IDF 示例使用在线 Waveshare BSP 和 Espressif LVGL 适配器组件。
- ESP-IDF 工程覆盖两个受支持的发布系列。
- Arduino 示例使用当时最新验证的 Arduino-ESP32 内核和随仓库提供的库。
- 仓库设置、示例、固件、CI、发布和故障排查文档位于 `docs/`。

### 烧录

解压所需示例的固件包，安装 esptool，然后运行：

```bash
./flash_combined.sh /dev/ttyACM0
```

Windows：

```bat
flash_combined.bat COMx
```

脚本从偏移 `0x0` 烧录合并镜像。不要混用不同固件包中的二进制。如果监视器报告校验和
不匹配，请重新烧录完整固件包，并使用同一 CI 构建中的符号文件。

出厂固件包与示例固件包一起附在本 Release 中。
