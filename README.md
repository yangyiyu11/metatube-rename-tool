# metatube-rename-tool

`metatube_rename.py` - 一个简单高效的命令行工具，用于根据文件名称中的AV番号自动重命名文件。

## 功能特性

- 自动从文件名中提取各种格式的番号，如 `ABC-123`、`ABC123` 等
- 支持处理带域名、特殊标记的复杂文件名
- 保持文件扩展名不变
- 避免文件名冲突
- 支持递归处理子目录
- 提供模拟运行模式，安全预览重命名结果

## TODO

- [x] 增加对常见番号格式的支持
- [ ] 增加对其他番号格式的支持
- [ ] 增加对自定义重命名规则的支持

## 安装

该工具使用Python标准库开发，无需安装额外依赖。只需确保您的系统已安装Python 3.6或更高版本。

## 使用方法

直接运行 `metatube_rename.py`

```bash
# 基本使用 - 处理当前目录中的文件
python metatube_rename.py

# 指定目录
python metatube_rename.py /path/to/directory

# 递归处理子目录
python metatube_rename.py -r /path/to/directory

# 模拟运行（不实际重命名文件）
python metatube_rename.py -d /path/to/directory

# 组合使用 - 递归处理并模拟运行
python metatube_rename.py -rd /path/to/directory
```

## 工作原理

该工具通过正则表达式从文件名中识别常见的AV番号格式，然后将文件重命名为标准格式的番号加上原始扩展名。

### 支持的番号格式

- 标准格式：`ABC-123`、`abc-123`
- 无分隔符格式：`ABC123`、`abc123`
- 数字在前格式：`123ABC`、`123abc`

### 安全机制

1. 如果目标文件已存在，将自动添加数字后缀（如`ABC123_1.mp4`）以避免覆盖
2. 对于无法识别番号的文件，将保留原样并在输出中标记为跳过

## 注意事项

- 该工具仅处理文件，不会修改目录名称
- 使用时请确保您有足够的文件系统权限
- 建议在执行重命名操作前，先使用模拟运行模式（`-d`参数）预览结果