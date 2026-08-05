#!/bin/bash
# ============================================================
# 警情案件工作台账登记系统 - 容器启动脚本
#
# 流程:
#   1. 等待 MySQL 健康检查通过
#   2. 创建数据库（如果不存在）
#   3. 启动 Flask 应用（开发/生产模式自适应）
# ============================================================

set -eo pipefail

MYSQL_HOST="${MYSQL_HOST:-db}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASS="${MYSQL_PASSWORD:-root}"
MYSQL_DB="${MYSQL_DATABASE:-work_ledger}"
FLASK_MODE="${FLASK_ENV:-production}"

echo ""
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║  警情案件工作台账登记系统                     ║"
echo "  ╠══════════════════════════════════════════════╣"
echo "  ║  MySQL  : ${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}                "
echo "  ║  FLASK  : ${FLASK_MODE}                                  "
echo "  ╚══════════════════════════════════════════════╝"
echo ""

# ── Step 1: 等待 MySQL ────────────────────────
echo "  [1/3] 等待 MySQL 就绪..."
echo "        host=${MYSQL_HOST} port=${MYSQL_PORT} user=${MYSQL_USER}"

MAX_RETRIES=30
RETRY_INTERVAL=2
retry=0

while [ $retry -lt $MAX_RETRIES ]; do
    if mysqladmin ping \
        -h "${MYSQL_HOST}" \
        -P "${MYSQL_PORT}" \
        -u "${MYSQL_USER}" \
        --password="${MYSQL_PASS}" \
        --skip-ssl \
        --silent 2>/dev/null; then
        echo "  √  MySQL 已就绪 (等待约 $((retry * RETRY_INTERVAL)) 秒)"
        break
    fi
    retry=$((retry + 1))
    if [ $((retry % 5)) -eq 0 ]; then
        echo "        ... 等待中 ($((retry * RETRY_INTERVAL))s / $((MAX_RETRIES * RETRY_INTERVAL))s)"
    fi
    sleep $RETRY_INTERVAL
done

if [ $retry -ge $MAX_RETRIES ]; then
    echo "  ✗  MySQL 连接超时（${MYSQL_HOST}:${MYSQL_PORT}），无法继续"
    exit 1
fi

# ── Step 2: 确保数据库存在 ────────────────────
echo ""
echo "  [2/3] 确保数据库 ${MYSQL_DB} 存在..."

mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u "${MYSQL_USER}" --password="${MYSQL_PASS}" --skip-ssl -e "
    CREATE DATABASE IF NOT EXISTS \`${MYSQL_DB}\`
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
" 2>/dev/null

echo "  √  数据库 ${MYSQL_DB} 已就绪"

# ── Step 3: 启动应用 ──────────────────────────
echo ""
echo "  [3/3] 启动应用 (${FLASK_MODE} 模式)..."

# 数据库 URL
DB_URL="mysql+pymysql://${MYSQL_USER}:${MYSQL_PASS}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB}?charset=utf8mb4"
export SQLALCHEMY_DATABASE_URI="$DB_URL"

cd /app

if [ "${FLASK_MODE}" = "development" ]; then
    echo "        Flask 内置开发服务器 (0.0.0.0:5000)"
    echo ""
    exec python /app/run.py
else
    echo "        Waitress 生产服务器 (0.0.0.0:5000, 4 threads)"
    echo ""
    exec python -c "
from app import create_app
from waitress import serve
import os

app = create_app(os.environ.get('FLASK_ENV', 'production'))
serve(app, host='0.0.0.0', port=5000, threads=4, channel_timeout=120)
"
fi
