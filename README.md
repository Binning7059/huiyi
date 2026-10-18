# 回译训练句库

按搭配间隔复习的英语回译训练，题材覆盖雅思和 PTE 常见话题，难度 B2–C1。

## 文件

| 文件 | 内容 |
|---|---|
| `index.html` | 练习页面：今日队列、句库、进度统计 |
| `bank.json` | 句库数据：句子、搭配、翻译技巧标签 |

## 部署到 GitHub Pages

1. 新建一个公开仓库，例如 `huiyi`。
2. 把 `index.html`、`bank.json` 和本文件上传到仓库根目录。
3. 打开仓库的 **Settings → Pages**，在 Source 里选 **Deploy from a branch**，分支选 `main`，目录选 `/ (root)`，保存。
4. 一两分钟后访问 `https://<你的用户名>.github.io/huiyi/`。

## 更新句库

只需替换 `bank.json` 并提交，页面刷新后就会用上新句子，已有进度不受影响。

## 进度保存

进度保存在浏览器本地。换设备或清理浏览器数据之前，请在「进度」页导出备份，到新设备上再导入。

直接双击打开 `index.html` 无法载入句库（浏览器禁止本地页面读取文件），请通过 GitHub Pages 访问，或在本目录运行 `python3 -m http.server` 后打开 `http://localhost:8000`。
