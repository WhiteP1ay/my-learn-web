# My Learn Web

AI 全栈工程师学习进度看板 — 供 Hermes Agent 读取并执行一对一教学。

## 是什么

朴昊哲（前端开发）转型 AI 全栈工程师的个人学习系统。由一个纯静态 HTML 页面 + 三个 JSON 数据文件组成，零依赖。

Hermes Agent 读取 `data/` 下的文件，根据课程安排和当前进度执行教学，教学完成后更新 JSON 并同步到 HTML，push 到 GitHub Pages 自动部署。

- 在线地址: https://whitep1ay.github.io/my-learn-web/
- 本地预览: `python3 -m http.server 3333 -d docs/`

## 项目结构

```
my-learn-web/
├── data/                    ← Agent 读写的数据层（JSON）
│   ├── curriculum.json      # 课程大纲：Phase → Group → Chapter
│   ├── learning-state.json  # 学习进度、复习池、停车场、upcoming plan
│   └── profile.json         # 学习者画像（已有技能、偏好、目标）
├── docs/
│   └── index.html           # 可视化看板（内联 CSS/JS，零依赖）
└── README.md
```

**数据流**: `data/*.json`（Agent 更新） → 手动同步到 `docs/index.html` 内联 DATA → GitHub Pages 渲染

## 数据文件详解

### curriculum.json

课程大纲树。顶层是 `phases` 数组，每个 Phase 包含多个 `groups`，每个 Group 包含多个 `chapters`。

```jsonc
{
  "phases": [
    {
      "id": "phase1",
      "name": "Phase 1: Python + 数据库 + 后端地基",
      "groups": [
        {
          "id": "python-core",
          "name": "Python 语言核心精讲",
          "chapters": [
            {
              "id": "py-1",                    // 唯一 ID（phase前缀-序号）
              "name": "Python 环境搭建与工具链", // 显示名称
              "mastery": 3,                     // 0=未学 1-2=学习中 3=学完 4=精通
              "evidence": "能独立用 uv 创建项目...", // 学完后可验证的具体产出
              "strategy": "completed",          // 教学策略（见下方）
              "note": "类比：相当于前端用 pnpm...",  // 前端类比（可选）
              "merge_note": "合并了原 A、B、C 三个章节" // 合并说明（可选）
            }
          ]
        }
      ]
    }
  ],
  "meta": {
    "last_updated": "2026-08-12",
    "project_spine": "AI 客服工单系统",     // 贯穿全课程的项目
    "current_phase": "phase1",
    "current_position": "py-14. 类型系统进阶",
    "session_count": 6
  }
}
```

#### 教学策略 (strategy)

| 策略 | 含义 | Agent 行为 |
|------|------|-----------|
| `comprehensive` | 完整教学 | 系统讲解 + 练习 + 验证 evidence |
| `completed` | 已学完 | 跳过，可出现在复习池 |
| `fast_track` | 速通 | 利用已有知识对比差异，快速过 |
| `in_project` | 项目中学 | 不单独讲，在项目遇到时即时教学 |
| `deferred` | 延后 | 暂时不学 |
| `optional` | 选学 | 用户决定是否学 |
| `next_up` | 下一节 | 当前即将学习的章节 |

#### Chapter 设计原则

每节课 45-60 分钟，有清晰边界：
- `evidence` 是可验证的具体产出（不是为了凑数）
- `note` 优先用前端类比降低学习曲线
- 过细的概念已合并，过重的主题已拆分

### learning-state.json

当前学习状态，驱动 UI 展示和 Agent 教学决策。

```jsonc
{
  "current": {
    "phase": "phase1",
    "knowledge_point": "py-14. 类型系统进阶（类型标注与ABC）",
    "session": 6                      // 已完成课时数
  },
  "review_pool": [                    // 掌握度 3/4 的章节，需定期复习
    {
      "chapter_id": "py-1",
      "chapter_name": "Python 环境搭建与工具链",
      "mastery": 3,
      "max_mastery": 4,
      "gap": "未独立处理版本冲突..."  // 还差什么达到 4
    }
  ],
  "upcoming_plan": [                  // 接下来要学的章节 ID
    "py-14 → py-17 → db-1 → db-2 → db-3 → fw-1"
  ],
  "parking_lot": [                    // "停车场"：在项目中碰到的即时教学
    {
      "chapter": "py-11 装饰器",
      "trigger": "项目中需要路由权限校验或计时器时触发"
    }
  ]
}
```

### profile.json

学习者画像 — 不变的基础信息。

```jsonc
{
  "name": "朴昊哲",
  "goal": "从前端开发转型为可独立交付的 AI 全栈工程师",
  "existing_skills": ["Vue", "React", "TypeScript", ...],
  "preferences": {
    "language": "中文",            // 教学语言
    "keep_english_terms": true,    // 保留英文术语不翻译
    "use_frontend_analogies": true, // 用前端概念做类比
    "require_evidence": true,      // 每章必须有可验证的产出
    "skip_frontend_basics": true   // 跳过 JS/HTML/CSS 基础
  }
}
```

## Agent 教学流程

```
1. 读取 data/profile.json      → 了解学习者背景和偏好
2. 读取 data/curriculum.json   → 找到 current_position 对应的章节
3. 读取 data/learning-state.json → 了解复习池和停车场
4. 执行教学（45-60 分钟）:
   a. 根据 strategy 决定教学方式
   b. 用前端类比解释概念（profile.preferences.use_frontend_analogies）
   c. 用 evidence 验证学习成果
   d. 记录到 session（session_search 可回顾历史）
5. 更新数据:
   a. curriculum.json: 更新 mastery 和 strategy
   b. learning-state.json: 更新 current、session、review_pool
   c. docs/index.html: 同步内联 DATA（使 GitHub Pages 反映最新进度）
6. git commit + push
```

## 更新 HTML 内联数据

`docs/index.html` 中的 `const DATA` 对象需要与 `data/*.json` 保持同步。

每次更新 JSON 后，用以下脚本自动生成 HTML：

```bash
cd /Users/piaohaozhe/asuka/my-learn-web
python3 scripts/sync-html.py
```

（脚本需要从 curriculum.json + learning-state.json 生成 HTML 内联的 DATA 对象）

## 本地开发

```bash
# 启动本地服务器
cd /Users/piaohaozhe/asuka/my-learn-web
python3 -m http.server 3333 -d docs/

# 访问
open http://localhost:3333
```

## 部署

Push 到 `main` 分支，GitHub Pages 自动从 `docs/` 目录部署。

```bash
git add -A && git commit -m "描述变更" && git push
```

## 关键约定

- **章节 ID 格式**: `{前缀}-{序号}`，如 `py-14`、`db-1`、`rag-3`。不可重名。
- **每节 45-60 分钟**: 合并过细的，拆分过重的。
- **evidence 可验证**: 不是笼统的"理解 xxx"，而是"能用 xxx 做 yyy"。
- **前端类比**: 每个新概念如果找得到前端对应物，必须在 note 中类比。
- **项目贯穿**: 所有练习围绕 `project_spine`（AI 客服工单系统）展开。
- **更新后同步 HTML**: JSON 是数据源，HTML 是渲染面，两者必须一致。
