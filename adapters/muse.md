# Meta Muse（手工、按能力降级）

这里的 Muse 指 Meta 的个人 AI Agent，官方入口背景为 [How We Designed Muse](https://introducing.muse.ai/)，不是 Google 同名研究模型。

状态：核对官方产品/形象研究介绍；未运行 Muse。本包未验证公开图像编辑 API、任意照片上传、双参考条件控制、SKILL.md 原生安装、PNG 下载或真实 alpha 导出。官方自定义形象介绍不能证明这些接口存在。

1. 在你实际使用的 Muse 界面中检查是否能描述/编辑形象、是否能上传图片、是否能下载静态图。不要臆造按钮、endpoint、模型名称或透明参数
2. 若可用的是文本形象定制，将 `prompts/avatar.md` 中的风格和可见辨识点作为自然语言描述；不要让它声称读取未上传的参考图
3. 仅在当前界面明确支持参考输入时才加入主体/双参考，并写清职责。若不支持，标注“文字近似”，不能承诺复刻固定角色或照片转换
4. 若确实提供可下载的图像，下载检查后才可按主流程做本地圆形 PNG 收尾。若只显示动态形象且没有导出，就保留为平台内形象；不要声称已得到透明 PNG，不以截图冒充原生导出
5. 若 Muse 入口不能完成图片生成/导出，可以提供完整提示词，让用户自行选择其他支持图片编辑的工具；不要自动把照片转交第三方

参考：[Meta 官方介绍](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)、[形象技术介绍](https://research.meta.ai/blog/bringing-your-muse-to-life)。这些是产品/研究资料，不是本项目兼容性测试报告。
