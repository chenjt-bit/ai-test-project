import json
import pytest
import allure
from apis.coze_client import chat_with_agent
from utils.llm_judge import llm_as_judge


def load_cases():
    cases = []
    with open("data/hr_agent_cases.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["case_id"])
def test_hr_agent_case(case, coze_config):
    case_id = case["case_id"]
    answer = ""
    tool_calls = []

    with allure.step(f"1. 执行用例 {case_id}"):
        try:
            if case["conversation_mode"] == "single":
                answer, _, tool_calls = chat_with_agent(coze_config, case["query"])
            elif case["conversation_mode"] == "multi":
                conversation_id = None
                for turn in case["turns"]:
                    answer, conversation_id, tool_calls = chat_with_agent(coze_config, turn, conversation_id)
        except TimeoutError:
            pytest.skip(f"[{case_id}] 触发平台安全拦截或超时")
            return

        allure.attach(
            json.dumps({"query": case.get("query", case.get("turns")), "answer": answer}, ensure_ascii=False, indent=2),
            name="AI 交互日志", attachment_type=allure.attachment_type.JSON
        )

    with allure.step("2. 传统规则断言校验"):
        if "expected_contains" in case:
            for keyword in case["expected_contains"]:
                assert keyword in answer, f"❌ 未包含 '{keyword}'"
        if "expected_not_contains" in case:
            for keyword in case["expected_not_contains"]:
                assert keyword not in answer, f"❌ 泄露敏感词 '{keyword}'"

    with allure.step("3. Agent 工具调用行为断言"):
        if "check_tool_call" in case:
            tool_calls_str = json.dumps(tool_calls, ensure_ascii=False)
            assert len(tool_calls) > 0, "❌ 预期应调用插件，实际未调用！"
            assert case["check_tool_call"] in tool_calls_str, f"❌ 参数错误，未找到工号 {case['check_tool_call']}！"

        if case.get("check_no_tool_call"):
            assert len(tool_calls) == 0, "❌ 失败：前置条件不满足，不应调用插件！"

    with allure.step("4. DeepSeek 大模型裁判 (LLM-as-a-Judge)"):
        if "judge_criteria" in case:
            judge_result = llm_as_judge(
                query=case.get("query", str(case.get("turns"))),
                answer=answer,
                criteria=case["judge_criteria"]
            )

            allure.attach(
                json.dumps(judge_result, ensure_ascii=False, indent=2),
                name="DeepSeek 裁判报告",
                attachment_type=allure.attachment_type.JSON
            )

            assert judge_result.get("passed") is True, f"❌ DeepSeek 裁判判定失败: {judge_result.get('reason')}"