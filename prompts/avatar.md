# 单母版、分阶段编辑 / Single-master staged edit

先实际查看源图，写出3–5个可见特征及附着区域；原图不作为默认图像工具输入。以下所有阶段只传入一张当前底图，不声称模型看了未上传照片。母版与容差须来自用户自己的已确认模板；本公开包不附带私人母版。

## 中文：阶段 A

“唯一输入图是固定毛绒角色编辑底图。来源图片已由执行者实际看图，但未传给图像工具。本轮只将这些特征转为身体外层布料：[服装主色、滚边、标志]。整个头、布面、五官、厚四边绒框和头像圆盘不动，不加头发／耳朵／头饰。身体只换面料，保持原圆胖填充体积、肩臂位置、无颈承托和裁切；无窄颈柱、真人胸腰或新姿势。保留已测母版几何：[真实归一化目标／容差]。无UI、文字、无关配件，圆外真实透明。”

无身体外观变化时跳过A。确认A仍符合母版后，才继续B。

## 中文：阶段 B

“唯一输入图是上一阶段合格的固定毛绒小人。只增加这些源图可见特征：[后侧发片／小耳朵／眼镜／饰物及明确附着区域]。保持现有身体、衣服、脸、头套、五官和圆盘不重构，不缩放、移动或下移小人。头发只在奶油头套后侧，奶油前部在发片前方；不画遮脸刘海或覆盖绒框的大假发。保留发色与扫向／长度特征，不变成无关细线。动物斑纹是在原绒毛上着色，不新增加宽头的厚毛块；眼镜围绕原珠眼，只缩镜架，不移动眼睛。大配件只缩小、侧移或改为布面之外的小扁饰，不用挤压头脸空间。保留真实母版几何：[P/H、H/D、P/D、面板宽高、中心及容差]。无新姿势、鼻梁、吻部或额外道具。圆外透明。”

无头部附件时跳过B。若B破坏几何，回到A而非继续使用错误头型；改动附件布局并重新检查。

## English: stage A

The ONLY supplied image is the fixed plush MASTER edit target. The source photo was actually inspected by the operator, but is not supplied to the image model. Change only torso fabric appearance using these observed cues: [clothing colors, piping, emblem]. Preserve the entire head, woven panel, facial features, raised four-sided cream rim, circle and camera. Add no hair, ears or head ornaments in this step. Clothing wraps the same stout stuffed body with the same shoulder/arm positions and directly connected neckless support; no thin post, human waist or new pose. Frozen measured geometry: [actual baseline targets/tolerances]. No text/UI or invented props. True transparent exterior if supported.

Skip stage A when no torso changes are needed; inspect it before stage B.

## English: stage B

The ONLY supplied image is the accepted preceding stage. Add only these actually observed appearance cues: [small rear hair pieces/ears/glasses/ornaments and attachment zones]. Keep the existing body, clothing, face, hood, facial features, framing and circle unchanged. No zoom, head shifting or reconstruction. Hair stays BEHIND the cream hood, with recognizable hue and direction/length; no front bangs across cloth, no wig replacing the rim, no meaningless generic stripe. Recolor existing fur for animal markings without widening the actual hood. Fit glasses to existing eyes, never move the eyes. Simplify/reposition accessories or use small flat ornaments outside the cloth rather than moving the mascot to fit them. Preserve measured P/H, H/D, P/D, panel aspect and center: [actual values/tolerances]. No anatomical muzzle, nose, new pose or extra props.

Skip B when no head additions are needed. If B drifts, restart that stage from the last accepted image with a genuinely different accessory arrangement, rather than building on the wrong geometry.

## Limits

If the product cannot isolate the master as the edit input, disclose the conditioning limitation; do not promise the same stability. A text-only product without a master cannot guarantee fixed geometry. An explicit full-body request uses a separate frozen full-body template, not a silent reframe of this avatar workflow. Verify actual alpha output; a checkerboard is not transparency.

## 可选技术阶段：不透明方形中间图

仅当用户／宿主允许后续alpha圆边处理时使用。只输入当前已通过造型的成图：

“仅将这张图转换为完全不透明的浅蓝方形中间图。保持角色的脸、头套、五官、头身、服装、配件、镜头和画布位置，不重构、不缩放。只将圆外背景补为同色浅蓝，并输出真正RGB或全alpha255；不要伪画透明棋盘格。中间图不需要透明，后续会单独恢复透明圆外。”

English: “Convert only the background/output opacity of this accepted avatar into a fully opaque pale-blue SQUARE intermediate. Preserve the exact visible mascot geometry, face, hood, features, clothing, accessories, camera and positions; no resizing or reconstruction. Extend only the pale-blue background. Output genuinely opaque RGB or alpha255, no checkerboard. This intermediate is intentionally opaque; authorized circular-alpha finishing follows separately.”

按工具当前实际接口选择不透明输出，不臆造参数。之后检查新造型未漂移、真实不透明，再运行有限alpha蒙版和全套最终检查；不能以旧文件的报告代替新文件。
