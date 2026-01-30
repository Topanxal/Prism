# Prism Health AI Agent - 功能说明文档 (Functional Specification)

## 1. 项目概述 (Overview)
本项目是一个专为 **健康科普自媒体工作者 (Health Content Creators)** 打造的 AI 辅助创作 Agent。
它的核心目标是解决创作者在制作专业医疗科普短视频时的痛点：**脚本构思耗时** 和 **专业素材获取困难**。
用户只需输入创作意图（主题、风格、受众等），Agent 即可自动编排专业的分镜脚本，并利用生成式 AI 生成对应的视频素材，极大地缩短从灵感到成片的制作周期。

## 2. 核心功能流程 (Core Workflow)

### 2.1 创作意图解析 (Creative Intent Analysis)
*   **输入**: 创作者输入自然语言的创作指令（例如：“帮我做一个关于力量训练改善失眠的视频，风格要活泼一点，时长 30 秒左右”）。
*   **预处理**:
    *   **PII 脱敏**: 移除输入中的敏感信息。
    *   **语言对齐**: 支持多语言输入，内部统一对齐为英文进行处理。
*   **参数提取 (IR Parsing)**:
    *   利用 LLM (Qwen) 将非结构化的创作指令解析为结构化的 **创作参数 (Intermediate Representation)**。
    *   关键参数包括：
        *   **Topic**: 核心医学/健康主题 (e.g., Insomnia, Strength Training)。
        *   **Style**: 视觉风格偏好 (e.g., Cartoon, Realistic, Bright lighting)。
        *   **Target Audience**: 隐含的目标受众。
        *   **Emotion Curve**: 视频的情绪节奏 (e.g., Anxiety -> Relief)。
        *   **Duration**: 预期的视频时长。

### 2.2 智能脚本编排 (Intelligent Script Orchestration)
*   **专业模板匹配 (Template Routing)**:
    *   系统内置了经过医学专业校验的 **叙事模板库** (e.g., "Myth vs Fact", "Symptom Explainer", "Treatment History")。
    *   基于语义检索 (FAISS) 将用户的创作主题匹配到最合适的叙事结构。
*   **分镜生成 (Shot Planning)**:
    *   结合用户的创作参数和选定的叙事模板，生成具体的 **分镜脚本 (ShotPlan)**。
    *   **内容填充**: 自动生成每一镜的旁白 (`Narration`) 和画面描述 (`Visual Prompt`)。
    *   **导演视角**: 自动规划每一镜的运镜方式 (`Camera Movement`) 和音效氛围。

### 2.3 视频素材生成 (AI Video Generation)
*   **素材合成**:
    *   调用 **Wan2.1 (Wan26)** 文生视频模型，根据分镜脚本中的画面描述，并行生成无版权风险的专业视频素材。
    *   支持 720p/1080p 高清分辨率。
    *   *音频说明*: 当前设计依赖模型直接生成包含音频的视频文件（若模型支持）。若模型仅生成画面，系统将保留静音视频或需后续处理。
*   **粗剪预览**:
    *   利用 FFmpeg 将生成的分镜片段按顺序拼接，生成一个可预览的视频草稿 (Video Draft)。

### 2.4 交互式打磨 (Iterative Revision)
*   **创作者反馈**: 创作者可以像与剪辑师对话一样提出修改意见（如“这一个镜头太暗了，换个明亮的场景”、“旁白太严肃，改轻松点”）。
*   **精准重绘**: Agent 解析反馈，智能定位需要修改的特定分镜或字段（Targeted Fields），触发增量生成，确保修改精准且不破坏整体一致性。

## 3. 系统架构 (System Architecture)

### 前端 (Frontend)
*   **技术栈**: React, TypeScript, Vite, TailwindCSS.
*   **界面**:
    *   `LandingView`: 创作指令输入台。
    *   `ScriptWorkspace`: 脚本可视化工作台（支持查看分镜、修改台词）。
    *   `VideoView`: 视频预览与反馈窗口。

### 后端 (Backend)
*   **技术栈**: Python (FastAPI), SQLAlchemy, FFmpeg.
*   **核心组件**:
    *   `LLMOrchestrator`: 担任“编剧”与“导演”角色。
    *   `TemplateRouter`: 担任“策划”角色，匹配最佳叙事结构。
    *   `Wan26Adapter`: 担任“摄影师”角色，生成视频素材。
    *   `JobManager`: 担任“制片”角色，统筹全流程状态。
    *   **开发辅助**: 内置 `MOCK_MODE`，用于在开发阶段使用本地数据模拟生成过程，节省 API Token。

## 4. 数据流向 (Data Flow)
1.  **Creator Input** (Creative Brief) -> **API** -> **JobManager**
2.  **JobManager** -> **LLM** (Extract Creative Params) -> **Template Router**
3.  **Selected Template** + **Creative Params** -> **LLM** (Write Script) -> **ShotPlan**
4.  **ShotPlan** -> **Wan26 Adapter** (Generate Footage) -> **Raw Clips**
5.  **Raw Clips** -> **FFmpeg** (Assembly) -> **Draft Video**

## 5. 接口定义 (Key API Endpoints)
*   `POST /v1/t2v/generate`: 提交创作指令。
*   `GET /v1/t2v/jobs/{job_id}`: 查询制作进度。
*   `POST /v1/t2v/jobs/{job_id}/revise`: 提交修改反馈。
