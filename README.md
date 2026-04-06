# Nyquest-unstable.github.io

这个仓库现在保存的是 Hexo 源文件，使用 NexT 主题并通过 GitHub Actions 发布到 GitHub Pages。

## 本地使用

```bash
npm install
npm run server
```

本地预览地址默认是 `http://localhost:4000/`。

## 构建

```bash
npm run build
```

生成结果会输出到 `public/`，该目录已经在 `.gitignore` 中排除，不需要提交。

## GitHub Pages

按 Hexo 官方文档，仓库应使用 `GitHub Actions` 作为 Pages 发布源。这个仓库已经包含 [.github/workflows/pages.yml](/home/lubancat/github_workspace/Nyquest-unstable.github.io/.github/workflows/pages.yml)。

在 GitHub 上需要确认：

1. 仓库名为 `Nyquest-unstable.github.io`
2. 默认分支是 `master`
3. `Settings > Pages > Source` 选择 `GitHub Actions`

## 内容说明

- 现有文章已经从静态页面恢复到 `source/_posts/`
- 原先依赖内网 WordPress 的两张图片已改为本地占位图，避免 GitHub Pages 上出现坏链
