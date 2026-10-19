# 持续集成

本仓库的 `.github/workflows/build.yml` 是一个可复用工作流（`on: workflow_call`）。产品仓库只保留一个约 10 行的调用文件和一份 `.github/product.json`，发现、构建、打包的全部逻辑都在本仓库。发布到 GitHub Releases 的示例固件来自该工作流，不通过手工编译产生。

## 产品仓库如何调用

```yaml
on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
  workflow_dispatch:
jobs:
  build:
    uses: waveshareteam/esp32-repo-template/.github/workflows/build.yml@v1
    with:
      examples: ${{ inputs.examples || 'all' }}
    permissions:
      contents: write
    secrets: inherit
```

完整文件见 [`skeleton/.github/workflows/build.yml`](../skeleton/.github/workflows/build.yml)。push 只在 `main` 和 `v*` 标签上触发，拉取请求由 `pull_request` 构建，同一次改动不会构建两遍。`contents: write` 只给打标签时创建草稿 Release 的任务使用，其他任务只读。

| 输入 | 默认值 | 说明 |
| --- | --- | --- |
| `examples` | `all` | 手动触发时的选择器：`all`、示例目录名或仓库相对路径，可用逗号分隔多个 |
| `template_repository` | `waveshareteam/esp32-repo-template` | 提供 `ci/` 和 `defaults/` 的仓库 |
| `template_ref` | `v1` | 检出模板仓库的 ref，必须与 `uses: ...@<ref>` 保持一致 |

工作流的每个任务都会先检出产品仓库，再把模板仓库检出到 `.ci-template/`，然后运行其中的 `ci/*.py`。

## 配置来源

| 配置 | 来源 |
| --- | --- |
| 产品名、ESP-IDF target、ESP-IDF 版本、Arduino core、Arduino FQBN | 产品仓库的 `.github/product.json` |
| 变更路由规则 | 本仓库的 `defaults/ci-routing.json` |
| Markdown 审计规则 | 本仓库的 `defaults/markdown-audit.json` |
| 单个产品的例外 | `product.json` 的 `overrides.ci_routing`、`overrides.markdown_audit` |

`overrides` 的合并规则：列表追加到默认列表之后（去重），其他类型的值直接替换默认值。`product.json` 的字段定义见 [`schema/product.schema.json`](../schema/product.schema.json)。工作流和脚本里不写任何框架版本、target 或 FQBN。

## 发现边界

- ESP-IDF 工程是 `examples/esp-idf/` 下同时包含 `CMakeLists.txt` 和 `main/` 的直接子目录。
- Arduino 草图是 `examples/arduino/examples/` 下包含顶层 `.ino` 文件的第一方目录。
- `examples/arduino/libraries/**` 和本地组件自带的示例被排除。
- `product.json` 没有 `esp_idf` 或 `arduino` 字段时，对应框架不构建。
- 出厂固件是 `firmware/sourcecode/` 这一个 ESP-IDF 工程，只在 `product.json` 有 `factory_firmware` 时构建，使用其中指定的那一个 ESP-IDF 版本。

## 构建矩阵

矩阵大小 = ESP-IDF 工程数 × `esp_idf.versions` 的个数 + Arduino 草图数，有出厂固件时再加 1。

完整工作流包含一个轻量的分类任务、两个发现任务、矩阵里的全部构建/打包任务、出厂固件构建任务，以及只在 `v*` 标签上运行的草稿 Release 任务。矩阵任务不启用快速失败（`fail-fast: false`），单个任务失败不会隐藏其他示例的结果。

## 变更路由

每个拉取请求和 `main` 推送先运行分类任务。分类任务先校验 `product.json`，再用能识别重命名的分类器处理完整的 base/head 差异。差异不可用或为空时，分类任务直接失败，不会退化成「全部构建」或「全部跳过」。新仓库的第一次推送没有上一个提交可比，这时构建全部。

| 改动 | 结果 |
| --- | --- |
| Markdown、文档图片、LICENSE、`firmware/*.bin` 等 | 不启动示例构建 |
| 某个示例的源码或配置 | 只构建该示例 |
| `examples/arduino/libraries/**` | 构建全部 Arduino 草图 |
| `firmware/sourcecode/**` | 只构建出厂固件 |
| `.github/**`（含 `product.json` 和调用工作流） | 构建完整矩阵 |
| 无法归类的非文档路径 | 构建完整矩阵，并在结果中列出 |
| 手动触发、`v*` 标签 | 构建完整矩阵和出厂固件；`v*` 标签再创建草稿 Release |

## 产物约定

每个成功构建上传一个 `*-combined.zip`，格式见[发布](release.md#固件包格式)。

## 版本策略

CI 跟踪 ESP-IDF v5.5 系列的最新稳定补丁版、最新稳定 ESP-IDF v6 版本，以及最新稳定 Arduino-ESP32 版本。升级时修改产品仓库的 `product.json`，并完成以下工作：

1. 审查上游发布说明和迁移指南。
2. 运行完整 CI 矩阵。
3. 对受影响的示例进行硬件验证。
4. 更新产品 README 的版本表和 GitHub Release 说明。

## 模板自测

`.github/workflows/self-test.yml` 在本仓库运行 `python -m pytest tests/`。测试以 `tests/fixtures/` 和 `skeleton/` 为输入，不依赖任何产品仓库。

需要核对某个产品仓库的真实文件时，设置环境变量 `PRODUCT_REPO` 再运行测试：

```bash
PRODUCT_REPO=/path/to/product-repo python -m pytest tests/
```

设置 `PRODUCT_REPO` 后，测试额外检查该产品仓库的 `product.json` 和 README 首页结构。`tests/contracts/<产品名>.json` 存在时，测试还会检查其中记录的引脚契约。
