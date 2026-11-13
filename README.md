# 企业级 HR 智能客服 Agent 自动化质量评测框架

## 📖 项目简介
本项目针对基于 Coze 平台搭建的【HR 智能客服 Agent】（具备 RAG 知识库、插件调用、多轮记忆功能）构建了一套完整的自动化质量评估框架。旨在解决大模型在业务落地过程中的幻觉、工具调用失败及安全红队注入等核心痛点。

## 🛠️ 技术栈
*   **核心框架**：Python, Pytest, Requests
*   **数据驱动**：JSONL 数据集 (`@pytest.mark.parametrize`)
*   **评估模型**：DeepSeek API (LLM-as-a-Judge 裁判机制)
*   **可视化与资产**：Allure 测试报告、飞书多维表格（用例矩阵 & 缺陷池）

## 🏗️ 架构设计
采用分层解耦设计：
*   `apis/`：封装 Coze 会话接口与异步轮询逻辑。
*   `data/`：存储 28 条 JSONL 格式的核心测试用例。
*   `utils/`：封装 DeepSeek 语义裁判评估器。
*   `tests/`：测试执行层（包含规则断言与工具调用取证）。
*   `reports/`：Allure 测试报告输出目录。

## 🎯 测试维度与覆盖 (共 28 条核心用例)
1.  **应用层 RAG (12条)**：事实忠实度、未召回拒答、边界防幻觉。
2.  **智能体 Agent (8条)**：Function Calling 参数验证、多轮记忆保持与隔离。
3.  **大模型底层 (6条)**：越狱注入防御、系统提示词泄露、乱码鲁棒性。
4.  **AI 综合评价 (2条)**：一致性与有用性。

## 💡 核心亮点
*   **双轨断言机制**：结合传统正则断言与 DeepSeek LLM-as-a-Judge（语义打分），完美解决长文本回答带来的“假阳性”误报问题。
*   **工具调用取证**：通过底层 API 抓包，精准断言 Agent 是否携带正确参数（如 employee_id）调用插件。
*   **优雅降级验证**：验证了 Agent 在插件限流/异常场景下，不产生幻觉并主动引导联系人工的兜底能力。

## 🚀 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 配置环境变量：参考 `.env.example` 配置 `.env`。
3. 执行测试并生成报告：
   ```bash
   pytest tests/ -v --alluredir=./reports
   allure serve ./reports