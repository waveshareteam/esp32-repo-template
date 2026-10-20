# Firmware

[English](README.md) | [简体中文](README_ZH.md)

Ready-to-flash firmware tested on the <PRODUCT-MODEL> board. Each file is a merged image flashed at `0x0`; the date (or upstream version) in the file name is its version. Older versions are kept; the newest is listed first.

| File | Purpose |
| --- | --- |
| `<PRODUCT-MODEL>_FactoryOnly_<YYYYMMDD>.bin` | Factory firmware, restores the out-of-box demo |

Flash with esptool:

```bash
python -m pip install esptool
esptool.py --chip <esp-idf-target> --port <PORT> erase_flash
esptool.py --chip <esp-idf-target> --port <PORT> write_flash 0x0 <PRODUCT-MODEL>_FactoryOnly_<YYYYMMDD>.bin
```

The factory firmware source is in [`examples/factory`](../examples/factory/). <!-- Delete this line when the source is closed. -->
