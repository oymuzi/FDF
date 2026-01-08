# FDF Dashboard - 快速部署指南

## 📂 项目结构

```
fdf/
├── data/                      # CSV数据文件
│   ├── mz_history.csv
│   └── wj_history.csv
├── website/                   # 静态网站
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── scripts/
│   └── update.py             # 数据更新脚本
└── .github/workflows/
    ├── update.yml            # 定时更新数据
    └── deploy.yml            # 自动部署网站
```

## 🚀 3步部署

### 步骤1: 修改配置

编辑 `website/js/app.js` 第3行:

```javascript
githubUsername: 'YOUR_USERNAME',  // 改成你的GitHub用户名
```

### 步骤2: 推送到GitHub

```bash
cd fdf
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/fdf.git
git push -u origin main
```

### 步骤3: 启用GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. **Source** 选择 **GitHub Actions**
3. 保存

## 🎉 完成!

访问: `https://你的用户名.github.io/fdf/`

## ⚙️ 工作原理

- 每小时自动运行 `scripts/update.py`
- 从 `../football/` 复制CSV到 `data/`
- Git自动提交并推送到GitHub
- GitHub Actions自动部署网站

## 🔄 手动更新数据

在GitHub仓库:
- **Actions** → **更新数据** → **Run workflow**

或本地:
```bash
cd fdf
python scripts/update.py
git add data/
git commit -m "Update data"
git push
```

## ⚠️ 注意

- 仓库必须设为 **Public**
- 确保CSV文件在 `data/` 目录
- 网站部署需要2-3分钟

## 📊 功能

- ✅ 实时显示MZ和George的资产
- ✅ 自动计算涨跌幅
- ✅ 漂亮的图表展示
- ✅ 响应式设计
- ✅ 每小时自动更新

需要帮助? 查看浏览器控制台(F12)查看日志!
