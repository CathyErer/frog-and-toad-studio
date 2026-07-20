# Frog and Toad 同步配置

## 目标

这份配置用来固定 Frog and Toad 精读课的同步规则：主资料库负责保存课程成品，Obsidian 负责保存课程索引、追踪和家长沟通文本。

以后检查或更新同步时，以本文件为准。

## 路径配置

不要在公开文件中保存个人电脑的绝对路径。使用以下三个变量：

- `<SKILL_DIR>`：当前 `SKILL.md` 所在的 Skill 文件夹
- `<COURSE_ROOT>`：Frog and Toad 课程资料根目录
- `<OBSIDIAN_DIR>`：Obsidian 中的 Frog and Toad 课程追踪目录

`<COURSE_ROOT>` 和 `<OBSIDIAN_DIR>` 从 `config.local.json` 读取。首次使用时复制
`config.example.json` 为 `config.local.json`，填写当前电脑的真实路径。`config.local.json`
已被 `.gitignore` 排除，不得提交到 GitHub。

若本地配置缺失或目录不存在，停止同步并向用户确认，不得猜测路径。

### 主资料库

`<COURSE_ROOT>`

这里保存所有正式课程成品：

- `00_课包管理/` 课包说明、成品清单、交付检查记录
- 每章 `关键词地图.html`
- 每章 `Workbook.docx`
- 每章 `Workbook 答案版.docx`
- 每章 mp3 音频
- `90_参考资料/` 原书 PDF / Homework PDF / Study Guide
- `99_归档/` 旧同步副本和历史残留文件，不作为正式课件来源

Skill 可以安装或克隆到其他位置，以 `<SKILL_DIR>` 为准，不要求位于主资料库内部。

### Skill 文件夹

`<SKILL_DIR>`

这里保存生成规则、脚本、模板和同步配置。

入库文件（随公开仓库分发）：

- `SKILL.md`
- `README.md`
- `LICENSE`
- `config.example.json`
- `sync-config.md`
- `sync-checklist.md`
- `assets/template_keyword_map.html`
- `scripts/make_workbooks.py`
- `scripts/sync_vocabulary_to_html.py`
- `references/course-map.md`
- `skills/frog-and-toad-illustration-style/`

本地文件（已被 `.gitignore` 排除，只存在于自己电脑上，不提交）：

- `config.local.json` — 本机路径配置
- `课程总结与作业（微信版）.md` — 微信版总结主文件
- `Frog and Toad 课程设计思路.md` — 私人设计笔记
- `frog-and-toad-studio.skill` — 本地打包产物

### Obsidian 课程追踪目录

`<OBSIDIAN_DIR>`

这里保存课程索引和追踪记录。每次需要读写 Obsidian 时，只申请这个目录的权限。

## 同步原则

### 主资料库是成品来源

`.html`、`.docx`、`.mp3`、`.pdf` 默认不复制进 Obsidian。它们留在主资料库对应章节文件夹里。

### Obsidian 是追踪和索引

Obsidian 里需要保持这些文件：

- `00 - Frog and Toad 全系列课程地图.md`
- `01 - Days with Frog and Toad 关键词地图.md`
- `01 - Days with Frog and Toad.md`
- `02 - Frog and Toad All Year 关键词地图.md`
- `02 - Frog and Toad All Year.md`
- `03 - Frog and Toad Together 关键词地图.md`
- `03 - Frog and Toad Together.md`
- `04 - Frog and Toad Are Friends 关键词地图.md`
- `04 - Frog and Toad Are Friends.md`
- `课程总结与作业（微信版）.md`

### 微信版总结的主文件

主文件在：

`<SKILL_DIR>/课程总结与作业（微信版）.md`

Obsidian 中的同名文件是同步副本。更新微信版总结时，先改 studio 里的主文件，再覆盖同步到 Obsidian。

## 完成标记标准

每个故事完成后，Obsidian 的对应关键词地图小节标题应包含：

`✅三件套已生成`

每本书五章全部完成后，对应追踪笔记的升级日志应写明：

`全书五章完成 ✅`

全系列完成后，Book 4 追踪笔记应保留全系列完成记录。

## 权限规则

默认只读写主资料库。需要检查或同步 Obsidian 时，申请以下目录的读写权限：

`<OBSIDIAN_DIR>`

不需要申请整个电脑权限。
