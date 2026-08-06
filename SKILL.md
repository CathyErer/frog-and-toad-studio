---
name: frog-and-toad-studio
description: >-
  Frog and Toad 精读课 studio (Arnold Lobel, I Can Read L2, ESL G1). Generates the
  per-chapter 三件套 — a 关键词地图 projection HTML (locked cream-paper house style),
  a one-page Student Workbook .docx, and an Answer Key 答案版 .docx (red bold underlined
  answers) — plus optional per-lesson 课程总结与作业 (WeChat-ready) and Obsidian sync. Trigger
  whenever the user asks to make, redo, update, or fix ANY Frog and Toad teaching material: "做 Frog and
  Toad 三件套", "第X章 关键词地图 / workbook / 练习册 / 答案版", "青蛙和蟾蜍", "重新生成
  Spring 的 workbook", "更新课程总结", "列出下一章关键词", "按 Frog and Toad 风格做"; or when
  they upload/reference Frog and Toad book PDFs (Days with Frog and Toad / All Year /
  Together / Are Friends) or mention Frog, Toad, Arnold Lobel with a request for 课件, 教案,
  worksheet, 复述, or 作业. Also use it as the house-style base when the user asks to do another
  bridge book "像 Frog and Toad 那样".
---

# Frog and Toad Studio · 三件套工作流

本 skill 面向教 ESL G1（一年级）学生的老师。每个故事 = 一次课 = 一个三件套：

1. **`0M - <Chapter> 关键词地图.html`** — 投屏 lesson plan，锁定风格（奶油纸+手写风），5 个 tab（含 Vocabulary）
2. **`0M - <Chapter> Workbook.docx`** — 单页学生练习
3. **`0M - <Chapter> Workbook 答案版.docx`** — 答案版，答案红色加粗下划线

外加（按需）：**课程总结与作业（微信版）** 段落、**Obsidian 同步**。

## 运行前配置

不要写死或猜测用户电脑上的路径。先确定三个路径变量：

- `<SKILL_DIR>`：当前 `SKILL.md` 所在的 Skill 文件夹，无需用户设置
- `<COURSE_ROOT>`：Frog and Toad 课程资料根目录
- `<OBSIDIAN_DIR>`：Obsidian 中的 Frog and Toad 课程追踪目录

首次运行时读取 `<SKILL_DIR>/config.local.json`。若文件不存在，参考
`<SKILL_DIR>/config.example.json`，向用户确认 `<COURSE_ROOT>` 和 `<OBSIDIAN_DIR>` 后创建本地配置。
找不到目录时必须询问用户，不得根据用户名或常见文件夹位置猜测。

模板、脚本和参考资料始终相对于 `<SKILL_DIR>` 定位。本地配置和生成的微信版课程总结不得提交到公开仓库。

## 文件夹与命名约定

素材库：`<COURSE_ROOT>/`

```
Frog and Toad精读课/
├── 1.days with frog and toad/    ← 课 01–05（Tomorrow/Kite/Shivers/Hat/Alone）
├── 2.frog and toad all year/     ← 课 06–10
├── 3.frog and toad together/     ← 课 11–15
├── 4.frog and toad are friends/  ← 课 16–20
│   ├── 1.Frog and Toad Are Friends.pdf   ← 扫描版原书
│   └── 1-Spring/                 ← 每章一个文件夹 <M-Chapter>/
│       ├── 01 - Spring 关键词地图.html
│       ├── 01 - Spring Workbook.docx
│       └── 01 - Spring Workbook 答案版.docx
```

Skill 文件夹：`<SKILL_DIR>/`。其中可保存本地生成的
`课程总结与作业（微信版）.md`，也可按需从当前正式源生成安装包；这类本地文件不提交到公开仓库。

**教学顺序 = 文件夹书序**（Days with → All Year → Together → Are Friends），全系列课号 01–20。

Obsidian 库：`<OBSIDIAN_DIR>/`
- `00 - Frog and Toad 全系列课程地图.md` — 20 课寓意 + inference 问题总表
- `0N - <Book> 关键词地图.md` — 每本书一份，每章一节（含 ✅三件套已生成 标记）
- `0N - <Book>.md` — 追踪笔记，升级日志加一行（带 wikilink）
- `课程总结与作业（微信版）.md` — 与 `<SKILL_DIR>/课程总结与作业（微信版）.md` 保持同步

## 工作流（7 步，顺序执行）

### 1. 读原文（扫描 PDF 无文字层）

用 pypdfium2 渲染成图再 Read（视觉转录）：

```python
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument("<book>.pdf")
for i, page in enumerate(pdf):
    page.render(scale=1.5).to_pil().save(f"outputs目录/pXX.png")
```

每张 PNG 是一个跨页（2 个书页）。用 Read 工具逐张读图、逐字转录。**引文必须逐字**——
后面 HTML/Workbook 里的所有 quote 都要能在原文找到（历史教训：dumb≠dump、
"I am feeling much better now"≠"I feel much better"、"on the front door"≠"at the front door"）。

### 2. 先列关键词，确认后再动手

**绝不跳过**：先把关键词列表发给用户确认，再开始生成（"先列出关键词，再来做"）。
粒度是「中间版」——历史校准中"字太多"和"这也太精简啦"都被反馈过，收敛后的标准：

- **寓意**（英文 moral + 中文短释）
- **核心 inference 问题**（Why did …? 一课一个，笑点藏在"说的和做的不一致"里）
- **关键词复述线**：场景小标题 + emoji 开头的 bullet + **加粗关键词** + 简短逐字引文
- **动词词库**（6 个，供 Workbook 填空）+ **寓意填空**（2 个空）

若用户上传了手绘关键词地图，以用户的图为准挑关键词。

