# 产品仓库规范

本文定义 Waveshare ESP32 产品仓库的目录结构、达标级别，以及每类信息应该写在哪里。

## 目录规范

产品仓库只放用户关心的内容，外加一份产品配置：

```text
<PRODUCT-MODEL>/
├── .github/
│   ├── workflows/build.yml        # 约 10 行，调用本仓库的可复用工作流
│   └── product.json               # 唯一的产品配置
├── examples/
│   ├── esp-idf/<示例>/            # 每个示例有 README.md + README_ZH.md
│   ├── arduino/
│   │   ├── examples/<示例>/       # 每个示例有 README.md + README_ZH.md
│   │   └── libraries/
│   │       ├── board_config/      # 板级配置，如 pin_config.h
│   │       ├── lv_conf.h
│   │       └── <第三方库>/        # 只保留编译所需文件 + LICENSE
│   ├── factory/                   # 可选，开源的出厂固件源码（一个 ESP-IDF 工程）
│   └── xiaozhi/                   # 可选，仅限不好合并到小智仓库的特殊产品
├── firmware/                      # 可选，只放实测过、可直接烧录的 BIN
│   ├── README.md / README_ZH.md   # 每个固件一行：文件名和用途
│   └── <PRODUCT-MODEL>_FactoryOnly_<YYYYMMDD>.bin
├── hardware/
│   ├── schematic/                 # 原理图 PDF
│   └── mechanical/                # 可选，2D 尺寸图（PDF、DXF）和 3D 模型（STEP）
├── docs/images/                   # README 用到的图片
├── README.md
├── README_ZH.md
├── LICENSE
└── .gitignore
```

目录规则：

