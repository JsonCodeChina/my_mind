# 邮件推送快速开始 ⚡

## 3 步配置，5 分钟搞定！

---

## 步骤 1: 安装依赖 (30 秒)

```bash
pip install pyyaml markdown
```

---

## 步骤 2: 配置邮箱 (2 分钟)

编辑 `.shared/config.yaml`:

```yaml
email:
  enabled: true  # 🔥 启用邮件

  smtp:
    host: "smtp.qq.com"      # 你的 SMTP 服务器
    port: 587
    use_tls: true

  sender:
    email: "your@qq.com"     # 你的邮箱
    name: "Mind AI Report"

  recipients:
    - "your@qq.com"          # 接收邮箱（可以是自己）
```

**常用 SMTP 配置**:
- **Gmail**: `smtp.gmail.com:587`
- **QQ**: `smtp.qq.com:587`
- **163**: `smtp.163.com:465` (use_ssl: true)
- **Outlook**: `smtp-mail.outlook.com:587`

---

## 步骤 3: 设置密码 (1 分钟)

### 获取应用密码

**QQ 邮箱**:
1. 打开 [QQ 邮箱](https://mail.qq.com/) → 设置 → 账户
2. 开启 "SMTP 服务"
3. 生成授权码 → 复制

**Gmail**:
1. 访问 [Google Account](https://myaccount.google.com/security)
2. 启用"两步验证"
3. 生成"应用专用密码"

### 设置环境变量

```bash
# 临时设置
export MIND_EMAIL_PASSWORD="你的授权码"

# 或永久设置（添加到 ~/.zshrc）
echo 'export MIND_EMAIL_PASSWORD="你的授权码"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🧪 测试发送

```bash
cd /Users/shenbo/Desktop/mind

# 发送今天的报告
python .shared/email_sender.py --report cc/2025-10-28/index.md --type ccnews
```

**成功标志**: 看到 `✓ 邮件发送成功！`

---

## 🚀 自动化推送

### 方式 1: 手动触发

```bash
# 生成报告后发送
/ccnews
python .shared/email_sender.py --report cc/$(date +%Y-%m-%d)/index.md --type ccnews
```

### 方式 2: 使用调度脚本（推荐）

```bash
./.shared/scheduler.sh ccnews  # 自动生成 + 发送
```

### 方式 3: 定时任务

```bash
crontab -e
```

添加:
```cron
MIND_EMAIL_PASSWORD=你的授权码

# 每天 9 点自动发送
0 9 * * * cd /Users/shenbo/Desktop/mind && ./.shared/scheduler.sh ccnews
```

---

## ❓ 遇到问题？

| 问题 | 解决方法 |
|------|---------|
| "认证失败" | 检查是否用的**授权码**而非登录密码 |
| "连接超时" | 检查 SMTP 地址和端口 |
| "未收到邮件" | 看垃圾箱，或查看 `.shared/logs/email.log` |

---

## 📖 详细文档

完整配置指南请查看: [EMAIL_SETUP_GUIDE.md](./EMAIL_SETUP_GUIDE.md)

---

*快速开始 | 5 分钟上手*
