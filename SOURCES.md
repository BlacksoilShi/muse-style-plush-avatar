# 来源与验证范围

复核日期：2026-10-04。官方功能不等于本头像风格实测，也不等于用户当前入口全部可用。

## Grok

- [Imagine Image 2.0](https://x.ai/news/grok-imagine-image-2)：Quality Mode、多参考图、区域编辑与去背景透明导出。去背景不保证保留本任务需要的浅蓝圆盘
- [多图编辑](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing)：最多五张、按顺序引用、第一张默认影响宽高比；未据此推断第一张视觉权重更高或几何锁定
- [Build技能](https://docs.x.ai/build/features/skills-plugins-marketplaces)、[Bot技能](https://docs.x.ai/grok-bot/skills-routines-and-automations)：不同入口各有机制，不能等同于消费端Imagine上传Markdown就是安装

## Meta

- [Muse产品](https://ai.meta.com/muse/)：个人Agent包括图片生成能力
- [Muse Image / Muse Video](https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/)：Muse Image编辑、多参考合成及其发布入口；不是Muse Agent图像接口规格
- [Muse安全与技能背景](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse)：skills与工具背景；不能证明此包ZIP导入、附件转交或图像API契约
- [Muse设计](https://introducing.muse.ai/)、[形象研究](https://research.meta.ai/blog/bringing-your-muse-to-life)：视觉背景资料，不分发截图或第三方角色资产

尚未核实用户当前Muse入口的参考数量/顺序语义、区域蒙版、透明导出或本包原生安装路径。未知不代表不支持。

## OpenAI

- [图像生成](https://developers.openai.com/api/docs/guides/image-generation)：编辑、透明背景与支持alpha的输出格式。接口能力不自动等于每个聊天UI

## 验证分层

1. 既有Python合成测试验证脚本约束，不验证任何外部图像模型
2. 官方文档核对产品能力，不验证当前用户的实际入口
3. Grok/Muse新提示未做目标平台出图测试；待失败样图、入口与输入顺序后对照验证

本包未包含私人母版、照片、模型输出、凭证或账户标识。原创文档/代码许可不覆盖第三方参考资产。与OpenAI、xAI或Meta无隶属或背书关系。
