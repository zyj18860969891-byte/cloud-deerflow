#!/bin/bash
#
# DeerFlow 部署验证脚本
# 用法: ./verify-deployment.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "======================================================"
echo "     DeerFlow 部署验证脚本"
echo "======================================================"
echo -e "${NC}"

# 颜色输出函数
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查计数
passed=0
failed=0
warnings=0

# 1. 系统工具检查
echo ""
echo -e "${BLUE}[1/5] 检查系统工具${NC}"
echo "======================================================"

# 检查 Docker
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
    success "Docker: $docker_version"
    ((passed++))
else
    error "Docker 未安装"
    ((failed++))
fi

# 检查 Docker Compose
if command -v docker compose &> /dev/null; then
    dc_version=$(docker compose version | awk '{print $4}')
    success "Docker Compose: $dc_version"
    ((passed++))
else
    error "Docker Compose 未安装"
    ((failed++))
fi

# 检查 Git
if command -v git &> /dev/null; then
    success "Git: $(git --version | awk '{print $3}')"
    ((passed++))
else
    warning "Git 未安装（非必须）"
    ((warnings++))
fi

# 2. 目录检查
echo ""
echo -e "${BLUE}[2/5] 检查数据目录${NC}"
echo "======================================================"

required_dirs=(
    "/data/deer-flow/.deer-flow"
    "/data/deer-flow/.deer-flow/skills"
    "/data/deer-flow/.deer-flow/logs"
    "/data/deer-flow/tenants"
    "/data/deer-flow/backup"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        success "$dir"
        ((passed++))
    else
        error "$dir 不存在"
        ((failed++))
    fi
done

# 检查权限
if [ -O "/data/deer-flow" ]; then
    success "数据目录权限正确"
    ((passed++))
else
    warning "数据目录权限可能不正确"
    ((warnings++))
fi

# 3. 配置文件检查
echo ""
echo -e "${BLUE}[3/5] 检查配置文件${NC}"
echo "======================================================"

config_files=(
    "/opt/deer-flow/config.yaml"
    "/opt/deer-flow/.env"
    "/opt/deer-flow/docker/docker-compose.yaml"
)

for config in "${config_files[@]}"; do
    if [ -f "$config" ]; then
        success "$config"
        ((passed++))
    else
        warning "$config 不存在"
        ((warnings++))
    fi
done

# 检查 BETTER_AUTH_SECRET
if [ -f "/opt/deer-flow/.env" ]; then
    if grep -q "BETTER_AUTH_SECRET=" "/opt/deer-flow/.env"; then
        secret=$(grep "BETTER_AUTH_SECRET=" "/opt/deer-flow/.env" | cut -d= -f2 | head -c 10)
        if [ -n "$secret" ] && [ "$secret" != "your-" ]; then
            success "BETTER_AUTH_SECRET 已设置"
            ((passed++))
        else
            error "BETTER_AUTH_SECRET 未设置或使用默认值"
            ((failed++))
        fi
    else
        error "BETTER_AUTH_SECRET 未找到"
        ((failed++))
    fi
fi

# 4. Docker 容器检查
echo ""
echo -e "${BLUE}[4/5] 检查 Docker 容器状态${NC}"
echo "======================================================"

if command -v docker &> /dev/null; then
    # 检查容器是否运行
    container_count=$(docker ps | grep -c "deer" || true)
    
    if [ "$container_count" -gt 0 ]; then
        success "DeerFlow 容器已启动 ($container_count 个)"
        ((passed++))
        
        # 检查各个服务
        services=("nginx" "frontend" "gateway" "langgraph")
        for service in "${services[@]}"; do
            if docker ps | grep -q "$service"; then
                success "  - $service 正在运行"
                ((passed++))
            else
                warning "  - $service 未运行"
                ((warnings++))
            fi
        done
    else
        warning "DeerFlow 容器未启动"
        ((warnings++))
    fi
else
    warning "无法检查容器（Docker 未安装）"
    ((warnings++))
fi

# 5. 服务连接检查
echo ""
echo -e "${BLUE}[5/5] 检查服务连接${NC}"
echo "======================================================"

# 检查前端
if curl -s -f http://localhost:2026/ > /dev/null 2>&1; then
    success "前端服务: http://localhost:2026"
    ((passed++))
else
    warning "前端服务无法访问（可能未启动）"
    ((warnings++))
fi

# 检查 API
if curl -s -f http://localhost:8001/docs > /dev/null 2>&1; then
    success "API 服务: http://localhost:8001/docs"
    ((passed++))
else
    warning "API 服务无法访问（可能未启动）"
    ((warnings++))
fi

# 检查 LangGraph
if curl -s -f http://localhost:2024/ > /dev/null 2>&1; then
    success "LangGraph 服务: http://localhost:2024"
    ((passed++))
else
    warning "LangGraph 服务无法访问（可能未启动）"
    ((warnings++))
fi

# 总结报告
echo ""
echo -e "${BLUE}======================================================"
echo "检查总结"
echo "======================================================${NC}"
echo ""
echo -e "${GREEN}✅ 通过: $passed${NC}"
echo -e "${RED}❌ 失败: $failed${NC}"
echo -e "${YELLOW}⚠️  警告: $warnings${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 所有关键检查都通过了！${NC}"
    echo ""
    echo "后续步骤："
    echo "1. 访问 http://localhost:2026 查看前端"
    echo "2. 访问 http://localhost:8001/docs 查看 API 文档"
    echo "3. 创建第一个对话线程开始使用"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  请解决上述问题后再继续${NC}"
    echo ""
    echo "常见解决方案："
    echo "1. 确保 Docker 已启动: sudo systemctl start docker"
    echo "2. 检查文件权限: sudo chown -R \$USER:\$USER /data/deer-flow"
    echo "3. 查看容器日志: docker compose logs -f gateway"
    echo "4. 参考文档: DEPLOYMENT_GUIDE.md 第11章"
    echo ""
    exit 1
fi
