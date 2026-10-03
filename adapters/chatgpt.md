# ChatGPT / OpenAI

状态：提示词与工作流适配；公开包未做端到端回归。

先用用户授权参考建立一次固定母版。正常转换先实际读源图提取文字特征，再分阶段只把母版／上一阶段合格图作为图像工具输入，不直接混入原人物照片。聊天 UI 中直接附图与粘贴提示词；支持 Agent Skill 的宿主按其安装说明加载 `SKILL.md`。两种用法不等同。

若宿主提供内置 `image_gen`，遵守该工具当前参数说明。仅当它明确提供 `referenced_image_paths` 时用本地输入路径；全部必要图片必须可见，缺失时不要声称已传入。角色阶段请求透明时用工具正式支持的透明选项，不假造参数。对主流程中特别请求的不透明方形技术中间图，内置工具可按真实参数使用 `transparent_background: false`；最后由已授权alpha蒙版恢复透明圈外，不能把该中间图误当最终透明文件。

OpenAI API 官方文档说明可配置透明背景，并选择支持 alpha 的 PNG/WebP 格式。这不意味着每个聊天入口都提供相同参数。本仓库不调用 API、不存储凭证，运行者必须以当前接口文档为准。

生成后查看构图与 alpha。若运行环境允许请求中的 Python 后处理，按主工作流选择原生透明路径或“模型先出不透明中间图”的路径，再用 `finish_circle.py` 收尾（真RGB须显式 `--allow-rgb`，不填旧RGBA内部alpha）；否则交付原图并说明圆边尚未验证，不能声称脚本已运行。

参考：[OpenAI 图像生成官方文档](https://developers.openai.com/api/docs/guides/image-generation)。
