# Muse-style Plush Avatar

**非官方灵感项目，与 Meta/Muse 无隶属、授权或背书关系，不提供官方角色资产。**

跨模型毛绒头像提示词与 Agent Skill：照片 → 奶油短绒小人 → 可选的圆形透明 PNG。

中文工作流、可复制中英提示词、ChatGPT/Grok/Meta Muse/通用适配说明，以及独立的 Python 圆边收尾工具。模型负责造型；本地脚本只负责确定性的圆形 alpha，不训练模型、不调用付费 API。

## 快速开始

1. 在支持 Skill 的 Agent 中按该产品说明加载本目录的 `SKILL.md`。普通聊天产品无需安装：直接复制 `prompts/avatar.md`，再读取对应 `adapters/` 说明
2. 准备你有权使用的主体照片，以及可选的头像与全身双参考；可本地放入 `local-inputs/`、`local-references/`。这些目录和常见图片格式被 `.gitignore` 排除，不要强制提交个人照片
3. 选择模型实际支持的图片输入/编辑方式。明确每张图的作用，生成方形、圆形安全构图的头像
4. 检查完整头部、发型、眼镜、配色、材质与配件；需要真实圈外透明时运行本地脚本

不附带第三方参考图片。没有参考图也可使用文字模式生成原创近似风格，但不能保证还原某个已有角色。

## 适配状态

- ChatGPT / OpenAI：提示词和工作流适配；API 透明输出能力核对官方文档。此公开版本未做端到端生成回归
- Grok Imagine：官方多图编辑能力已核对；可按顺序提供主体、头像、全身参考。未实际调用验证本风格，未核实原生 alpha，使用本地收尾兜底
- Meta Muse：这里指 Meta 的个人 AI Agent，不是 Google 同名研究模型。公开材料说明自定义形象；本包只提供按实际界面能力执行的手工适配，未证实开放图片编辑 API、双参考输入或透明导出，也未实测
- 其他模型：能力门控的手工提示词方案；文字模式只承诺描述风格，不承诺图片身份/角色一致性

能力来源与复核日期见 [SOURCES.md](SOURCES.md)。本项目不宣称任意平台原生支持 Skill 安装。

## 圆形透明收尾

Python 3.10+ 和 Pillow。无网络请求、无 API key。建议在虚拟环境运行：

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

先查看生成图的实际像素，测量圆心、半径和关键特征极值。下列是**仅适用于 64×64 合成测试图**的示例，不要把数字直接用于你的头像：

```bash
python scripts/finish_circle.py outputs/generated.png outputs/circle.png \
  --center 31.5 31.5 --radius 28 \
  --protect-point 31 10 --reviewed --qa-dir qa/run-001
```

真实图片请用自己的测量值替换，重复 `--protect-point X Y` 保护所有重要极值。点必须距离圆边至少 3 像素。`--reviewed` 是你已审核的声明，不是脚本替你做了视觉检查。

- RGBA 输入：只降低 alpha；内部 RGBA 与 RGB 保持不变
- RGB 输入：额外加 `--allow-rgb` 才能处理。增加初始 alpha=255，再裁圆；RGB 指解码后像素，不保证 JPEG 文件字节不变
- 灰度、调色板、动画、有未归一化 EXIF 方向的图：拒绝。先另外准备规范图片并重审
- 圆边采用 4×4 子像素覆盖率，约 1 像素抗锯齿带；验证圆外指像素中心距圆心大于 radius+1 的区域
- 不改变画布大小、不重绘、不抠角色、不修白边、不使内部透明变实心、不自动估计圆心或保证保护点以外的特征安全
- 原图和已有输出不会覆盖，QA 必须使用新目录。QA 包含 `dark.png`、`light.png` 和 `verification.json`，均用于本地检查
- 输出重建自像素，避免携带源 EXIF；隐形 RGB 未清零是为了遵守 RGB 不变。不要把透明当成敏感信息擦除，公开前检查所有像素

## 测试与限制

单元测试使用合成图，不含照片和第三方素材。覆盖 alpha/RGB 不变性、圆外透明、保护点、非法几何、拒绝覆盖、RGB 显式转换、模式拒绝和 CLI。实际外部模型未运行；提示词的可移植性不等于视觉结果一致性。

发布前可运行：`python -m unittest discover -s tests -v`。不要把输入照片、模型输出、凭证或个人账户标识提交到仓库。`.gitignore` 不是数据防泄漏安全边界。

## 许可与参考资产

仓库原创代码与文档采用 MIT。参考图片、照片、第三方角色、商标以及外部模型输出不在本项目 MIT 授权范围内；本仓库不提供这些资产。请自行取得必要权利并遵守模型服务条款。此项目与 OpenAI、xAI、Meta 无隶属或背书关系。

本流程的参考方向包括 Meta Muse 的柔软角色形象；只链接官方背景资料，不分发截图或宣称拥有其角色版权。见 [SOURCES.md](SOURCES.md)。
