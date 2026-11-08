import asyncio
import sys
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:                                         
    def __init__(self):
        self.session = None                              
        self.exit_stack = AsyncExitStack()              

    # ---------- Kết nối (bài 8 + bài 9) ----------
    async def connect(self, server_script: str):
        server_params = StdioServerParameters(
            command=sys.executable,                      
            args=[server_script],
            env=None,
        )
        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)                  # khởi động server + nối ống stdin/stdout
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)                   # MiniClient.send() 
        )
        await self.session.initialize()                  # bắt tay với server
        print("✓ Connected to MCP server")

    # ---------- Tools ----------
    async def list_tools(self):
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: dict):
        return await self.session.call_tool(tool_name, arguments)

    # ---------- Resources ----------
    async def list_resources(self):
        result = await self.session.list_resource_templates()
        return result.resourceTemplates

    async def read_resource(self, uri: str):
        return await self.session.read_resource(uri)

    # ---------- Prompts ----------
    async def list_prompts(self):
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, arguments: dict):
        return await self.session.get_prompt(prompt_name, arguments)

    async def run(self):
        print("\n=== MCP Client ===")
        print("Commands: tools | call | resources | read | prompts | prompt | quit")

        while True:
            cmd = input("> ").strip().lower()
            if cmd == "quit":
                break
            try:
                if cmd == "tools":
                    for t in await self.list_tools():
                        print(f"  • {t.name}: {t.description}")

                elif cmd == "call":
                    tool_name = input("  Tool name: ").strip()
                    args = json.loads(input('  Arguments (JSON, e.g. {"text": "hello"}): ').strip())
                    result = await self.call_tool(tool_name, args)
                    for content in result.content:
                        if hasattr(content, "text"):
                            print(f"  Result: {content.text}")

                elif cmd == "resources":
                    resources = await self.list_resources()
                    if resources:
                        for r in resources:
                            print(f"  • {r.name}")
                            print(f"    URI template: {r.uriTemplate}")
                    else:
                        print("  No resources available")

                elif cmd == "read":
                    uri = input("  URI: ").strip()
                    result = await self.read_resource(uri)
                    for content in result.contents:
                        if hasattr(content, "text"):
                            print(f"\n{content.text}")

                elif cmd == "prompts":
                    for p in await self.list_prompts():
                        args_info = ""
                        if p.arguments:
                            arg_names = [arg.name for arg in p.arguments]
                            args_info = f" (args: {', '.join(arg_names)})"
                        print(f"  • {p.name}: {p.description}{args_info}")

                elif cmd == "prompt":
                    prompt_name = input("  Prompt name: ").strip()
                    args = json.loads(input("  Arguments (JSON): ").strip())
                    result = await self.get_prompt(prompt_name, args)
                    print(f"\n--- Prompt: {result.description} ---")
                    for msg in result.messages:
                        text = msg.content.text if hasattr(msg.content, "text") else str(msg.content)
                        print(f"{msg.role}: {text}")

                else:
                    print("  Unknown command")

            except json.JSONDecodeError:
                print("  Error: Invalid JSON format")
            except Exception as e:
                print(f"  Error: {e}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <server_script>")
        sys.exit(1)

    client = MCPClient()
    try:                                                 
        await client.connect(sys.argv[1])
        await client.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())                                  