- 顶层只允许出现上面列出的条目。CI 脚本、测试、发布工具、规范文档放在本仓库。CONTRIBUTING、SUPPORT、SECURITY、issue 和 PR 模板由 `waveshareteam/.github` 提供，组织下的仓库自动继承。
- 没有 Arduino 示例的产品不建 `examples/arduino/`，也不在 `product.json` 里写 `arduino`。没有 ESP-IDF 示例的产品同理。
- 示例目录不带框架版本号（不用 `ESP-IDF-v5.5/` 这类名字），版本只写在 `product.json`。
- 每个示例都必须能用 `product.json` 列出的全部框架版本编译。
- `examples/arduino/libraries/` 是所有草图共用的一套库，同一个库只放一个版本（例如只放一个 LVGL）。
- `firmware/` 只放维护者在实物上测试过的合并镜像（BIN）和说明它们的 README，供用户不搭环境直接烧录、对比，不放源码。见[发布](release.md#出厂固件)。
- 固件源码放在 `examples/` 下与 `esp-idf/`、`arduino/` 平行的固定目录，用名字区分，不编号：出厂固件源码开源时放在 `examples/factory/`，并在 `product.json` 写 `factory_firmware.esp_idf`；不开源时不建这个目录。小智源码一般不放进产品仓库，只有不好合并到小智仓库的特殊产品才放在 `examples/xiaozhi/`。
- 硬件资料只放这两个子目录，有内容才建。文件名带产品名和版本，例如 `<产品名>-Schematic-V1.0.pdf`、`<产品名>-3D-V1.0.step`。原理图和 PCB 的源文件不放进产品仓库。
- 第一方 Markdown 提供英文主文件和 `_ZH.md` 简体中文版，两者顶部互相链接。第三方库和上游组件自带的文档保持原样，不翻译、不改名。
- 构建产物、下载的 CI 产物和大体积二进制文件不提交到 Git，`firmware/` 中实测过的固件除外。
- `.gitmodules`、`.gitattributes`、`.gitkeep` 必须被跟踪，不要写进 `.gitignore`。
- `.claude/`、`.cursor/`、`.codex/` 等 AI 编码代理的本地目录必须写进 `.gitignore`，不得提交。

新仓库或迁移旧仓库时，从 [`skeleton/`](../skeleton/) 复制骨架。

## 级别

`product.json` 的 `tier` 字段记录仓库当前达到的级别。

| 级别 | `tier` | 要求 |
| --- | :---: | --- |
| L0 卫生 | 0 | README 符合模板、有 LICENSE、`.gitignore` 正确、不提交构建产物和大体积二进制文件（`firmware/` 除外）、第三方库只保留编译所需文件和 LICENSE |
| L1 构建 | 1 | L0 + `product.json` + `build.yml`，所有示例 CI 编译通过，每个示例有 README |
| L2 发布 | 2 | L1 + 用 `v*` 标签发布：CI 生成的草稿 Release 经审阅后发布，版本说明写在 GitHub Release 里 |

## 每类信息只有一个来源

同一条信息只写在一个地方，其他地方需要时链接过去，不复制。

| 信息 | 唯一来源 |
| --- | --- |
| 框架版本、FQBN | `product.json` |
| 引脚定义 | 托管 BSP 或 `board_config/pin_config.h` |
| 固件包格式、烧录说明 | 本仓库 [`docs/release.md`](release.md) 和固件包自带的 README |
| issue 需提供的信息 | 组织仓库的 issue 模板 |
| CI 和发布规则 | 本仓库 [`docs/ci.md`](ci.md)、[`docs/release.md`](release.md) |
| 示例特有说明 | 该示例的 README |

产品 README 里的版本表是 `product.json` 的展示，升级版本时两处一起修改。两处不一致时，以 `product.json` 为准。

## 组件归属原则

示例优先使用 Waveshare 和 Espressif 的托管组件，在 `idf_component.yml` 中声明依赖，不把可复用的 BSP、显示、触摸、传感器、音频或总线驱动复制进产品仓库。

仓库里的本地组件按所有权和用途区分，判断清楚之后再决定去留：

- **产品功能代码**：只服务于某个示例的 UI 或业务逻辑，留在该示例下。
- **嵌入的上游框架**：保留源码、归属说明和文档，除非执行明确的上游同步，否则不改动。
- **板级胶水代码**：构建在托管 BSP 之上、只对这块板有意义的适配层，留在使用它的示例下。

具体做法：

- 用托管组件替换本地副本的前提是：存在语义等价、硬件兼容，并且覆盖 `product.json` 所列全部框架版本的托管组件。
- 开发板专用的示例组合、临时兼容代码和仅供示例使用的资源，放在使用它的示例附近。
- 可复用的 BSP、显示、触摸、传感器、音频和总线修复，尽可能先进入共享组件源，而不是只修在产品仓库里。
- 仅凭组件名称或目录位置，不足以证明某个组件可以删除。
- 为了兼容性而限制依赖版本时，在清单旁边写明受影响的框架或 target、限制的原因，以及什么条件下可以放开。

## 示例 README

每个示例有 `README.md` 和 `README_ZH.md`，固定 5 节：功能、硬件需求、怎么运行、预期现象、常见问题。模板见 [`skeleton/example-README.md`](../skeleton/example-README.md) 和 [`skeleton/example-README_ZH.md`](../skeleton/example-README_ZH.md)。

- 「常见问题」没有内容时写「暂无」，不要删除这一节。

## 产品 README

`README.md` 和 `README_ZH.md` 只面向用户，结构固定：

| 章节 | 内容 |
| --- | --- |
| 头部 | 居中标题、语言切换、徽章、快捷链接、头图（商品页白底图，`width="500"`） |
| ✨ 概述 | 两三句话 + 器件表；器件表必须写 Flash 和 PSRAM 容量，没有 PSRAM 时写"无" |
| 📦 快速开始 | 下载合并固件包并烧录，5 步以内；出厂固件一行 |
| 🧪 示例 | 每个框架一张表，每一项链接到示例目录 |
| 🛠️ 开发环境 | 版本表：框架、版本、示例数 |
| 📚 资料 | 原理图、机械资料（有 `hardware/mechanical/` 时）、产品页、Wiki；`README_ZH.md` 的 Wiki 用中文站 `https://docs.waveshare.net/<产品名>/` |
| 🤝 支持 | issue 和官方支持的链接；`README_ZH.md` 的 issue 指向 Gitee 镜像 `https://gitee.com/waveshare/<产品名>/issues`，没有 Gitee 镜像时删掉这一行，技术支持指向 `https://docs.waveshare.net/<产品名>/Technical-Support/` |
| 📄 许可证 | 一行 |

不写仓库结构表、CI 任务数、矩阵说明和维护者文档链接。章节图标和快捷链接由 [`defaults/markdown-audit.json`](../defaults/markdown-audit.json) 约束，`tests/test_homepage_contract.py` 会检查骨架 README 是否符合。

## GitHub 仓库信息

仓库页面 About 栏的三项与 README 和 `product.json` 保持一致：

| 字段 | 内容 |
| --- | --- |
| Description | `Waveshare <README 头部的一句话描述>: <框架> examples, firmware and hardware resources`，`<框架>` 按 `product.json` 写 `ESP-IDF and Arduino`、`ESP-IDF` 或 `Arduino` |
| Website | `product.json` 的 `product_url` |
| Topics | `waveshare`、`esp32`、芯片（`target` 加连字符，如 `esp32-s3`）、型号（仓库名转小写，`.` 换成 `-`，如 `esp32-s3-touch-amoled-2-06`），以及 `product.json` 中有的 `esp-idf`、`arduino` |

例如 `ESP32-S3-Touch-AMOLED-2.06` 的 Description 是 `Waveshare ESP32-S3 2.06-inch 410 x 502 QSPI AMOLED touch development board: ESP-IDF and Arduino examples, firmware and hardware resources`。
