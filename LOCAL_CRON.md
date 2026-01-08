# 本地定时任务使用说明

## 已配置的定时任务

系统已经配置了 cron 定时任务，**每小时运行一次**：

```bash
5 * * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh
```

- **运行时间**：每小时的第 5 分钟
- **执行内容**：
  1. 运行数据更新脚本（获取 MZ 和 George 的余额）
  2. 追加新数据到 `data/` 目录
  3. 自动 git 提交
  4. 自动 git push 到远程仓库
- **日志位置**：`logs/update.log`

## 查看日志

```bash
# 查看最新日志
tail -f logs/update.log

# 查看最近50行
tail -n 50 logs/update.log
```

## 管理 cron 任务

### 查看当前的 cron 任务
```bash
crontab -l
```

### 编辑 cron 任务
```bash
crontab -e
```

### 删除所有 cron 任务
```bash
crontab -r
```

### 临时禁用（不删除，只是注释掉）
```bash
crontab -e
# 在任务前加 # 号即可注释
# 5 * * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh ...
```

## 手动运行

如果需要手动运行一次（不等待定时任务）：

```bash
cd /Users/oymuzi/blockchain/fdf
./scripts/run_and_commit.sh
```

## 修改运行频率

编辑 crontab：
```bash
crontab -e
```

常用配置示例：

```bash
# 每小时（当前配置）
5 * * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh >> /Users/oymuzi/blockchain/fdf/logs/update.log 2>&1

# 每30分钟
*/30 * * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh >> /Users/oymuzi/blockchain/fdf/logs/update.log 2>&1

# 每2小时
0 */2 * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh >> /Users/oymuzi/blockchain/fdf/logs/update.log 2>&1

# 每天早上9点（北京时间）
0 1 * * * /Users/oymuzi/blockchain/fdf/scripts/run_and_commit.sh >> /Users/oymuzi/blockchain/fdf/logs/update.log 2>&1
```

## 故障排查

### 检查 cron 服务是否运行
```bash
# macOS
sudo launchctl list | grep cron
# 或者
ps aux | grep cron
```

### 检查日志文件
```bash
# 查看是否有日志生成
ls -la logs/update.log

# 查看最近的错误
tail -n 50 logs/update.log | grep -i error
```

### 测试脚本
```bash
# 手动运行脚本，看是否正常
./scripts/run_and_commit.sh
```

## GitHub Actions 说明

本地定时任务运行后，推送到 GitHub 会自动触发部署工作流，更新网站。

GitHub Actions 的 `update.yml` 可以保留或删除，不影响本地定时任务。

---

**注意**：确保计算机在定时任务运行时是开机状态，否则任务无法执行。
