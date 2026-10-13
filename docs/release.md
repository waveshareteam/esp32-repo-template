# 发布

本文是固件包格式、烧录说明和发布流程的唯一来源。产品仓库的 README 只保留「下载并烧录」的几步操作，其余内容都指向本文和固件包自带的 README。

## 两类固件

| 类型 | 来源 | 存放位置 |
| --- | --- | --- |
| 示例固件 | CI 从 `examples/` 的源码构建 | GitHub Release 资产 |
| 出厂固件 | 工厂烧录和恢复用镜像，不由 CI 生成 | GitHub Release 资产，下载页面记录在 `product.json` 的 `factory_firmware` |

出厂固件体积大且不可复现，不提交到 Git，也不会被重新打包为示例固件。需要可复现的固件时，使用带标签的 Release 包。

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

## 发布门禁

满足以下全部条件才可以发布：

1. 拉取请求的分类任务和按变更范围选中的全部构建/打包任务成功。
2. 必要的硬件验证或维护者批准已完成。
3. 拉取请求已合并，发布标签指向合并后的提交。
4. 标签触发的完整 CI 矩阵成功。
5. 标签运行的全部压缩包通过 `ci/prepare_release_assets.py` 验证。
6. GitHub Release 包含全部合并 ZIP 和 `manifest-combined-assets.json`。

发布固件必须来自成功的标签工作流，本地构建的固件不能作为发布输入。

## 发布命令

以下命令在产品仓库的根目录运行，`<template>` 是本仓库的检出路径。

### 下载 CI 产物

```bash
python3 <template>/ci/download_artifacts.py --run-id <run-id> --keep-archives --clean
```

省略 `--run-id` 时，下载器选择当前分支上最新成功的 `build.yml` 运行。可用 `--artifact <名称>` 下载单个产物，或用 `--pattern "firmware-esp-idf-*"` 选择子集。产物解压到 `release-downloads/run-<run-id>/`。身份验证使用 `GH_TOKEN`、`GITHUB_TOKEN` 或当前 GitHub CLI 登录。

### 验证并暂存发布资产

```bash
python3 <template>/ci/prepare_release_assets.py \
  --input-dir release-downloads/run-<run-id> \
  --output-dir release-dist/<版本> \
  --version <版本> \
  --git-sha <标签提交的完整 SHA> \
  --clean
```

期望的压缩包数量默认等于完整矩阵的大小，由 `product.json` 和仓库里发现的示例算出，也可以用 `--expected-count` 指定。脚本会拒绝缺少合并镜像、偏移不正确、校验和不匹配、产物名重复、Git SHA 混用或数量不符的输入。验证通过后，脚本复制 ZIP 并写入 `manifest-combined-assets.json`，其中有全部 ZIP 的校验和。

把暂存目录中的全部 ZIP 和 `manifest-combined-assets.json` 上传到 GitHub Release。

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
| `release-dist/` | 暂存的发布资产 |

这三个路径都应被产品仓库的 `.gitignore` 忽略，不得提交。
