#!/bin/bash
# QQ 邮箱快速配置脚本

echo "======================================"
echo "QQ 邮箱配置助手"
echo "======================================"
echo ""

# 1. 检查依赖
echo "📦 步骤 1/4: 检查依赖..."
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "  → 安装 pyyaml..."
    pip3 install pyyaml markdown
fi
echo "  ✓ 依赖检查完成"
echo ""

# 2. 获取邮箱信息
echo "📧 步骤 2/4: 配置邮箱信息"
read -p "请输入你的 QQ 邮箱地址 (如: 123456789@qq.com): " QQ_EMAIL

if [[ ! "$QQ_EMAIL" =~ @qq\.com$ ]]; then
    echo "❌ 错误: 请输入正确的 QQ 邮箱地址"
    exit 1
fi

echo ""
echo "📝 步骤 3/4: 获取授权码"
echo ""
echo "请按照以下步骤获取 QQ 邮箱授权码："
echo "  1. 访问 https://mail.qq.com/"
echo "  2. 登录后点击 [设置] → [账户]"
echo "  3. 找到 [POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务]"
echo "  4. 开启 [SMTP服务]"
echo "  5. 点击 [生成授权码]"
echo "  6. 使用手机 QQ 扫码验证"
echo "  7. 复制生成的授权码（16 位字符）"
echo ""
read -p "请输入授权码: " -s AUTH_CODE
echo ""

if [ -z "$AUTH_CODE" ]; then
    echo "❌ 错误: 授权码不能为空"
    exit 1
fi

echo ""
echo "🔧 步骤 4/4: 保存配置..."

# 3. 更新配置文件
CONFIG_FILE="$HOME/Desktop/mind/.shared/config.yaml"

# 备份原配置
cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"

# 使用 Python 更新配置
python3 << EOF
import yaml

config_file = "$CONFIG_FILE"

with open(config_file, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 更新邮件配置
config['email']['enabled'] = True
config['email']['smtp']['host'] = 'smtp.qq.com'
config['email']['smtp']['port'] = 587
config['email']['smtp']['use_tls'] = True
config['email']['smtp']['use_ssl'] = False
config['email']['sender']['email'] = '$QQ_EMAIL'
config['email']['sender']['name'] = 'Mind AI Report'
config['email']['recipients'] = ['$QQ_EMAIL']

with open(config_file, 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("  ✓ 配置文件已更新")
EOF

# 4. 设置环境变量
echo ""
echo "export MIND_EMAIL_PASSWORD=\"$AUTH_CODE\"" >> ~/.zshrc
echo "  ✓ 授权码已保存到 ~/.zshrc"

# 5. 测试发送
echo ""
echo "======================================"
echo "✅ 配置完成！"
echo "======================================"
echo ""
echo "📊 配置信息："
echo "  邮箱: $QQ_EMAIL"
echo "  SMTP: smtp.qq.com:587"
echo "  状态: 已启用"
echo ""
echo "🧪 测试发送："
echo ""
echo "  方式 1: 测试今天的报告"
echo "  $ source ~/.zshrc"
echo "  $ cd ~/Desktop/mind"
echo "  $ python .shared/email_sender.py --report cc/$(date +%Y-%m-%d)/index.md --type ccnews"
echo ""
echo "  方式 2: 使用调度脚本"
echo "  $ source ~/.zshrc"
echo "  $ cd ~/Desktop/mind"
echo "  $ ./.shared/scheduler.sh ccnews"
echo ""
echo "💡 提示: 请执行 'source ~/.zshrc' 使环境变量生效"
echo ""
