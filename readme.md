# Auto Save Code

Auto Save Code 是一个为 claude 设计的代码保存工具，用于从claude生成的项目文件中自动保存和管理 AI 生成的代码。本工具极大地提高了 AI 辅助编程过程中的代码管理效率，使开发者能够更专注于创意和问题解决。
请把生成的文件都放在同一个工作文件夹中，所有文件中只包含一个文档结构内容，其他代码相关内容，默认同文件结构保持一致。
界面是tk写的，比较简陋，将就看吧。

## 目录
1. [主要功能](#主要功能)
2. [安装指南](#安装指南)
3. [详细使用说明](#详细使用说明)
4. [代码格式要求](#代码格式要求)
5. [文件结构要求](#文件结构要求)
6. [支持的文本格式及调整方法](#支持的文本格式及调整方法)
7. [配置说明](#配置说明)
8. [性能优化](#性能优化)
9. [常见问题解答](#常见问题解答)
10. [贡献指南](#贡献指南)
11. [版本历史](#版本历史)
12. [许可证](#许可证)

## 主要功能

1. **智能代码块检测**：自动识别并提取 AI 生成的代码块。
2. **项目结构提取**：生成清晰的项目文件结构树。
3. **多文件类型支持**：灵活处理各种文本文件格式。
4. **用户友好的图形界面**：直观操作，实时反馈。
5. **详细的执行日志**：全面记录处理过程。
6. **代码块元数据提取**：提取并保存代码相关信息。
7. **灵活的配置选项**：通过配置文件自定义程序行为。
8. **代码块保存和组织**：按项目结构保存提取的代码块。
9. **统计信息生成**：提供处理结果的量化指标。

## 安装指南

1. **克隆仓库**：
   ```
   git clone https://github.com/YourUsername/auto_save_code.git
   cd auto_save_code
   ```

2. **创建虚拟环境**（推荐）：
   ```
   python -m venv venv
   source venv/bin/activate  # 在 Windows 上使用 venv\Scripts\activate
   ```

3. **安装依赖**：
   ```
   pip install -r requirements.txt
   ```

## 详细使用说明

1. **启动程序**：
   ```
   python main.py
   ```

2. **图形界面操作**：
   - 选择输入目录和输出目录
   - 指定要处理的文件类型
   - 点击 "执行" 开始处理
   - 查看实时进度和日志信息

3. **查看结果**：
   - 在输出目录中查看保存的代码块文件
   - 检查生成的处理报告

## 代码格式要求

为确保 Auto Save Code 能够正确识别和提取代码块，请遵循以下格式要求：

1. **代码块标记**：
   - 开始标记：```language:path/to/file
   - 结束标记：```
   例如：
   ````
   ```python:/src/main.py
   def hello_world():
       print("Hello, World!")
   ```
   ````

2. **语言指定**：
   - 在开始标记中明确指定编程语言
   - 支持的语言包括但不限于：python, javascript, html, css, java, c, cpp

3. **文件路径**：
   - 在开始标记中指定代码块所属的文件路径
   - 路径应该是相对于项目根目录的路径

4. **代码内容**：
   - 保持原有的缩进和格式
   - 可以包含注释

5. **未更改代码标记**：
   - 使用 `// ... existing code ...` 表示省略的未更改代码

6. **多个代码块**：
   - 不同代码块之间应有明确的分隔，如空行或注释

## 文件结构要求

Auto Save Code 对项目的文件结构有一定的要求，以确保最佳的处理效果：

1. **项目根目录**：
   - 应包含主要的源代码文件夹（如 `src`, `lib`, `include` 等）
   - 配置文件（如 `config.yaml`）应放在根目录下

2. **源代码组织**：
   - 建议按功能或模块组织源代码文件
   - 保持清晰的目录结构，避免过深的嵌套

3. **资源文件**：
   - 将非代码文件（如图片、数据文件等）放在单独的目录中（如 `resources`, `assets`）

4. **输出目录**：
   - 程序会在指定的输出目录中创建与输入结构相匹配的目录树
   - 确保输出目录有足够的写入权限

5. **文件命名**：
   - 使用有意义的文件名
   - 避免使用空格和特殊字符，推荐使用下划线或驼峰命名

6. **版本控制**：
   - 如果使用版本控制系统，确保 `.gitignore`（或类似文件）正确配置，以排除不必要的文件

## 支持的文本格式及调整方法

Auto Save Code 默认支持多种文本文件格式，您也可以根据需要进行调整：

1. **默认支持的格式**：
   - Python (.py)
   - JavaScript (.js)
   - HTML (.html)
   - CSS (.css)
   - Markdown (.md)
   - Text (.txt)

2. **调整支持的格式**：
   - 打开 `config.yaml` 文件
   - 找到 `file_types` 部分
   - 修改 `types` 字段，添加或删除文件扩展名
   例如：
   ```yaml
   file_types:
     types: "py,js,html,css,md,txt,java,c,cpp"
   ```

3. **添加新的文件类型**：
   - 在 `config.yaml` 中添加新的文件扩展名
   - 如果新文件类型需要特殊处理，可能需要修改 `code_block_detector.py`

4. **自定义文件类型处理**：
   - 对于特殊的文件类型，您可以在 `code_block_detector.py` 中添加自定义的检测逻辑
   - 在 `detect_code_blocks` 方法中增加对新文件类型的支持

5. **文件编码**：
   - 程序默认使用 UTF-8 编码读取文件
   - 如果需要支持其他编码，可以修改 `utils.py` 中的文件读取函数

## 配置说明

`config.yaml` 文件允许您自定义程序的行为。以下是主要的配置选项：

```yaml
code_block_detection:
  start_marker: "```"
  end_marker: "```"
  min_occurrences: 2
  indentation_level: 4

file_types:
  types: "py,js,html,css,md,txt"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

gui:
  window_title: "Auto Save Code"
  window_size: "800x600"

processing:
  max_file_size: 10485760  # 10MB in bytes
  thread_count: 4
```

- `code_block_detection`: 定义代码块的检测参数
- `file_types`: 指定要处理的文件类型
- `logging`: 配置日志记录的级别和格式
- `gui`: 设置图形界面的属性
- `processing`: 控制文件处理的相关参数

## 性能优化

为了提高 Auto Save Code 的处理效率，可以考虑以下优化措施：

1. **增加处理线程**：
   - 在 `config.yaml` 中调整 `processing.thread_count`
   - 根据您的 CPU 核心数来设置，通常设置为 CPU 核心数的 1-2 倍

2. **调整最大文件大小**：
   - 修改 `config.yaml` 中的 `processing.max_file_size`
   - 增大此值可以处理更大的文件，但可能会影响性能

3. **优化文件读取**：
   - 对于大文件，考虑使用流式读取而不是一次性加载整个文件
   - 可以在 `code_block_detector.py` 中实现这一优化

4. **缓存机制**：
   - 实现一个简单的缓存系统，避免重复处理相同的文件
   - 可以在 `code_block_processor.py` 中添加缓存逻辑

5. **并行处理**：
   - 考虑使用 Python 的 `multiprocessing` 模块进行并行处理
   - 这对于处理大量小文件特别有效

6. **代码优化**：
   - 使用性能分析工具找出程序的瓶颈
   - 优化关键路径上的代码，如使用更高效的数据结构或算法

## 常见问题解答

1. Q: 如何处理超大项目？
   A: 对于超大项目，建议分批处理文件，或增加处理线程数。也可以考虑使用 `multiprocessing` 进行并行处理。

2. Q: 程序卡在某个文件上怎么办？
   A: 检查该文件是否符合格式要求，或者文件是否损坏。可以尝试增加超时机制来跳过问题文件。

3. Q: 如何自定义代码块的保存格式？
   A: 修改 `code_block_processor.py` 中的 `save_code_blocks` 方法来自定义保存逻辑。

4. Q: 支持增量更新吗？
   A: 当前版本不支持增量更新。您可以通过实现文件哈希比较来添加这个功能。

5. Q: 如何处理加密或压缩的文件？
   A: 当前版本不直接支持加密或压缩文件。您需要先解密或解压文件，然后再进行处理。

## 贡献指南

我们欢迎并感谢任何形式的贡献！如果您想为 Auto Save Code 项目做出贡献，请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 将您的更改推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

对于重大更改，请先开issue讨论您想要改变的内容。

## 版本历史

- 1.0.0
  - 初始发布
  - 基本的代码块检测和保存功能
- 1.1.0
  - 添加了项目结构提取功能
  - 改进了GUI界面
- 1.2.0
  - 增加了代码块元数据提取功能
  - 优化了文件处理逻辑
- 1.3.0
  - 添加了多线程支持
  - 改进了配置系统
- 1.4.0
  - 增加了对更多文件类型的支持
  - 优化了内存使用

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

---

我们希望这个详细的 README 文件能够帮助您更好地理解和使用 Auto Save Code 工具。如果您有任何问题或建议，请随时联系我们或提交 issue。祝您使用愉快！