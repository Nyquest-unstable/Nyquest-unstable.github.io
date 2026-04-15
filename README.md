# Nyquest-unstable.github.io

这个仓库现在保存的是 Hexo 源文件，使用 NexT 主题并通过 GitHub Actions 发布到 GitHub Pages。

## 本地使用

```bash
npm install
npm run server
```

本地预览地址默认是 `http://localhost:4000/`。

也可以直接使用仓库内脚本：

```bash
./start-local.sh
```

默认同样会启动到 `http://127.0.0.1:4000/`。

## 在线查看

这个站点的公开访问地址是：

`https://nyquest-unstable.github.io/`

需要注意：

1. `http://localhost:4000/` 只是本地预览地址，只有你自己的机器能直接访问
2. 互联网上查看时，应访问 GitHub Pages 地址 `https://nyquest-unstable.github.io/`
3. GitHub Pages 不是实时本地预览，只有推送到仓库并完成部署后，线上页面才会更新

## 构建

```bash
npm run build
```

生成结果会输出到 `public/`，该目录已经在 `.gitignore` 中排除，不需要提交。

## GitHub Pages

按 Hexo 官方文档，仓库应使用 `GitHub Actions` 作为 Pages 发布源。这个仓库已经包含 [.github/workflows/pages.yml](/home/lubancat/github_workspace/Nyquest-unstable.github.io/.github/workflows/pages.yml)。

线上发布流程如下：

1. 提交并推送代码到 `master`
2. GitHub 自动触发 `Pages` workflow
3. workflow 构建成功后，GitHub Pages 更新 `https://nyquest-unstable.github.io/`

在 GitHub 上需要确认：

1. 仓库名为 `Nyquest-unstable.github.io`
2. 默认分支是 `master`
3. `Settings > Pages > Source` 选择 `GitHub Actions`

如果你在互联网上暂时看不到页面，优先检查：

1. 最近一次 `Actions > Pages` 任务是否成功
2. 是否确实访问了 `https://nyquest-unstable.github.io/`，而不是本地 `localhost` 地址
3. 推送的分支是否为 `master`
4. GitHub Pages 部署是否还在生效延迟中，通常等待几分钟后再刷新

## 内容说明

- 现有文章已经从静态页面恢复到 `source/_posts/`
- 原先依赖内网 WordPress 的两张图片已改为本地占位图，避免 GitHub Pages 上出现坏链
