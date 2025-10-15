#!/bin/bash

# ccnews 每日自动生成和发送脚本
# 作者: ccnews automation
# 用途: 每天凌晨 4 点自动生成 Claude Code 简报并发送邮件

set -e  # 遇到错误立即退出

# ==================== 配置区域 ====================

# 邮箱配置（需要根据实际情况修改）
EMAIL_TO="your-email@example.com"                    # 收件人邮箱
EMAIL_FROM="ccnews@yourdomain.com"                    # 发件人邮箱（可选）
EMAIL_SUBJECT="Claude Code 每日简报 - $(date +%Y-%m-%d)"

# ccnews 配置
CCNEWS_DIR="/Users/shenbo/Desktop/mind/cc"
OUTPUT_DIR="$CCNEWS_DIR/$(date +%Y-%m-%d)-auto"
DAILY_MD="$OUTPUT_DIR/DAILY.md"
INDEX_HTML="$OUTPUT_DIR/index.html"

# 日志配置
LOG_DIR="$CCNEWS_DIR/logs"
LOG_FILE="$LOG_DIR/ccnews-auto-$(date +%Y-%m-%d).log"

# Node.js 路径（根据实际情况修改）
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

# ==================== 函数定义 ====================

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 错误处理函数
error_exit() {
    log "错误: $1"
    exit 1
}

# 发送邮件函数（使用 macOS 内置 mail 命令）
send_email_simple() {
    log "使用 macOS mail 命令发送邮件..."

    if [ -f "$DAILY_MD" ]; then
        cat "$DAILY_MD" | mail -s "$EMAIL_SUBJECT" "$EMAIL_TO"
        log "邮件发送成功（文本版）"
    else
        error_exit "找不到 DAILY.md 文件"
    fi
}

# 发送邮件函数（使用 Python + SMTP）
send_email_smtp() {
    log "使用 SMTP 发送邮件..."

    python3 <<EOF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# SMTP 配置（需要根据实际情况修改）
SMTP_SERVER = "smtp.gmail.com"  # Gmail: smtp.gmail.com, QQ: smtp.qq.com
SMTP_PORT = 587                 # 587 for TLS, 465 for SSL
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # 使用应用专用密码

# 邮件内容
email_to = "$EMAIL_TO"
email_from = SMTP_USER
subject = "$EMAIL_SUBJECT"

# 读取 Markdown 内容
with open("$DAILY_MD", "r", encoding="utf-8") as f:
    body_text = f.read()

# 读取 HTML 内容（如果存在）
html_body = None
if os.path.exists("$INDEX_HTML"):
    with open("$INDEX_HTML", "r", encoding="utf-8") as f:
        html_body = f.read()

# 创建邮件
msg = MIMEMultipart("alternative")
msg["From"] = email_from
msg["To"] = email_to
msg["Subject"] = subject

# 添加文本和 HTML 版本
part1 = MIMEText(body_text, "plain", "utf-8")
msg.attach(part1)

if html_body:
    part2 = MIMEText(html_body, "html", "utf-8")
    msg.attach(part2)

# 发送邮件
try:
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("邮件发送成功")
except Exception as e:
    print(f"邮件发送失败: {e}")
    exit(1)
EOF

    if [ $? -eq 0 ]; then
        log "邮件发送成功（HTML + 文本版）"
    else
        error_exit "邮件发送失败"
    fi
}

# ==================== 主流程 ====================

# 创建日志目录
mkdir -p "$LOG_DIR"

log "========================================="
log "开始执行 ccnews 自动生成任务"
log "========================================="

# 1. 检查必要的目录和文件
log "检查环境..."
if [ ! -d "$CCNEWS_DIR" ]; then
    error_exit "ccnews 目录不存在: $CCNEWS_DIR"
fi

# 2. 进入工作目录
cd "$CCNEWS_DIR"
log "当前目录: $(pwd)"

# 3. 执行 ccnews 生成（使用 Claude Code CLI）
log "开始生成 ccnews..."

# 创建临时提示词文件
PROMPT_FILE="/tmp/ccnews-prompt-$$.txt"
cat > "$PROMPT_FILE" <<'PROMPT_EOF'
/ccnews
PROMPT_EOF

# 使用 Claude Code CLI 执行（假设已安装）
if command -v claude &> /dev/null; then
    log "使用 claude CLI 执行 ccnews..."
    claude < "$PROMPT_FILE" >> "$LOG_FILE" 2>&1
    RESULT=$?
    rm -f "$PROMPT_FILE"

    if [ $RESULT -ne 0 ]; then
        log "警告: claude 命令执行返回非零值，但继续执行..."
    fi
else
    log "警告: 未找到 claude 命令，跳过 CLI 执行..."
    log "注意: 你可能需要手动配置 ccnews 的执行方式"
fi

# 4. 等待文件生成（最多等待 60 秒）
log "等待文件生成..."
WAIT_COUNT=0
while [ ! -f "$DAILY_MD" ] && [ $WAIT_COUNT -lt 60 ]; do
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))

    # 检查最新的输出目录
    LATEST_DIR=$(ls -dt "$CCNEWS_DIR"/20*/ 2>/dev/null | head -1)
    if [ -n "$LATEST_DIR" ] && [ -f "${LATEST_DIR}DAILY.md" ]; then
        OUTPUT_DIR="$LATEST_DIR"
        DAILY_MD="${OUTPUT_DIR}DAILY.md"
        INDEX_HTML="${OUTPUT_DIR}index.html"
        log "找到最新输出目录: $OUTPUT_DIR"
        break
    fi
done

# 5. 检查文件是否生成成功
if [ ! -f "$DAILY_MD" ]; then
    error_exit "未找到生成的 DAILY.md 文件"
fi

log "文件生成成功:"
log "  - DAILY.md: $(wc -c < "$DAILY_MD") 字节"
if [ -f "$INDEX_HTML" ]; then
    log "  - index.html: $(wc -c < "$INDEX_HTML") 字节"
fi

# 6. 发送邮件
log "准备发送邮件到: $EMAIL_TO"

# 选择发送方式（默认使用简单方式）
# 如果配置了 SMTP，可以改为 send_email_smtp
send_email_simple

# 7. 清理旧文件（保留最近 7 天）
log "清理旧文件..."
find "$CCNEWS_DIR" -maxdepth 1 -type d -name "20*-*" -mtime +7 -exec rm -rf {} \; 2>/dev/null || true
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true

log "========================================="
log "ccnews 自动生成任务完成"
log "========================================="

exit 0
