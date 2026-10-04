# 可复制短提示与定向修正

一次只用适合当前输入的一条。把方括号替换成实际观察，删掉无关项。不要把测量报告、API参数、全部修正句一起粘贴给模型。平台专用首轮见 [Grok](../adapters/grok.md) 与 [Muse](../adapters/muse.md)。

## 双图通用版

输入顺序：A共同脸部母版在前，B当前主体在后。确认图像工具确实收到两张图。

> 图1提供脸部模板，图2提供当前角色外观。保持图1独立圆角矩形织布面的宽高位置、黑珠眼、短弧笑口和粉腮红。将外部造型完整换成图2：[发型、刘海、耳朵、配饰、衣服与层次]，去掉图1不属于当前角色的发型、头饰和衣服。刘海可覆盖额头外层绒边，布面和五官完整可见，脸边留可读奶油绒内缘。正面毛绒胸像，丰满肩身直接接头，无细颈。保留服装与饰物的可辨形状，1:1浅蓝圆盘构图，无文字。

English alternative (use instead of, not in addition to, the Chinese prompt):

> Edit image 1 using image 2 only for the character's outer appearance. Keep image 1's separate rounded-rectangle woven face panel at the same size and position, with the same black bead eyes, curved smile and pink cheeks. Replace the hair, bangs, ears, accessories and complete visible outfit with image 2: [observed details]. Remove image 1's unrelated hair, ornaments and clothing. Bangs may cover the outer forehead fur, but leave the cloth face and features visible with a readable cream-fur inner rim. Front-facing stuffed plush bust, full soft shoulders directly supporting the head, no thin neck. Preserve recognizable outfit layers and accessory shapes. Square pale-blue circular-avatar composition, no text.

## 只有一张编辑输入时

只上传A。执行者先实际看B再填写描述；不要声称生图模型收到B。

> 编辑这张共同母版，只替换布面以外的造型为：[完整外观描述与位置关系]。保持独立圆角矩形织布脸的大小位置、黑珠眼、短弧笑口和粉腮红。刘海可压住额头外层绒缘，脸面和五官完整露出，沿脸留奶油绒内缘。保留完整发型与服装层次、可读配饰；去掉母版不属于目标角色的旧造型。正面平视毛绒胸像，头直接接丰满肩身，无细颈，维持脸部尺度与圆盘构图。

这条路径丢失B的视觉条件，可能不如实际双图保留细节；不是性能保证。

## 定向修正：每次只挑一条

只在脸合格时把当前图作为编辑底图；若脸已偏移，回到A+B重新做，并引用A的几何。引用来源图的句子只在来源真的同时输入时使用，否则改写成已观察的具体外观。

- **刘海/分层丢失：** “只补回来源中的[刘海扫向、层次和发髻]，保留当前织布脸与五官位置。头发自然覆盖额头外层绒缘，不遮布面；保留完整发型，不缩成后侧小毛束。”
- **衣服变胸前色块：** “只恢复[外套、领口、翻领、袖肩、花纹和层次]的完整可见形状，服装包住丰满毛绒肩身。保留当前脸和头部位置，不加细颈或真人腰身。”
- **鱼/花被缩成徽章：** “只把[配饰]恢复为来源可辨的完整形状，放在[实际位置关系]，保留自然体积与颜色。维持脸和构图；如果圆内放不下，请指出冲突，不自行改成徽章。”
- **母版串色：** “只将残留的[具体母版特征]换成[来源特征]。保留当前合格的脸、五官与其他已正确造型。”
- **出现细脖子：** “只修正头下连接：丰满柔软的毛绒肩身直接承托头部，领口包覆这一体积，不藏一根细颈柱。脸的大小、位置及服装辨识细节保持不变。”

## 文件步骤：可选不透明中间图

仅在确实需要修复透明文件、且后续圆边处理已获授权时，对当前合格图单独操作：

> 只把背景与输出改为完全不透明的浅蓝方形中间图。保留当前角色的脸、五官、头发、饰物、服装、头身承托、镜头和位置。不要重构或缩放角色，不画棋盘格。这个中间图暂不需要透明。

真实输出模式由平台能力决定，文字要求不等于文件已合格。重新检查RGB/RGBA、角色和构图后再收尾；不能用旧报告代替新文件检查。
