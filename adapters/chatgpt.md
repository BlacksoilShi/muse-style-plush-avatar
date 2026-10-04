# ChatGPT / OpenAI

状态：可移植提示与工作流；公开包尚未做端到端生成回归。

默认按主SKILL提交两张：A共同脸部母版，B当前主体外观。实际查看两张图，用[双图提示](../prompts/avatar.md)说明职责。若当前入口只接收一张图，使用单图降级提示并说明B未传入。不同角色不分别使用各自脸部尺度。

只有支持Skill的宿主才按其安装流程加载SKILL.md；聊天中上传文本不等于安装。若使用内置 `image_gen`，遵守该工具当前说明：所有必要图片都有本地路径时才用 `referenced_image_paths`，不与 `num_last_images_to_include` 混用。图像工具必须真的收到引用图片。

透明设置遵从当前工具参数，不把OpenAI参数复制给Grok或Muse。OpenAI官方图像API支持透明背景与PNG/WebP，但API能力不自动等于每个聊天入口。本包不调用API或存储凭证。[官方文档](https://developers.openai.com/api/docs/guides/image-generation)

先检查脸、外观和头身，再验实际alpha。需要本地圆边处理时遵循主SKILL与README的权限、保护点和不改RGB要求；没有运行工具就不能声称文件已验证。
