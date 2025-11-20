#!/bin/bash

echo "====================================="
echo "测试客户端 API 服务更新"
echo "====================================="
echo ""

# 1. 登录获取 token
echo "步骤 1: 登录获取 token..."
LOGIN_RESPONSE=$(curl -s http://localhost:8000/api/v1/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "登录响应: $LOGIN_RESPONSE"
echo ""

# 提取 token
TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "错误: 无法获取 token"
    exit 1
fi

echo "成功获取 token: ${TOKEN:0:50}..."
echo ""

# 2. 调用数据同步接口
echo "步骤 2: 调用数据同步接口..."
SYNC_RESPONSE=$(curl -s http://localhost:8000/api/v1/sync/fetch \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "同步响应: $SYNC_RESPONSE"
echo ""

# 3. 查询检测对象列表
echo "步骤 3: 查询检测对象列表..."
CHECK_OBJECTS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/check-objects?page=1&page_size=10" \
  -X GET \
  -H "Authorization: Bearer $TOKEN")

echo "检测对象列表: $CHECK_OBJECTS_RESPONSE"
echo ""

# 4. 查询同步日志
echo "步骤 4: 查询同步日志..."
SYNC_LOGS_RESPONSE=$(curl -s "http://localhost:8000/api/v1/sync/logs?page=1&page_size=5" \
  -X GET \
  -H "Authorization: Bearer $TOKEN")

echo "同步日志: $SYNC_LOGS_RESPONSE"
echo ""

echo "====================================="
echo "测试完成"
echo "====================================="
