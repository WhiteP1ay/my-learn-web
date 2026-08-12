# My Learn Web

AI-driven mastery learning dashboard — 可视化 AI 全栈学习进度。

## 是什么

一个纯静态 HTML 页面，搭配 JSON 数据层，追踪从前端开发转型 AI 全栈工程师的学习进度。

- 4 个 Phase（Python 后端 / AI 工程 / Java 企业 / 运维）
- 每章掌握度 0-4 分，颜色区分
- 一键复制命令 → 粘贴到终端交由 [Hermes Agent](https://github.com/NousResearch/hermes-agent) + [my-learn skill](https://github.com/WhiteP1ay/my-skills) 执行教学
- 可复习池 + 学习计划 + 停车场

## 使用

```bash
cd web
python3 -m http.server 8080
# 浏览器打开 http://localhost:8080
```

或者直接双击 `web/index.html`（需要浏览器允许 file:// 协议读取内联数据）。

## 数据更新

Hermes Agent 教学完成后自动更新 `data/` 下的 JSON 文件，刷新页面即可看到最新进度。

## 项目结构

```
├── data/
│   ├── curriculum.json      # 课程结构（Phase → Group → Chapter）
│   ├── learning-state.json  # 当前进度、复习池、学习计划、停车场
│   └── profile.json         # 学习者画像
└── web/
    └── index.html            # 单页可视化（内联 CSS/JS，零依赖）
```
