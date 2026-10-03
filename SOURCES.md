# 来源与验证范围

复核日期：2026-10-03。下列仅为官方能力来源，不是运行实测或商标授权。

- [xAI 多图编辑](https://docs.x.ai/developers/model-capabilities/images/multi-image-editing)：输入顺序、多图条件和宽高比选项。页面称最多五张；UI 和账户可用能力应现场复核
- [OpenAI 图像生成](https://developers.openai.com/api/docs/guides/image-generation)：图像编辑、透明背景与支持 alpha 的输出格式。接口选项不自动等于聊天 UI 能力
- [Meta Muse 官方产品介绍](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)、[How We Designed Muse](https://introducing.muse.ai/)、[Bringing Your Muse to Life](https://research.meta.ai/blog/bringing-your-muse-to-life)：Muse 产品与形象设计背景；不据此声称可公开调用照片转换或多参考图片编辑 API

本包的柔软角色方向参考上述公开设计背景与通用毛绒玩具视觉特征。没有复制/分发 Meta 角色截图、他人照片、训练数据或模型输出；品牌与角色权利归各自权利人。仅提供来源链接不等于取得素材再分发授权。

验证分层：
1. 本地 Python 合成图单元测试：可以运行且检查像素约束
2. 外部模型文档：已查看官方来源
3. 外部模型视觉效果：此公开版本尚未做端到端实测

添加实测记录时写明产品入口、日期、输入授权、输出格式、视觉缺陷和 alpha 检查结果；不要公开私密输入或凭证。
