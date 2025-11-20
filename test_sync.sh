#!/bin/bash

# 测试同步功能

echo "1. 登录获取 token..."
LOGIN_RESPONSE=$(curl -s http://localhost:8000/api/v1/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "$LOGIN_RESPONSE" | python -m json.tool

TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "登录失败！"
  exit 1
fi

echo -e "\n2. 使用 token 调用同步接口..."
SYNC_RESPONSE=$(curl -s http://localhost:8000/api/v1/sync/fetch \
  -X POST \
  -H "Authorization: Bearer $TOKEN")

echo "$SYNC_RESPONSE" | python -m json.tool

echo -e "\n3. 检查同步日志..."
docker-compose -p food-quality exec -T postgres psql -U postgres -d food_quality -c "SELECT id, sync_type, status, fetched_count, error_message FROM sync_logs ORDER BY start_time DESC LIMIT 3;"

echo -e "\n4. 检查检测对象数量..."
docker-compose -p food-quality exec -T postgres psql -U postgres -d food_quality -c "SELECT COUNT(*) as total_objects FROM check_objects;"
