#!/bin/bash

# 配置 PostgreSQL 数据库环境变量
# 此脚本使用 Railway CLI 为 PostgreSQL 插件配置环境变量

echo "🔧 Railway 数据库配置脚本"
echo ""
echo "请在 Railway 仪表板执行以下步骤："
echo ""
echo "1️⃣ 打开 Railway 项目: https://railway.com/dashboard"
echo "2️⃣ 选择项目: cloud-deerflow"
echo "3️⃣ 点击「Add Service」添加服务"
echo "4️⃣ 选择「PostgreSQL」数据库"
echo "5️⃣ 等待数据库启动后，DATABASE_URL 会自动注入"
echo ""
echo "如果无法自动添加，手动设置环境变量："
echo ""
echo "DATABASE_URL=postgresql://postgres:password@host:5432/deerflow"
echo ""
echo "然后重新部署:"
echo "  railway up"
echo ""
