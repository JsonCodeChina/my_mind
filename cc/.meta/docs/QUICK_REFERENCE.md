# ccnews 快速参考卡 v2.0

## 🚀 一键运行

```bash
/ccnews
```

## 📁 关键文件

| 文件 | 说明 | 位置 |
|------|------|------|
| **config.json** | 配置文件 | `cc/config.json` |
| **baseline.json** | 基线数据 | `cc/baseline.json` |
| **ccnews.md** | 命令文件 | `.claude/commands/ccnews.md` |
| **index.html** | 主页面 | `cc/YYYY-MM-DD/index.html` |
| **README.md** | 系统说明 | `cc/README.md` |

## ⚙️ 快速配置

### 添加新数据源

编辑 `cc/config.json`：

```json
{
  "dataSources": {
    "community": [
      {
        "name": "新数据源",
        "url": "https://example.com",
        "priority": "high",
        "type": "documentation"
      }
    ]
  }
}
```

### 修改显示数量

```json
{
  "display": {
    "topFeaturesCount": 5,      // 热门功能数量
    "topArticlesCount": 4,       // 精选文章数量
    "topCommunityTopics": 5      // 社区热点数量
  }
}
```

### 禁用自动打开浏览器

```json
{
  "output": {
    "autoOpenBrowser": false
  }
}
```

## 📂 输出结构

```
cc/YYYY-MM-DD/
├── index.html                 ⭐ 主页面
├── community-trends.html      🔥 社区趋势
├── QUICK_VIEW.md              📋 快速浏览
├── README.md                  📖 说明
└── details/                   📁 详细内容
    ├── DETAILS.md
    ├── updates.md
    ├── all-articles.md
    └── ...
```

## 🎯 常用操作

### 查看今日资讯

```bash
open cc/$(date +%Y-%m-%d)/index.html
```

### 查看快速概览

```bash
cat cc/$(date +%Y-%m-%d)/QUICK_VIEW.md
```

### 查看社区趋势

```bash
open cc/$(date +%Y-%m-%d)/community-trends.html
```

### 查看配置

```bash
cat cc/config.json | jq .
```

### 查看基线数据

```bash
cat cc/baseline.json | jq .
```

## 🔧 故障排除

### 网络问题

```bash
# 检查网络连接
ping docs.claude.com

# 检查失败的 URL
cat cc/$(date +%Y-%m-%d)/details/resources.md
```

### 权限问题

```bash
# 检查目录权限
ls -la cc/

# 修复权限
chmod -R 755 cc/
```

### 配置问题

```bash
# 验证 JSON 格式
cat cc/config.json | jq .

# 重置为默认配置
cp cc/config.json cc/config.json.backup
# 然后手动编辑恢复
```

## 📊 版本信息

### 查看当前版本

```bash
cat cc/baseline.json | jq .claudeCodeVersion
```

### 查看上次检查日期

```bash
cat cc/baseline.json | jq .lastCheckDate
```

### 查看系统版本

```bash
head -1 cc/README.md
```

## 🎨 自定义主题

### 修改颜色

编辑 `cc/templates/index-template.html` 的 CSS 变量：

```css
:root {
    --primary: #000000;      /* 主色 */
    --accent: #d32f2f;       /* 强调色 */
    --bg: #fafafa;           /* 背景色 */
    /* ... */
}
```

### 修改字体

```css
body {
    font-family: 'Georgia', 'Times New Roman', serif;
}
```

## 📈 性能优化

### 减少爬取的数据源

编辑 `config.json`，将不需要的数据源的 `priority` 设为 `"low"` 或删除。

### 减少重试次数

```json
{
  "features": {
    "maxRetries": 1
  }
}
```

### 禁用某些功能

```json
{
  "features": {
    "communityAnalysis": false,  // 禁用社区分析
    "versionTracking": true
  }
}
```

## 🔗 快捷链接

### 官方资源

- **官方文档**: https://docs.claude.com/en/docs/claude-code/overview
- **更新日志**: https://claudelog.com/claude-code-changelog/
- **GitHub**: https://github.com/anthropics/claude-code

### 社区资源

- **社区文档**: https://cc.deeptoai.com/docs
- **Hacker News**: https://news.ycombinator.com/
- **Reddit**: https://www.reddit.com/r/ClaudeAI/

## 💡 使用技巧

### 1. 每日自动化

创建 cron 任务（macOS/Linux）：

```bash
# 每天早上 9 点运行
0 9 * * * cd /Users/shenbo && claude /ccnews
```

### 2. 快速查看今日内容

创建别名（~/.zshrc 或 ~/.bashrc）：

```bash
alias cctoday='open ~/Desktop/mind/cc/$(date +%Y-%m-%d)/index.html'
alias ccview='cat ~/Desktop/mind/cc/$(date +%Y-%m-%d)/QUICK_VIEW.md'
```

### 3. 对比版本

```bash
# 查看基线版本
cat cc/baseline.json | jq .claudeCodeVersion

# 查看今日检测的版本
cat cc/$(date +%Y-%m-%d)/details/updates.md
```

### 4. 搜索历史

```bash
# 搜索所有日期的文件
find cc/ -name "index.html"

# 搜索特定关键词
grep -r "特定功能" cc/*/details/
```

## 📝 更新记录

| 版本 | 日期 | 主要变化 |
|------|------|----------|
| v2.0.0 | 2025-10-13 | 配置文件化、模块化、优化布局 |
| v1.0.0 | 2025-10-12 | 初始版本 |

## 🆘 获取帮助

### 查看完整文档

```bash
cat cc/README.md
```

### 查看更新日志

```bash
cat cc/CHANGELOG.md
```

### 查看命令说明

```bash
cat .claude/commands/ccnews.md
```

---

📅 版本：v2.0.0
📆 更新：2025-10-13
📖 完整文档：cc/README.md
