# esp32-repo-template

本仓库是 Waveshare ESP32 产品仓库的统一模板，集中存放 CI、发布工具、规范文档和新仓库骨架。产品仓库的目录规范、CI 规则和发布规则以本仓库为准。

## 仓库分工

产品仓库只放用户关心的内容（示例、原理图、README）和一份 `.github/product.json`。维护者使用的其余内容集中在本仓库，产品仓库通过一个约 10 行的工作流调用：

| 仓库 | 存放内容 |
| --- | --- |
| 产品仓库 | 示例、硬件资料、README、`.github/product.json`、调用工作流 |
| `waveshareteam/esp32-repo-template`（本仓库） | CI、脚本、测试、规范文档、骨架 |
| `waveshareteam/.github` | CONTRIBUTING、SUPPORT、SECURITY、issue 和 PR 模板，组织下的仓库自动继承 |

## 目录

| 路径 | 内容 |
| --- | --- |
| `.github/workflows/build.yml` | 可复用工作流：变更分类、示例发现、矩阵构建、出厂固件构建、固件打包、打标签时创建草稿 Release |
| `.github/workflows/self-test.yml` | 在本仓库运行 `tests/` |
| `ci/` | 工作流和发布流程用到的 Python 脚本（只依赖标准库） |
| `schema/product.schema.json` | `product.json` 的 JSON Schema |
| `defaults/` | 变更路由和 Markdown 审计的默认规则 |
| `skeleton/` | 新建仓库或迁移旧仓库时复制的骨架 |
| `tests/` | 脚本、工作流和骨架的自测 |
| `docs/` | [规范](docs/spec.md)、[CI](docs/ci.md)、[发布](docs/release.md) |

## 接入产品仓库

1. 把 [`skeleton/`](skeleton/) 里的文件复制到产品仓库的对应位置：

   | 骨架文件 | 复制到 |
   | --- | --- |
   | `skeleton/.github/workflows/build.yml` | `.github/workflows/build.yml`（不需要修改） |
   | `skeleton/.github/product.json` | `.github/product.json` |
   | `skeleton/README.md`、`skeleton/README_ZH.md` | 仓库根目录 |
   | `skeleton/example-README.md`、`skeleton/example-README_ZH.md` | 每个示例目录，改名为 `README.md`、`README_ZH.md` |
   | `skeleton/firmware-README.md`、`skeleton/firmware-README_ZH.md` | `firmware/`，改名为 `README.md`、`README_ZH.md`；没有实测固件时不建 `firmware/` |
   | `skeleton/.gitignore` | 仓库根目录 |

2. 填写 `.github/product.json`，把所有 `<...>` 占位符换成实际值：

   | 字段 | 含义 |
   | --- | --- |
   | `product` | 产品型号，用作固件包名前缀 |
   | `product_url` | 官方产品页 |
   | `tier` | 仓库达到的级别：0、1 或 2，定义见[规范](docs/spec.md#级别) |
   | `target` | ESP-IDF target，例如 `esp32s3` |
   | `esp_idf.versions` | 要构建的 ESP-IDF 版本标签；没有 ESP-IDF 示例时删除 `esp_idf` |
   | `arduino.core`、`arduino.fqbn` | Arduino-ESP32 版本和完整 FQBN；没有 Arduino 示例时删除 `arduino` |
   | `factory_firmware.esp_idf` | 构建 `examples/factory/` 出厂固件源码的 ESP-IDF 版本；出厂固件不开源时删除 `factory_firmware`，见[发布](docs/release.md#出厂固件) |
   | `overrides` | 可选，对 `defaults/` 的补充，见 [CI 文档](docs/ci.md#配置来源) |

3. 按[目录规范](docs/spec.md#目录规范)整理示例和硬件资料，填写两份 README。
4. 在本仓库的检出目录里校验配置：

   ```bash
   python ci/product_config.py --product /path/to/product-repo/.github/product.json
   PRODUCT_REPO=/path/to/product-repo python -m pytest tests/
   ```

5. 推送到产品仓库。产品仓库的 `Build` 工作流随后按 `product.json` 构建全部示例并打包固件。发布时打 `v*` 标签，流程见[发布](docs/release.md#发布流程)。

## 开发本仓库

```bash
python -m pip install pytest jsonschema
python -m pytest tests/
```

`jsonschema` 是可选依赖。未安装 `jsonschema` 时，用它校验 Schema 的那一项测试会跳过；其余测试只依赖标准库。

修改工作流或脚本后需要移动 `v1` 标签，产品仓库才会用到新版本。不兼容的改动应发布新的主版本标签，让产品仓库逐个升级。
