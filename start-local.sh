#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法:
  ./start-local.sh
  ./start-local.sh -h
  ./start-local.sh --help

可选环境变量:
  IP     监听地址，默认 127.0.0.1
  PORT   监听端口，默认 4000

示例:
  ./start-local.sh
  PORT=5000 ./start-local.sh
  IP=0.0.0.0 PORT=4000 ./start-local.sh
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "错误: 不支持的参数: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v npm >/dev/null 2>&1; then
  echo "错误: 未找到 npm，请先安装 Node.js 20+ 和 npm。" >&2
  exit 1
fi

if [ ! -d node_modules ]; then
  echo "未检测到 node_modules，正在安装依赖..."
  npm install
fi

IP="${IP:-127.0.0.1}"
PORT="${PORT:-4000}"

# 生成 RAG 搜索索引
echo "正在生成搜索索引..."
python rag_struct/indexer.py --format hexo --output source/search.json --rebuild

# 生成 Hexo 搜索数据库
echo "正在生成 Hexo 搜索数据..."
npx hexo generate

echo "正在启动 Hexo 本地预览..."
echo "预览地址: http://${IP}:${PORT}/"
echo "停止服务: Ctrl+C"

npm run server -- --ip "${IP}" --port "${PORT}"
