# Grok Imagine

状态：官方文档已核对；本工作流未做 Grok 生成实测。

1. 使用账户实际可用的图像编辑功能。若支持多图，按主体、头像参考、全身参考的顺序添加有权使用的输入，并在提示词中按该顺序明确职责
2. 粘贴 `prompts/avatar.md` 的中文或英文版本。选择方形构图（界面有该选项时）；不要把 OpenAI 的 `transparent_background` 参数移植到 Grok
3. 当前 xAI 官方多图文档写明支持最多五张输入，并支持按输入顺序引用及 `aspect_ratio` 覆盖。此说明不保证每个 Grok UI/订阅都暴露相同功能；以实际入口为准
4. 未核实原生 alpha 导出。默认请求浅蓝背景的方图与完整圆形安全构图，下载后检查模式，再使用本地 `finish_circle.py`。RGB 输入需显式 `--allow-rgb`
5. 若入口只支持一张图，优先主体照片并用文字风格约束；说明失去双参考约束。固定角色复现任务则请换可用多图入口或先补足条件，不承诺身份一致

本仓库不提供 API 调用器，不要求输入 API key，也不自动切换付费服务。参考：[xAI 多图编辑官方文档](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing)。
