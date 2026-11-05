#!/usr/bin/env python3
"""小红书 MCP：让 AI 读小红书的笔记、评论和博主。不用登录，不用扫码，不用 Cookie，不开浏览器。

这是一个标准输入输出（stdio）的 MCP 服务，由 Claude Code、Codex、Cursor 这类客户端启动。
Python 3.9+，只用标准库。Key 放在环境变量 DATAXAPI_API_KEY。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.dataxapi.com/v1/"
SOURCE = "gh-xiaohongshu-mcp-no-login"
SIGN_UP = f"https://dataxapi.com/zh/signin/?button={SOURCE}"
VERSION = "0.1.0"
PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

TARGET = {"type": "string", "description": "完整链接、小红书 App 复制的分享文字或 xhslink 短链，或 24 位编号"}
QUERY = {"type": "string", "description": "搜索词"}
CURSOR = {"type": "string", "description": "翻页用：上一次返回的 next_cursor，原样传回"}

# 工具名 → (接口, 说明, 参数, 必填)
TOOLS = {
    "search_notes": (
        "xiaohongshu.notes.search",
        "按关键词搜小红书笔记，返回标题、摘要、作者、点赞收藏评论数和链接。一页最多 20 条，每次 $0.02。",
        {"query": QUERY, "sort": {"type": "string", "enum": ["relevance", "latest", "popular"], "description": "排序：相关、最新、最热"}, "cursor": CURSOR},
        ["query"],
    ),
    "get_note": (
        "xiaohongshu.notes.get",
        "读一篇小红书笔记的全文、图片、话题和互动数。每次 $0.02。",
        {"target": TARGET},
        ["target"],
    ),
    "get_note_comments": (
        "xiaohongshu.notes.comments.list",
        "读一篇小红书笔记的评论，每次一页，$0.02。",
        {"target": TARGET, "cursor": CURSOR},
        ["target"],
    ),
    "search_users": (
        "xiaohongshu.users.search",
        "按名字或关键词找小红书博主，返回编号、名字和主页链接。每次 $0.02。",
        {"query": QUERY, "cursor": CURSOR},
        ["query"],
    ),
    "get_user": (
        "xiaohongshu.users.get",
        "读小红书博主的简介、粉丝数、关注数和笔记数。每次 $0.02。",
        {"target": TARGET},
        ["target"],
    ),
    "get_user_notes": (
        "xiaohongshu.users.notes.list",
        "列出小红书博主发过的笔记，从新到旧，每次一页，$0.02。",
        {"target": TARGET, "cursor": CURSOR},
        ["target"],
    ),
}


def call_api(capability: str, arguments: dict) -> dict:
    key = os.environ.get("DATAXAPI_API_KEY")
    if not key:
        raise RuntimeError(f"缺 DATAXAPI_API_KEY。到这里注册领 Key，可免费试用：{SIGN_UP}")
    params = {name: value for name, value in arguments.items() if name != "target" and value}
    target = str(arguments.get("target") or "").strip()
    if target:
        params["id" if re.fullmatch(r"[0-9a-fA-F]{24}", target) else "url"] = target
    request = Request(
        API + capability.replace(".", "/") + "?" + urlencode({**params, "view": "standard" if capability.endswith("notes.get") else "compact"}),
        headers={"Authorization": f"Bearer {key}", "X-Source": SOURCE, "User-Agent": SOURCE},
    )
    for last in (False, True):
        try:
            with urlopen(request, timeout=120) as response:
                return json.load(response)
        except HTTPError as error:
            if not last and error.code in (429, 500, 502, 503, 504):
                time.sleep(3)  # 失败不扣费，重试一次
                continue
            try:
                message = json.load(error).get("message_zh")
            except ValueError:
                message = None
            raise RuntimeError(message or f"HTTP {error.code}") from error
        except OSError as error:
            raise RuntimeError(f"连不上接口：{error}") from error
    raise AssertionError


def call_tool(name: str, arguments: dict) -> dict:
    if name not in TOOLS:
        return {"content": [{"type": "text", "text": f"没有这个工具：{name}"}], "isError": True}
    capability = TOOLS[name][0]
    try:
        answer = call_api(capability, arguments)
    except RuntimeError as error:
        return {"content": [{"type": "text", "text": f"{error}（这次没有扣费）"}], "isError": True}
    result = {
        "data": answer.get("data"),
        "next_cursor": (answer.get("page") or {}).get("next_cursor"),
        "charged_usd": (answer.get("meta") or {}).get("billing", {}).get("amount"),
    }
    return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}


def handle(message: dict) -> dict | None:
    method, rid = message.get("method"), message.get("id")
    if rid is None:
        return None  # 通知，不用回
    if method == "initialize":
        asked = (message.get("params") or {}).get("protocolVersion")
        result = {
            "protocolVersion": asked if asked in PROTOCOLS else PROTOCOLS[0],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "xiaohongshu-mcp-no-login", "version": VERSION},
            "instructions": "读小红书的公开笔记、评论和博主，不需要登录。每次工具调用都会按说明里的价格扣费，失败不扣费。",
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {
            "tools": [
                {"name": name, "description": doc, "inputSchema": {"type": "object", "properties": props, "required": need}}
                for name, (_, doc, props, need) in TOOLS.items()
            ]
        }
    elif method == "tools/call":
        params = message.get("params") or {}
        result = call_tool(params.get("name"), params.get("arguments") or {})
    else:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"不支持：{method}"}}
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def main() -> None:
    for line in sys.stdin.buffer:
        if not line.strip():
            continue
        try:
            reply = handle(json.loads(line))
        except ValueError:
            reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "不是合法的 JSON"}}
        if reply is not None:
            sys.stdout.buffer.write(json.dumps(reply, ensure_ascii=False).encode("utf-8") + b"\n")
            sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
