# 固件

[English](README.md) | [简体中文](README_ZH.md)

在 <PRODUCT-MODEL> 开发板上实测过、可直接烧录的固件。每个文件都是从 `0x0` 烧录的合并镜像，文件名中的日期（或上游版本号）即版本。

| 文件 | 用途 |
| --- | --- |
| `<PRODUCT-MODEL>_FactoryOnly_<YYYYMMDD>.bin` | 出厂固件，恢复开箱演示 |

用 esptool 烧录：

```bash
python -m pip install esptool
esptool.py --chip <esp-idf-target> --port <PORT> erase_flash
esptool.py --chip <esp-idf-target> --port <PORT> write_flash 0x0 <FILE>.bin
```

出厂固件源码在 [`sourcecode`](sourcecode/) 目录。<!-- 源码不开源时删除这一行。 -->
