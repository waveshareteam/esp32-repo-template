# 发布

本文是固件包格式、烧录说明和发布流程的唯一来源。产品仓库的 README 只保留「下载并烧录」的几步操作，其余内容都指向本文和固件包自带的 README。

## 两类固件

| 类型 | 来源 | 存放位置 |
| --- | --- | --- |
| 示例固件 | CI 从 `examples/` 的源码构建 | GitHub Release 资产 |
| 出厂固件等实测固件 | 维护者在实物上测试后提交 | 产品仓库的 `firmware/` |

除 `firmware/` 外，固件二进制不提交到 Git。产品 README 中的出厂固件链接指向 `firmware/` 目录，更换固件时不用改链接。

## 出厂固件

`firmware/` 里的每个文件都是从 `0x0` 烧录的单个合并 BIN，不打包成 ZIP：

- 文件名为 `<产品名>_<固件名>_<YYYYMMDD>.bin`，日期即版本。出厂固件的固件名是 `FactoryOnly`，例如 `ESP32-S3-Touch-AMOLED-2.06_FactoryOnly_20261019.bin`。其他实测固件（如小智 AI）的固件名用说明用途的英文词；有自己版本号的固件用它的版本号代替日期，例如 `<产品名>_XiaoZhi_v2.1.0.bin`。它们不同步到固件下载页面。
- 旧版本保留，不删除。删掉的文件仍在 Git 历史里，删除并不能让仓库变小，保留下来用户可以直接下载旧版。
- `firmware/README.md` 和 `README_ZH.md` 每个文件一行：文件名和用途，新版本在上。烧录命令写最新出厂固件的完整文件名，客户可以直接复制运行，换固件时一起改。
- 提交前在实物上整片擦除后从 `0x0` 烧录验证。

固件下载页面从产品仓库的 `firmware/` 同步文件名匹配 `*_factoryonly*.bin` 的文件中日期最新的一个，所以出厂固件不能有两个文件日期相同。

| 情况 | 产品仓库 |
| --- | --- |
| 源码开源 | 源码放在 `examples/factory/`（一个 ESP-IDF 工程），`product.json` 写 `"factory_firmware": { "esp_idf": "v5.5.5" }`。CI 用这个版本编译，合并镜像 `<产品名>_FactoryOnly.bin` 作为 `factory-firmware` 产物上传，维护者下载后实测、改名提交到 `firmware/` |
| 源码不开源 | 没有 `examples/factory/`，`product.json` 不写 `factory_firmware`，维护者直接提交合并镜像 |

出厂固件只用一个 ESP-IDF 版本构建，不跟随 `esp_idf.versions`。

## 固件包格式

`ci/package_firmware.py` 读取框架的构建输出，生成 `<产物名>-combined.zip`，其中包含：

- `bin/` 下的原始偏移寻址二进制（引导程序、分区表、应用及其他）
- 从 `0x0` 烧录的 `bin/<产物名>-combined.bin`
- `flash_combined.sh`、`flash_combined.bat`、`flash_combined_args.txt`：烧录合并镜像
- `flash.sh`、`flash.bat`、`flash_args.txt`：烧录分段镜像
- `manifest.json`：框架、版本、工程、target、Git SHA、各文件的偏移、大小和 SHA256
- 固件包 README

产物名为 `<产品名>-<示例名>-<ESP-IDF 版本>` 或 `<产品名>-<示例名>-arduino-<core 版本>`，产品名取自 `product.json`。

ESP-IDF 的偏移和 esptool 参数来自 `flasher_args.json`。Arduino 优先使用导出的 `.merged.bin`；`.merged.bin` 不存在时，按引导程序位于 `0x0` 的布局推导。打包器会拒绝重叠的二进制区域，合并镜像用 `0xFF` 填充未使用的地址间隙。

## 烧录

常规安装使用 `flash_combined.sh` 或 `flash_combined.bat`。只有明确需要原始布局时才使用分段镜像脚本。

- 使用每个固件包清单记录的烧录布局，不要混用不同固件包里的引导程序、分区表或应用。
- 监视器报告应用校验和不匹配时，重新烧录完整的合并镜像，并用同一次 CI 构建的 ELF 解码日志。

## 发布流程

1. 改动通过拉取请求合并到 `main`，按变更范围选中的构建全部成功；需要硬件验证的改动已验证。
2. 在合并后的提交上打 `v*` 标签并推送，例如 `git tag v1.0.2 && git push origin v1.0.2`。
3. 标签触发完整构建：全部示例和出厂固件（开源时）。全部成功后，CI 用 `ci/prepare_release_assets.py` 核对固件包的数量、合并镜像、校验和与 Git SHA，再创建同名的**草稿** Release，附上全部示例 ZIP 和 `manifest-combined-assets.json`。
4. 维护者打开草稿，按[版本说明](#版本说明)补写正文，然后发布。

任何构建失败或核对不通过时不会创建草稿 Release。偶发失败可在 Actions 页面重新运行失败的任务；需要改代码时，合并修复后打新的标签。发布固件必须来自标签触发的 CI，本地构建的固件不能作为发布内容。

## 调试命令

以下命令在产品仓库的根目录运行，`<template>` 是本仓库的检出路径。

### 下载 CI 产物

```bash
python3 <template>/ci/download_artifacts.py --run-id <run-id> --keep-archives --clean
```

用于在发布前拿到某次 CI 构建的固件做测试。省略 `--run-id` 时，下载器选择当前分支上最新成功的 `build.yml` 运行。可用 `--artifact <名称>` 下载单个产物，或用 `--pattern "firmware-esp-idf-*"` 选择子集。产物解压到 `release-downloads/run-<run-id>/`。身份验证使用 `GH_TOKEN`、`GITHUB_TOKEN` 或当前 GitHub CLI 登录。

### 本地调试打包器

```bash
python3 <template>/ci/package_firmware.py \
  --framework esp-idf \
  --project examples/esp-idf/<示例> \
  --build-dir build/<示例>-<版本> \
  --name <产品名>-<示例>-<版本> \
  --framework-version <版本> \
  --git-sha <git-sha> \
  --output-dir release-artifacts
```

Arduino 构建把 `--framework` 换成 `arduino`，`--project` 指向草图目录。`--target` 省略时取 `product.json` 的 `target`。

## 版本说明

版本说明写在 GitHub Release 的正文里，不在产品仓库中保存 Markdown 文件。写法可参考 [`release-notes-example.md`](release-notes-example.md)。

## 生成文件

| 路径 | 内容 |
| --- | --- |
| `release-artifacts/` | 打包器输出 |
| `release-downloads/` | 下载的 CI 产物 |
| `release-dist/` | `prepare_release_assets.py` 暂存的发布资产 |

这三个路径都应被产品仓库的 `.gitignore` 忽略，不得提交。
