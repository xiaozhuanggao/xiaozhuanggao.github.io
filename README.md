# blog

高晓庄的个人技术主页、在线简历、技术博客与项目作品集。

🌐 在线访问：<https://xiaozhuanggao.github.io>

## 技术栈

- **Hexo 8** —— 静态站点生成
- **Butterfly** 主题 —— 简洁专业的技术博客主题
- **GitHub Pages** —— 静态托管
- **GitHub Actions** —— 自动构建与部署
- **Node.js 22** —— 构建环境

## 内容板块

- 🏠 **首页** —— 个人简介、最新文章
- 📄 **简历** —— 在线简历 + PDF 下载
- 💼 **项目** —— 项目作品集
- 📚 **技术文章** —— 按 AI / Java / Go / Cloud Native / Database / Architecture 分类
- 🏷️ **标签** —— 主题标签云
- 🔍 **搜索** —— 站内全文搜索
- 🌙 **暗色模式** —— 跟随系统自动切换

## 本地开发

```bash
# 安装依赖
npm install

# 启动本地服务（http://localhost:4000）
npm run server

# 构建静态文件
npm run build

# 清理 + 构建
npm run clean && npm run build
```

## 部署

```bash
# 提交源码
git add .
git commit -m "更新内容"
git push origin main

# GitHub Actions 自动构建并部署到 GitHub Pages
```

## 目录说明

```text
source/_posts/    # 博客文章
source/about/     # 关于页面
source/resume/    # 简历页面
source/projects/  # 项目页面
source/downloads/ # 可下载文件（简历 PDF）
themes/           # 主题目录
_config.yml       # 站点配置
_config.butterfly.yml  # 主题配置
.github/workflows/pages.yml  # 自动部署
```

## License

MIT License - 内容仅供学习参考。