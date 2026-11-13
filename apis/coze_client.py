# apis/coze_client.py
import requests
import time


def chat_with_agent(config, query, conversation_id=None):
    """发送对话请求，返回完整的 answer 和 tool_calls"""
    url = f"{config['base_url']}/v3/chat"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "Content-Type": "application/json"
    }
    payload = {
        "bot_id": config["bot_id"],
        "user_id": "pytest_architect",
        "stream": False,
        "auto_save_history": True,
        "additional_messages": [{"role": "user", "content": query, "content_type": "text"}]
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    # 发起对话
    resp = requests.post(url, headers=headers, json=payload,timeout=10).json()
    if resp.get("code") != 0:
        raise Exception(f"API调用失败: {resp}")

    c_id = resp["data"]["conversation_id"]
    chat_id = resp["data"]["id"]

    # 轮询状态（最多等 60 秒）
    retrieve_url = f"{config['base_url']}/v3/chat/retrieve?conversation_id={c_id}&chat_id={chat_id}"
    for _ in range(120):
        r = requests.get(retrieve_url, headers=headers,timeout=10).json()
        if r.get("code") != 0:
            raise Exception(f"轮询失败: {r}")

        status = r.get("data", {}).get("status")
        if status == "completed":
            break
        elif status == "failed":
            raise Exception(f"对话异常: {r.get('data', {}).get('last_error')}")
        time.sleep(1)
    else:
        raise TimeoutError("轮询超时（60秒）")

    # 拉取消息列表
    msg_url = f"{config['base_url']}/v3/chat/message/list?conversation_id={c_id}&chat_id={chat_id}"
    msgs = requests.get(msg_url, headers=headers,timeout=10).json()

    answer = ""
    tool_calls = []
    for msg in msgs.get("data", []):
        if msg["role"] == "assistant":
            if msg["type"] == "answer":
                answer = msg["content"]
            elif msg["type"] in ["tool_request", "tool_response"]:
                tool_calls.append(msg)

    return answer, c_id, tool_calls