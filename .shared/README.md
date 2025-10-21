# .shared/ - 共享工具和配置

这个目录包含 Mind 项目的共享工具、配置和脚本。

---

## 📁 目录结构

```
.shared/
├── config.yaml           # 全局配置文件
├── logger.py             # 统一日志工具
├── scheduler.sh          # 自动化调度脚本
├── crontab.example       # crontab 配置示例
├── quality_check.py      # 报告质量检查工具
├── backup.sh             # 数据库备份脚本
├── logs/                 # 日志目录
├── backups/              # 备份目录
└── README.md             # 本文件
```

---

## 🚀 快速开始

### 1. 配置全局参数
编辑 `config.yaml`:
```yaml
ccnews:
  github:
    repo: "anthropics/claude-code"
    lookback_days: 3
```

### 2. 使用日志工具
```python
from .shared.logger import get_logger

logger = get_logger('ccnews')
logger.info("开始执行")
```

### 3. 自动化调度
```bash
# 手动运行
./scheduler.sh ccnews  # 生成 CC 日报
./scheduler.sh ainews  # 生成 AI 报告
./scheduler.sh both    # 生成两个报告

# 设置定时任务
crontab crontab.example
```

### 4. 质量检查
```bash
python quality_check.py ../cc/2025-10-18/index.md ccnews
```

### 5. 数据库备份
```bash
./backup.sh
```

---

## 🛠️ 工具说明

### config.yaml
- **用途**: 统一配置管理
- **优势**: 消除硬编码，便于维护
- **修改**: 直接编辑 YAML 文件

### logger.py
- **功能**: 分级日志、文件轮转
- **日志位置**: `{module}/.meta/logs/`
- **轮转策略**: 5MB，保留 5 个备份

### scheduler.sh
- **功能**: 自动化报告生成、清理
- **模式**:
  - `ccnews` - 仅 CC 日报
  - `ainews` - 仅 AI 报告
  - `both` - 两个都生成
  - `cleanup` - 清理旧报告

### quality_check.py
- **检查项**:
  - 行数（80-120）
  - 必需章节
  - 数据来源
  - 评论引用（ccnews）
  - 元数据

### backup.sh
- **备份**: ccnews.db
- **压缩**: 7 天后
- **删除**: 30 天后

---

## 📝 最佳实践

1. **日志**: 所有脚本统一使用 `logger.py`
2. **配置**: 从 `config.yaml` 读取参数
3. **调度**: 通过 `scheduler.sh` 统一调度
4. **质量**: 每次生成后运行质量检查
5. **备份**: 每日自动备份数据库

---

## 🔧 维护

### 查看日志
```bash
tail -f logs/scheduler.log
tail -f ../cc/.meta/logs/ccnews.log
```

### 查看备份
```bash
ls -lh backups/
```

### 手动清理
```bash
./scheduler.sh cleanup
```

---

## 📞 支持

如有问题，请查看:
- 项目主 README: `../README.md`
- 优化文档: `../OPTIMIZATION.md`
- CC 模块文档: `../cc/README.md`
- AI 模块文档: `../ainews/README.md`
