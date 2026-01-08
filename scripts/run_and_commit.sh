#!/bin/bash
# FDF 数据更新脚本 - 本地定时运行版本
# 每小时运行一次，更新数据后自动提交到 git

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔄 FDF 数据更新开始${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 进入项目目录
cd "$(dirname "$0")/.."

# 运行更新脚本
echo -e "${BLUE}📊 运行数据更新脚本...${NC}"
python3 scripts/update.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据更新成功${NC}"
    echo ""

    # 检查是否有变更
    if git diff --quiet data/; then
        echo -e "${BLUE}ℹ️  没有数据变更，跳过提交${NC}"
        exit 0
    fi

    # 添加数据文件
    echo -e "${BLUE}📝 提交数据变更...${NC}"
    git add data/

    # 提交
    echo -e "${BLUE}💾 创建提交...${NC}"
    git commit -m "更新数据 [skip ci]"
    # 推送
    echo -e "${BLUE}⬆️  推送到远程仓库...${NC}"
    git push

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ 数据更新并推送成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}❌ 数据更新失败${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
