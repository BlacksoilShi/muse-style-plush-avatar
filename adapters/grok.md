# Grok Imagine

状态：官方文档已核对；本工作流未做 Grok 生成实测。

1. 使用账户实际可用的图像编辑功能。先实际查看来源照片并提取文字外观线索；每一阶段只上传用户自己的固定母版／上阶段合格图作为编辑底图
2. 粘贴 `prompts/avatar.md` 的中文或英文版本。选择方形构图（界面有该选项时）；不要把 OpenAI 的 `transparent_background` 参数移植到 Grok
3. 当前 xAI 官方多图文档写明支持最多五张输入，并支持按输入顺序引用及 `aspect_ratio` 覆盖。此说明不保证每个 Grok UI/订阅都暴露相同功能；以实际入口为准
4. 未核实原生 alpha 导出。可请求真实不透明浅蓝方图与完整圆形安全构图；下载后确认RGB无透明元数据或RGBA全alpha255，并检查几何未漂移，再在授权下使用本地 `finish_circle.py`。RGB输入需显式 `--allow-rgb`；不得把OpenAI透明参数移植到此平台
5. 单图编辑即可用于默认单母版流程；来源照片未传给模型须如实说明。不能隔离母版编辑条件的入口应披露稳定性限制

本仓库不提供 API 调用器，不要求输入 API key，也不自动切换付费服务。参考：[xAI 多图编辑官方文档](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing)。
