#!/bin/bash

# Docker 容器部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
IMAGE_NAME="my-telegram-bot"
CONTAINER_NAME="my-telegram-bot"
PORT=${PORT:-8000}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🐳 Docker 容器部署脚本${NC}"
echo -e "${GREEN}========================================${NC}\n"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装，请先安装 Docker${NC}"
    echo "Windows/Mac: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在${NC}"
    echo "请创建 .env 文件并配置所有必需的环境变量"
    exit 1
fi

# 函数：构建镜像
build_image() {
    echo -e "${YELLOW}📦 构建 Docker 镜像...${NC}"
    docker build -t ${IMAGE_NAME}:latest .
    echo -e "${GREEN}✅ 镜像构建完成${NC}\n"
}

# 函数：停止并删除旧容器
cleanup_old_container() {
    if docker ps -a | grep -q ${CONTAINER_NAME}; then
        echo -e "${YELLOW}🛑 停止并删除旧容器...${NC}"
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
        echo -e "${GREEN}✅ 旧容器已清理${NC}\n"
    fi
}

# 函数：运行容器
run_container() {
    echo -e "${YELLOW}🚀 启动容器...${NC}"
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:${PORT} \
        --env-file .env \
        -e PORT=${PORT} \
        -v $(pwd)/logs:/app/logs \
        ${IMAGE_NAME}:latest
    echo -e "${GREEN}✅ 容器已启动${NC}\n"
}

# 函数：运行数据库迁移
run_migrations() {
    echo -e "${YELLOW}📊 运行数据库迁移...${NC}"
    docker exec ${CONTAINER_NAME} alembic upgrade head || {
        echo -e "${YELLOW}⚠️  迁移失败，请检查数据库连接${NC}"
    }
    echo ""
}

# 函数：显示状态
show_status() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}📊 容器状态${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${GREEN}📋 查看日志：${NC}"
    echo "docker logs -f ${CONTAINER_NAME}"
    
    echo -e "\n${GREEN}🔍 进入容器：${NC}"
    echo "docker exec -it ${CONTAINER_NAME} bash"
    
    echo -e "\n${GREEN}🌐 健康检查：${NC}"
    echo "curl http://localhost:${PORT}/health"
    echo ""
}

# 主函数
main() {
    case "${1:-deploy}" in
        build)
            build_image
            ;;
        deploy)
            build_image
            cleanup_old_container
            run_container
            sleep 5
            run_migrations
            show_status
            ;;
        start)
            cleanup_old_container
            run_container
            show_status
            ;;
        stop)
            echo -e "${YELLOW}🛑 停止容器...${NC}"
            docker stop ${CONTAINER_NAME} || true
            echo -e "${GREEN}✅ 容器已停止${NC}"
            ;;
        restart)
            echo -e "${YELLOW}🔄 重启容器...${NC}"
            docker restart ${CONTAINER_NAME} || {
                cleanup_old_container
                run_container
            }
            show_status
            ;;
        logs)
            docker logs -f ${CONTAINER_NAME}
            ;;
        shell)
            docker exec -it ${CONTAINER_NAME} bash
            ;;
        migrate)
            run_migrations
            ;;
        status)
            show_status
            ;;
        clean)
            echo -e "${YELLOW}🧹 清理容器和镜像...${NC}"
            docker stop ${CONTAINER_NAME} 2>/dev/null || true
            docker rm ${CONTAINER_NAME} 2>/dev/null || true
            docker rmi ${IMAGE_NAME}:latest 2>/dev/null || true
            echo -e "${GREEN}✅ 清理完成${NC}"
            ;;
        *)
            echo "用法: $0 [命令]"
            echo ""
            echo "命令："
            echo "  build     - 构建 Docker 镜像"
            echo "  deploy    - 完整部署（构建+运行+迁移）"
            echo "  start     - 启动容器"
            echo "  stop      - 停止容器"
            echo "  restart   - 重启容器"
            echo "  logs      - 查看日志"
            echo "  shell     - 进入容器"
            echo "  migrate   - 运行数据库迁移"
            echo "  status    - 显示容器状态"
            echo "  clean     - 清理容器和镜像"
            exit 1
            ;;
    esac
}

main "$@"



