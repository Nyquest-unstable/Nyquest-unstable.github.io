---
title: 使用hexo建站的一些经验
date: 2023-01-26 15:01:09
updated: 2023-01-29 23:19:05
---

# 建站的一些经验

## 修改主题

前两天运行起来了 Hexo 网站，然后今天对 Hexo 网站进行一些修改。

首先是对主题的修改，在 `_config.yml` 文件中修改：

<!-- more -->

```yml
theme: next
```

这样就指定了 `theme` 主题为 `next`，当然在这之前，需要在 `themes` 文件夹中下载好相应的文件才行：

![theme files](./image-20230126151457216.png)

在 theme 主题中的 `_config.yml` 中可以将主题修改为暗色模式：

```yml
# Dark Mode
darkmode: true
```

## 部署到 GitHub

同样是在 `_config.yml` 文件中，修改 `deploy` 选项：

```yml
# Deployment
## Docs: https://hexo.io/docs/one-command-deployment
deploy:
  type: git
  repository: git@github.com:Nyquest-unstable/Nyquest-unstable.github.io.git
  branch: master
```

在这之前需要与 GitHub 形成 SSH 通讯，否则无法在 GitHub 上部署。具体内容我参考了这篇文章：[使用 Hexo+GitHub 搭建个人免费博客教程（小白向）](https://zhuanlan.zhihu.com/p/60578464)。

## Hexo 网页使用本地图片

想要在 Hexo 搭建的网页上显示图片，有两种方法。一种是将图片上传到网络上，在服务器里直接调用网络图片；还有一种方法是，在本地保存图片，在编译静态网页时，将本地图片的地址编译到网页中。

我采用的方法是本地图片缓存。首先需要在 `_config.yml` 里修改：

```yml
post_asset_folder: true
```

这样每次创建文章时，会在同级目录下创建一个和文章名相同的文件夹，文件夹中可以保存一些富媒体文件。

其次需要使用 `hexo-asset-img` 这个插件。由于网络上的这个插件不兼容，并且不能按照 GitHub 上那个插件的下载方式下载，应该使用以下方法：

```bash
npm install https://github.com/CodeFalling/hexo-asset-image save
```

但是这样安装的插件，调用图片时使用的是以下格式：

```markdown
![image-20230129110142441](image-20230129110142441.jpg)
```

直接调用了文件，而 Typora 文章中的调用方式则是：

```markdown
![image-20230129110142441](.\文章名\image-20230129110142441.jpg)
```

所以需要对插件进行修改，在 Hexo 网站的根目录下找到 `node_modules` 文件夹，再找到 `hexo-asset-image`。
