# xiaohongshu-mcp-no-login：不用登录的小红书 MCP

让 Claude Code、Codex、Cursor 这些 AI 工具直接搜小红书笔记、读全文和评论、查博主。**不用登录小红书，不用扫码，不用 Cookie，不开浏览器**，你自己的账号不参与，也就不用担心它被风控或警告。

一个文件，不用装依赖，Python 3.9 以上就能跑。这是非官方项目，只读，不能发笔记。

## 30 秒接上

先[注册](https://dataxapi.com/zh/signin/?button=gh-xiaohongshu-mcp-no-login)领一个 DataXAPI 的 Key（可免费试用，最多 333 次），然后：

```bash
git clone https://github.com/data-x-api/xiaohongshu-mcp-no-login
cd xiaohongshu-mcp-no-login
```

**Claude Code：**

```bash
claude mcp add xiaohongshu -e DATAXAPI_API_KEY=dx_... -- python3 "$PWD/server.py"
```

**Codex**（`~/.codex/config.toml`）：

```toml
[mcp_servers.xiaohongshu]
command = "python3"
args = ["/完整路径/server.py"]
env = { DATAXAPI_API_KEY = "dx_..." }
```

**Cursor**（`~/.cursor/mcp.json`），其他支持 MCP 的客户端写法也差不多：

```json
{
  "mcpServers": {
    "xiaohongshu": {
      "command": "python3",
      "args": ["/完整路径/server.py"],
      "env": { "DATAXAPI_API_KEY": "dx_..." }
    }
  }
}
```

接上后直接问它：

```text
搜小红书上最近关于露营装备的笔记，挑点赞最高的 3 篇读全文和评论，总结大家在抱怨什么。
```

## 有哪些工具

| 工具 | 做什么 | 每次 |
|---|---|---|
| `search_notes` | 按关键词搜笔记，可按相关、最新、最热排序 | $0.02 |
| `get_note` | 读一篇笔记的全文、图片、话题和互动数 | $0.02 |
| `get_note_comments` | 读一篇笔记的评论 | $0.02 |
| `search_users` | 找博主 | $0.02 |
| `get_user` | 读博主的简介、粉丝数、关注数和笔记数 | $0.02 |
| `get_user_notes` | 列出博主发过的笔记 | $0.02 |

失败不扣费。笔记和博主都可以直接贴浏览器里的链接、App 复制的分享文字或 xhslink 短链。

## 一次真实运行

2026-11-05（北京时间），用 MCP 官方的 Python 客户端把 6 个工具各调一次：

| 工具 | 结果 | 扣费 |
|---|---|---|
| `search_notes`（咖啡，最热） | 20 条，有下一页 | $0.02 |
| `get_note` | 全文、图片和互动数（点赞 112,708，收藏 23,418，评论 803） | $0.02 |
| `get_note_comments` | 10 条，有下一页 | $0.02 |
| `search_users`（Nike） | 20 个，有下一页 | $0.02 |
| `get_user` | 简介和粉丝数 | $0.02 |
| `get_user_notes` | 22 条，有下一页 | $0.02 |

也在 Claude Code 里真实调用过一次 `search_notes`。Codex 和 Cursor 的写法是照 MCP 的标准配置写的，这次没有逐个试。

## 不想留一个文件在本地

可以直接连 DataXAPI 的远程 MCP：`https://api.dataxapi.com/mcp`。它除了小红书，还能查抖音、微信和其他平台，接法见 [dataxapi.com/zh/mcp](https://dataxapi.com/zh/mcp/)。

## 说明

- 这是 [DataXAPI](https://dataxapi.com/zh/) 的示例项目，不是小红书的官方项目。文件里只有调用接口的代码，没有爬虫。接口说明见[小红书笔记搜索](https://dataxapi.com/zh/apis/xiaohongshu/notes/search/)。
- 只读公开内容，请遵守法律和平台规则，不要用于骚扰他人或收集个人信息。
- 问题和建议提 issue，或写信到 support@dataxapi.com。MIT 许可证。

## English

A Xiaohongshu (RedNote) MCP server that needs no login: no account, no QR code, no cookies, no browser. Six read-only tools let Claude Code, Codex, Cursor and other MCP clients search notes, read full text and comments, and look up creators, at $0.02 a call with failed calls free. One Python 3.9+ file with no dependencies. Needs a [DataXAPI key](https://dataxapi.com/signin/?button=gh-xiaohongshu-mcp-no-login) in `DATAXAPI_API_KEY`. Unofficial.