### 3. 生成关键词地图 HTML

**复制 `<SKILL_DIR>/assets/template_keyword_map.html`，只换内容，绝不发明新版式。**
五个 tab 固定：① Warm-up 读前（3 张 q-card：聊自己→标题猜想→带问题读）
② Vocabulary 10 个核心词汇（英文解释 + 中文解释 + 例句）
③ The Story Map 复述路线 ④ Characters 人物+情绪线 ⑤ Theme 寓意。

版式部件（按故事结构选用）：
- `.route` 路线卡：**每一段都必须用 `<span>` 包住**（flex 容器裸文本会错误换行——历史 bug）
- `.mishap` 网格：3 项默认 / 4 项加 `.four` / 5 项加 `.five`
- `.idea` / `.we-know`（红色手写金句）/ `.morning` / `.gold`（金色寓意卡）/ `.sad-line`
- `.feel-line` 情绪线固定 **6 站**：📍节点卡（先读发生了什么）→ emoji → 心情标签
- `.char-grid` 两张人物卡，各带一个句型支架 `.frame`（"___ is ___ because ___."）

语言规则：中文都放 `<span class="zh">` 里（EN only 按钮会隐藏）；正文关键词式精简；
标题区 moral-tag = 寓意；footer 写 Lesson N。
词汇规则：Vocabulary tab 的主数据来自 Obsidian `0N - <Book> 关键词地图.md` 中每课的
`10 个词汇（中英解释 + 例句）` 模块；本地同步脚本为
`<SKILL_DIR>/scripts/sync_vocabulary_to_html.py`。

**自检**：Python HTMLParser 做标签平衡检查（历史上每次都查）。

### 4. 生成 Workbook 两件

用 `<SKILL_DIR>/scripts/make_workbooks.py`：照 `EXAMPLE`（Spring）的 shape 写新 config、
调 `build(cfg, False/True, path)` 生成学生版+答案版。规格已内置（Letter、Arial、
三列固定表格、红色答案、无 emoji）。四个 Part 固定：
Story Map 填动词（6 行，cue 逐字引文）→ Think! 推断题 → 寓意填空（2 空）→ Draw! 画图框+一句话。

**自检**：soffice 转 PDF 断言**每个文件恰好 1 页**（超页就精简 cue/closing 文字）。

### 5. 逐字核对

把 HTML + Workbook 里的每条引文与转录原文比对一遍。宁可删引号改叙述，不可改动原句。

### 6. Obsidian 同步（可选）

用户未使用 Obsidian 或未配置 `<OBSIDIAN_DIR>` 时跳过本步（此时第 3 步的词汇数据改为直接向用户确认）。
使用 `config.local.json` 中的 `<OBSIDIAN_DIR>`。同步前先确认该目录及目标笔记存在；
如果配置缺失或目录无效，停止并向用户确认，不得尝试其他 Obsidian Vault。

- 书的关键词地图笔记：追加/更新该章小节，标 `✅三件套已生成`，frontmatter `last_updated` 改今天
- 追踪笔记 `0N - <Book>.md`：升级日志加一行（日期 + 内容 + wikilink）
- 若全书完成：写"全书五章完成 ✅"

### 7. 课程总结与作业（微信版，可选）

按用户需要生成。每课一段，纯文本（微信不渲染 markdown），格式固定：

```
【Frog and Toad 精读 · <Chapter> <中文名>】

📖 今天的故事：（3-5 句中文概述，穿插英文关键句/引文）

🎯 本课重点
· 寓意：<英文 moral> —— <中文>
· 思考题：<inference 问题>
· 重点动词：<6 个>

📝 课后作业
1️⃣ 复述：打开"关键词地图"，沿 Story Map 路线把故事讲一遍（用上重点动词）
2️⃣ 完成 <Chapter> Workbook（一页）
3️⃣ 预习《<下一章>》：<一句吊胃口的预告问题>
```

最后一课的第 3 项改为全系列复习。写入
`<SKILL_DIR>/课程总结与作业（微信版）.md` 对应段落，并同步到 `<OBSIDIAN_DIR>`。

## 参考资料

- `<SKILL_DIR>/config.example.json` — 首次运行的路径配置示例
- `<SKILL_DIR>/sync-config.md` — 路径变量、资料分工和同步规则
- `<SKILL_DIR>/sync-checklist.md` — 每次检查/同步 Obsidian 时使用的固定清单
- `<SKILL_DIR>/assets/template_keyword_map.html` — 锁定的 HTML 模板（Spring 成品，含 .four/.five CSS）
- `<SKILL_DIR>/scripts/make_workbooks.py` — Workbook 生成器 + EXAMPLE config
- `<SKILL_DIR>/scripts/sync_vocabulary_to_html.py` — 从 Obsidian 关键词地图同步 Vocabulary tab 到 20 个 HTML
- `<SKILL_DIR>/references/course-map.md` — 全系列 20 课总表（寓意/思考题/动词词库），改总结或补课时查这里
- `<SKILL_DIR>/skills/frog-and-toad-illustration-style/` — 插画子 skill：画风规则 + 20 章提示词库（prompts/）+ 插图注入关键词地图 HTML 的锁定版式

## 交付清单（每章完成前过一遍）

- [ ] 关键词列表已经用户确认
- [ ] HTML 标签平衡，route 段都包了 span，中文都在 .zh 里，Vocabulary tab 有 10 个词汇卡
- [ ] Workbook + 答案版都是 1 页；答案红粗下划线；无 emoji
- [ ] 所有引文与原书逐字一致
- [ ] 章节文件夹三件套齐全，命名 `0M - <Chapter> …`
- [ ] Obsidian 两个笔记已更新
- [ ] 把生成的文件交付给用户，说明简短
