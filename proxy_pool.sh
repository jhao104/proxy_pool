#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/proxy_pool.pid"
PYTHON="${PYTHON:-python}"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 获取已启动的 PIDs
get_pids() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

# 检查进程是否存活
is_running() {
    local pid=$1
    kill -0 "$pid" 2>/dev/null
}

# 启动服务
cmd_start() {
    local foreground=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --fg|--foreground) foreground=true; shift ;;
            *) log_error "Unknown option: $1"; exit 1 ;;
        esac
    done

    # 检查是否已运行
    local pids=$(get_pids)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            if is_running "$pid"; then
                log_warn "Service already running (PID: $pid)"
                log_warn "Use '$0 stop' first, or '$0 restart'"
                exit 1
            fi
        done
    fi

    # 清理旧的 PID 文件
    rm -f "$PID_FILE"

    cd "$SCRIPT_DIR"

    if [ "$foreground" = true ]; then
        # 前台模式（容器环境）
        log_info "Starting in foreground mode..."

        trap 'log_info "Shutting down..."; kill $SERVER_PID $SCHEDULER_PID 2>/dev/null; wait; rm -f "$PID_FILE"; exit 0' EXIT INT TERM

        $PYTHON proxyPool.py server &
        SERVER_PID=$!

        $PYTHON proxyPool.py schedule &
        SCHEDULER_PID=$!

        echo "$SERVER_PID" >> "$PID_FILE"
        echo "$SCHEDULER_PID" >> "$PID_FILE"

        log_info "Services started (PIDs: $SERVER_PID $SCHEDULER_PID)"
        wait
    else
        # 后台模式（非容器环境）
        log_info "Starting in background mode..."

        nohup $PYTHON proxyPool.py server > /dev/null 2>&1 &
        SERVER_PID=$!

        nohup $PYTHON proxyPool.py schedule > /dev/null 2>&1 &
        SCHEDULER_PID=$!

        echo "$SERVER_PID" >> "$PID_FILE"
        echo "$SCHEDULER_PID" >> "$PID_FILE"

        sleep 2

        # 验证启动
        local failed=false
        if ! is_running "$SERVER_PID"; then
            log_error "Server failed to start"
            failed=true
        fi
        if ! is_running "$SCHEDULER_PID"; then
            log_error "Scheduler failed to start"
            failed=true
        fi

        if [ "$failed" = true ]; then
            cmd_stop
            exit 1
        fi

        log_info "Services started"
        log_info "  Server PID:    $SERVER_PID"
        log_info "  Scheduler PID: $SCHEDULER_PID"
        log_info "Use '$0 stop' to stop, '$0 status' to check"
    fi
}

# 停止服务
cmd_stop() {
    local pids=$(get_pids)

    if [ -z "$pids" ]; then
        log_warn "No PID file found. Services may not be running."
        exit 0
    fi

    log_info "Stopping services..."

    local stopped=0
    for pid in $pids; do
        if is_running "$pid"; then
            kill "$pid" 2>/dev/null || true
            stopped=$((stopped + 1))
        fi
    done

    # 等待进程退出
    sleep 1

    # 强制杀死仍在运行的进程
    for pid in $pids; do
        if is_running "$pid"; then
            log_warn "Force killing PID $pid"
            kill -9 "$pid" 2>/dev/null || true
        fi
    done

    rm -f "$PID_FILE"
    log_info "Stopped $stopped service(s)"
}

# 重启服务
cmd_restart() {
    cmd_stop
    sleep 1
    cmd_start "$@"
}

# 查看状态
cmd_status() {
    local pids=$(get_pids)

    if [ -z "$pids" ]; then
        log_info "No PID file found. Services are not running."
        exit 0
    fi

    local running=0
    local dead=0

    for pid in $pids; do
        if is_running "$pid"; then
            running=$((running + 1))
        else
            dead=$((dead + 1))
        fi
    done

    if [ $running -gt 0 ]; then
        log_info "Services: $running running, $dead dead"
        for pid in $pids; do
            local status="stopped"
            if is_running "$pid"; then
                status="running"
            fi
            echo "  PID $pid: $status"
        done
    else
        log_warn "All services are stopped"
        rm -f "$PID_FILE"
    fi
}

# 显示帮助
cmd_help() {
    cat <<EOF
ProxyPool Service Manager

Usage: $0 <command> [options]

Commands:
  start [--fg]    Start services (background by default)
                  --fg  Run in foreground (for containers)
  stop            Stop all services
  restart [--fg]  Restart services
  status          Show service status
  help            Show this help

Examples:
  $0 start              # Start in background
  $0 start --fg         # Start in foreground (containers)
  $0 stop               # Stop all services
  $0 status             # Check status

Environment:
  PYTHON    Python executable (default: python)
EOF
}

# 主入口
case "${1:-help}" in
    start)    shift; cmd_start "$@" ;;
    stop)     cmd_stop ;;
    restart)  shift; cmd_restart "$@" ;;
    status)   cmd_status ;;
    help|-h|--help) cmd_help ;;
    *)        log_error "Unknown command: $1"; cmd_help; exit 1 ;;
esac
