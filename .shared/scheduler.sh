#!/bin/bash
# Mind 项目自动化调度脚本
# 用法: ./scheduler.sh [ccnews|ainews|both]

set -e  # 遇到错误立即退出

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.shared/logs"
mkdir -p "$LOG_DIR"

# 加载环境变量
if [ -f "$PROJECT_ROOT/.shared/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.shared/.env" | xargs)
fi

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE=$(date +"%Y-%m-%d")

# 日志函数
log_info() {
    echo "[$TIMESTAMP] INFO: $1" | tee -a "$LOG_DIR/scheduler.log"
}

log_error() {
    echo "[$TIMESTAMP] ERROR: $1" | tee -a "$LOG_DIR/scheduler.log"
}

# ccnews 生成流程
run_ccnews() {
    log_info "开始生成 Claude Code 日报..."

    cd "$PROJECT_ROOT/cc"
    source .meta/venv/bin/activate

    # 1. 数据采集
    log_info "  → 数据采集中..."
    if python .meta/scripts/fetch_data_v2.py; then
        log_info "  ✓ 数据采集成功"
    else
        log_error "  ✗ 数据采集失败"
        return 1
    fi

    # 2. 生成报告（使用 Claude Code）
    log_info "  → 生成报告中..."
    # 这里需要调用 Claude Code CLI
    # claude --prompt "$(cat .claude/commands/ccnews.md)"

    # 3. 发送邮件（如果启用）
    REPORT_PATH="$PROJECT_ROOT/cc/$DATE/index.md"
    if [ -f "$REPORT_PATH" ]; then
        log_info "  → 发送邮件通知..."
        cd "$PROJECT_ROOT"
        if python3 .shared/email_sender.py --report "$REPORT_PATH" --type ccnews 2>&1 | tee -a "$LOG_DIR/email.log"; then
            log_info "  ✓ 邮件发送成功"
        else
            log_info "  ⚠ 邮件发送失败或未启用（查看日志: $LOG_DIR/email.log）"
        fi
    else
        log_info "  ⚠ 报告文件不存在，跳过邮件发送: $REPORT_PATH"
    fi

    log_info "✓ Claude Code 日报生成完成"
}

# ainews 生成流程
run_ainews() {
    log_info "开始生成 AI 全景报告..."

    # ainews 主要通过 Agent 实时采集，可选预采集
    # cd "$PROJECT_ROOT/ainews"
    # python .meta/scripts/fetch_ai_data.py --rankings --news

    log_info "  → 生成报告中..."
    # claude --prompt "$(cat .claude/commands/ainews.md)"

    # 发送邮件（如果启用）
    REPORT_PATH="$PROJECT_ROOT/ainews/$DATE/index.md"
    if [ -f "$REPORT_PATH" ]; then
        log_info "  → 发送邮件通知..."
        cd "$PROJECT_ROOT"
        if python3 .shared/email_sender.py --report "$REPORT_PATH" --type ainews 2>&1 | tee -a "$LOG_DIR/email.log"; then
            log_info "  ✓ 邮件发送成功"
        else
            log_info "  ⚠ 邮件发送失败或未启用（查看日志: $LOG_DIR/email.log）"
        fi
    else
        log_info "  ⚠ 报告文件不存在，跳过邮件发送: $REPORT_PATH"
    fi

    log_info "✓ AI 全景报告生成完成"
}

# 清理旧报告
cleanup_old_reports() {
    log_info "清理 30 天前的旧报告..."

    CUTOFF_DATE=$(date -v-30d +"%Y-%m-%d" 2>/dev/null || date -d "30 days ago" +"%Y-%m-%d")

    # 移动到归档
    find "$PROJECT_ROOT/cc" -maxdepth 1 -type d -name "2025-*" | while read dir; do
        report_date=$(basename "$dir")
        if [[ "$report_date" < "$CUTOFF_DATE" ]]; then
            archive_path="$PROJECT_ROOT/cc/archive/$(date -j -f "%Y-%m-%d" "$report_date" +"%Y-%m" 2>/dev/null || date -d "$report_date" +"%Y-%m")"
            mkdir -p "$archive_path"
            mv "$dir" "$archive_path/"
            log_info "  归档: $dir → $archive_path"
        fi
    done

    log_info "✓ 清理完成"
}

# 主逻辑
main() {
    MODE=${1:-both}

    log_info "========================================"
    log_info "Mind 项目自动化调度开始"
    log_info "模式: $MODE"
    log_info "========================================"

    case $MODE in
        ccnews)
            run_ccnews
            ;;
        ainews)
            run_ainews
            ;;
        both)
            run_ccnews
            run_ainews
            ;;
        cleanup)
            cleanup_old_reports
            ;;
        *)
            log_error "未知模式: $MODE"
            echo "用法: $0 [ccnews|ainews|both|cleanup]"
            exit 1
            ;;
    esac

    log_info "========================================"
    log_info "调度完成！"
    log_info "========================================"
}

main "$@"
