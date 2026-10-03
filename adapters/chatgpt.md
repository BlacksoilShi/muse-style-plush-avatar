# ChatGPT / OpenAI

状态：提示词与工作流适配；公开包未做端到端回归。

有图像编辑工具时同时提供可用的主体图、头像参考和全身参考，并明确各自职责。聊天 UI 中直接附图与粘贴提示词；支持 Agent Skill 的宿主按其安装说明加载 `SKILL.md`。两种用法不等同。

若宿主提供内置 `image_gen`，遵守该工具当前参数说明。仅当它明确提供 `referenced_image_paths` 时用本地输入路径；全部必要图片必须可见，缺失时不要声称已传入。圆外透明用工具正式支持的透明选项，而不是在提示词里假造接口参数。

OpenAI API 官方文档说明可配置透明背景，并选择支持 alpha 的 PNG/WebP 格式。这不意味着每个聊天入口都提供相同参数。本仓库不调用 API、不存储凭证，运行者必须以当前接口文档为准。

生成后查看构图与 alpha。若运行环境允许请求中的 Python 后处理，按主工作流用 `finish_circle.py` 收尾；否则交付原图并说明圆边尚未验证，不能声称脚本已运行。

参考：[OpenAI 图像生成官方文档](https://developers.openai.com/api/docs/guides/image-generation)。
