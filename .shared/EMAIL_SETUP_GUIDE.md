# 邮件推送配置指南

本指南将帮助你配置邮件推送功能，自动接收每日 AI 报告。

---

## 📋 目录

1. [快速开始](#快速开始)
2. [配置 SMTP](#配置-smtp)
3. [常见邮箱配置](#常见邮箱配置)
4. [测试邮件发送](#测试邮件发送)
5. [自动化推送](#自动化推送)
6. [故障排查](#故障排查)

---

## 🚀 快速开始

### 第 1 步：安装依赖

```bash
cd /Users/shenbo/Desktop/mind/.shared
pip install pyyaml markdown
```

### 第 2 步：配置邮箱信息

编辑 `.shared/config.yaml`，找到 `email` 部分并配置：

```yaml
email:
  enabled: true  # 启用邮件推送

  smtp:
    host: "smtp.example.com"  # 替换为你的 SMTP 服务器
    port: 587
    use_tls: true

  sender:
    email: "your-email@example.com"  # 你的邮箱
    password: ""                      # 留空，使用环境变量
    name: "Mind AI Report"

  recipients:
    - "your-email@example.com"  # 接收报告的邮箱
```

### 第 3 步：设置邮箱密码（推荐使用环境变量）

**方式 A：临时设置（当前会话有效）**
```bash
export MIND_EMAIL_PASSWORD="your-password-or-app-password"
```

**方式 B：永久设置（添加到 ~/.zshrc 或 ~/.bash_profile）**
```bash
echo 'export MIND_EMAIL_PASSWORD="your-password-or-app-password"' >> ~/.zshrc
source ~/.zshrc
```

⚠️ **安全提示**：强烈建议使用**应用专用密码**而不是邮箱登录密码！

---

## 📧 配置 SMTP

### 什么是 SMTP？

SMTP（Simple Mail Transfer Protocol）是发送邮件的协议。你需要配置：

- **host**: SMTP 服务器地址
- **port**: 端口号（通常是 587 或 465）
- **use_tls**: 是否使用 TLS 加密（587 端口用 TLS）
- **use_ssl**: 是否使用 SSL 加密（465 端口用 SSL）

---

## 🔑 常见邮箱配置

### 1. Gmail

**配置**:
```yaml
smtp:
  host: "smtp.gmail.com"
  port: 587
  use_tls: true
  use_ssl: false
```

**获取应用专用密码**:
1. 访问 [Google Account Security](https://myaccount.google.com/security)
2. 启用"两步验证"
3. 在"应用专用密码"中生成新密码
4. 使用该密码作为 `MIND_EMAIL_PASSWORD`

---

### 2. QQ 邮箱

**配置**:
```yaml
smtp:
  host: "smtp.qq.com"
  port: 587
  use_tls: true
  use_ssl: false
```

**获取授权码**:
1. 登录 [QQ 邮箱](https://mail.qq.com/)
2. 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启"SMTP服务"
4. 生成授权码
5. 使用授权码作为 `MIND_EMAIL_PASSWORD`

---

### 3. 163 邮箱

**配置**:
```yaml
smtp:
  host: "smtp.163.com"
  port: 465
  use_tls: false
  use_ssl: true
```

**获取授权码**:
1. 登录 [163 邮箱](https://mail.163.com/)
2. 设置 → POP3/SMTP/IMAP
3. 开启"SMTP服务"
4. 获取授权码
5. 使用授权码作为 `MIND_EMAIL_PASSWORD`

---

### 4. Outlook / Hotmail

**配置**:
```yaml
smtp:
  host: "smtp-mail.outlook.com"
  port: 587
  use_tls: true
  use_ssl: false
```

**使用账号密码或应用密码**:
- 如果启用了两步验证，需要生成应用密码
- 访问 [Microsoft Account Security](https://account.microsoft.com/security)

---

### 5. iCloud 邮箱

**配置**:
```yaml
smtp:
  host: "smtp.mail.me.com"
  port: 587
  use_tls: true
  use_ssl: false
```

**获取应用专用密码**:
1. 访问 [Apple ID](https://appleid.apple.com/)
2. 安全 → 应用专用密码
3. 生成新密码

---

## 🧪 测试邮件发送

### 手动测试

发送今天的 Claude Code 报告：

```bash
cd /Users/shenbo/Desktop/mind

# 设置密码（如果还没设置）
export MIND_EMAIL_PASSWORD="your-app-password"

# 发送邮件
python .shared/email_sender.py --report cc/2025-10-28/index.md --type ccnews
```

发送 AI 全景报告：

```bash
python .shared/email_sender.py --report ainews/2025-10-28/index.md --type ainews
```

### 查看日志

```bash
# 查看邮件发送日志
cat .shared/logs/email.log

# 实时监控
tail -f .shared/logs/email.log
```

---

## ⚙️ 自动化推送

### 方式 1: 手动触发（报告生成后立即发送）

生成报告后手动发送邮件：

```bash
# 生成 ccnews 报告
/ccnews

# 发送邮件
python .shared/email_sender.py --report cc/$(date +%Y-%m-%d)/index.md --type ccnews
```

---

### 方式 2: 集成到调度脚本（推荐）

调度脚本 `.shared/scheduler.sh` 已经集成了邮件发送功能。

**使用方法**:
```bash
cd /Users/shenbo/Desktop/mind

# 设置密码
export MIND_EMAIL_PASSWORD="your-app-password"

# 运行调度（自动发送邮件）
./.shared/scheduler.sh ccnews
```

---

### 方式 3: 定时任务（crontab）

设置每天自动生成并发送报告：

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天早上 9 点）
0 9 * * * export MIND_EMAIL_PASSWORD="your-password" && cd /Users/shenbo/Desktop/mind && ./.shared/scheduler.sh ccnews >> .shared/logs/cron.log 2>&1
```

**完整示例**:
```cron
# Mind AI 报告自动推送
MIND_EMAIL_PASSWORD=your-app-password

# Claude Code 日报（每天 9:00）
0 9 * * * cd /Users/shenbo/Desktop/mind && ./.shared/scheduler.sh ccnews

# AI 全景报告（每天 10:00）
0 10 * * * cd /Users/shenbo/Desktop/mind && ./.shared/scheduler.sh ainews
```

---

## 🔧 故障排查

### 问题 1: "SMTP 认证失败"

**可能原因**:
- 密码错误
- 未使用应用专用密码
- SMTP 服务未开启

**解决方法**:
1. 检查 `MIND_EMAIL_PASSWORD` 是否正确
2. 确认使用的是**授权码/应用密码**而非登录密码
3. 检查邮箱是否开启了 SMTP 服务

---

### 问题 2: "连接超时"

**可能原因**:
- SMTP 服务器地址或端口错误
- 防火墙阻止
- 网络问题

**解决方法**:
1. 检查 `config.yaml` 中的 `host` 和 `port`
2. 测试网络连接：
   ```bash
   telnet smtp.gmail.com 587
   ```
3. 检查防火墙设置

---

### 问题 3: "邮件未收到"

**可能原因**:
- 邮件进入垃圾箱
- 收件人地址错误
- 邮件被拦截

**解决方法**:
1. 检查垃圾邮件文件夹
2. 确认 `config.yaml` 中的 `recipients` 正确
3. 查看发送日志：
   ```bash
   cat .shared/logs/email.log
   ```

---

### 问题 4: "HTML 格式不正确"

**解决方法**:
1. 检查是否安装了 `markdown` 库：
   ```bash
   pip install markdown
   ```
2. 尝试使用纯文本格式：
   ```yaml
   content:
     format: "plain"  # 使用纯文本
   ```

---

## 📊 高级配置

### 多个收件人

```yaml
recipients:
  - "email1@example.com"
  - "email2@example.com"
  - "team@company.com"
```

### 自定义邮件主题

```yaml
content:
  subject_prefix: "[AI Daily]"  # 自定义前缀
```

### 附加 Markdown 原文

```yaml
content:
  attach_markdown: true  # 邮件附带 .md 文件
```

### 按需发送

只发送 Claude Code 报告，不发送 AI 全景报告：

```yaml
content:
  send_ccnews: true
  send_ainews: false
```

---

## 🎉 完成！

配置完成后，你将每天自动收到精美的 HTML 格式 AI 报告邮件！

---

## 📞 需要帮助？

如果遇到问题，请检查：
1. `.shared/logs/email.log` - 邮件发送日志
2. `.shared/logs/scheduler.log` - 调度脚本日志
3. 邮箱的垃圾邮件文件夹

---

*最后更新: 2025-10-28*
