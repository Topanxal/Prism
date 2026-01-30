# Prism Health AI Agent - 问题诊断与测试计划

## 1. 当前存在的问题 (Current Issues)

### 1.1 音频生成的实现确认 (Audio Generation Verification)
*   **现状**: 代码逻辑假设 Wan2.6 模型生成的视频文件中自带音频。`Wan26Adapter` 目前并未传递显式的音频生成参数（如 `audio_prompt` 或 `enable_audio`）。
*   **潜在问题**: 如果 Wan2.6 模型默认仅生成静音视频，那么 `FFmpegSplitter` 尝试提取音频时会失败（已在代码中做 fallback 处理，会得到静音视频）。
*   **建议**: 在首次集成测试时，务必检查生成的 `mp4` 文件是否包含音轨。如果确实没有音频，说明需要查阅 Wan2.6 文档补充音频参数，或接受 Demo 版本为静音。

### 1.2 前端交互体验优化
*   **进度反馈**: `ScriptWorkspace` 目前使用 `setTimeout` 模拟完成状态，这在 Mock 模式下工作良好，但在对接真实后端时可能会掩盖真实的生成进度。建议确保前端能响应后端真实的 `SUCCEEDED` 状态。
*   **交互误导**: 界面上的“替换素材”按钮目前是不可用的（且本项目一期不规划此功能），建议在 Demo 版中隐藏该按钮，以免用户误点。

### 1.3 错误处理不足
*   **模板匹配兜底**: 若创作者输入的意图过于冷门，Template Router 可能找不到匹配模板。建议增加一个通用的“万能叙事模板” (Generic Template) 作为兜底，确保任何输入都能生成视频。

## 2. 测试链路计划 (Testing Strategy)

### 阶段一：Mock 模式全链路验证 (Mock Mode Verification)
*   **目标**: 确保在不消耗 Token 的情况下，所有 UI 流程和后端状态流转正常。
*   **配置**: 确保 `.env` 中 `MOCK_MODE=True`。
*   **测试用例**:
    1.  **生成 (Generate)**: 
        *   输入任意指令。
        *   预期: 立即返回一个包含 4 个分镜的 Mock 视频（健康早餐主题），状态为 `SUCCEEDED`。
    2.  **修改 (Revise)**:
        *   点击 "Revise"，输入任意修改建议。
        *   预期: 创建一个新的 Job，状态立即为 `SUCCEEDED`。IR 中的 `narration_tone` 会变为 `casual_mock` (如果修改了 narration)。
    3.  **高清化 (Finalize)**:
        *   选择分镜点击 "Finalize" (如果 UI 有入口)。
        *   预期: Job 状态更新，视频分辨率元数据更新为 "1920x1080"。

### 阶段二：真实 API 冒烟测试 (Live Smoke Test)
*   **配置**: 确保 `.env` 中 `MOCK_MODE=False`。
*   **简单指令测试**:
    *   输入: "Create a short video about why we get headaches."
    *   验证: 
        *   后端日志显示解析出 Topic="headache"。
        *   最终生成的 Job 状态变更为 `SUCCEEDED`。
        *   **关键验证**: 下载生成的视频文件，播放确认是否有声音。

### 阶段三：演示剧本演练 (Demo Rehearsal)
1.  **黄金用例准备**: 挑选 2 个效果最惊艳的 Case（例如一个“卡通风格的失眠科普”）。
2.  **音频预案**: 如果验证发现生成的视频确实没声音，演示时可以侧重展示“分镜编排”和“视觉生成”能力。

## 3. 开发注意事项
1.  **Mock Mode**: 开发阶段保持开启以节省 Token，但在提交测试或演示前请务必关闭。
2.  **Timeout**: 真实视频生成耗时较长，确保前端请求超时时间设置足够长，或完全依赖轮询机制。
