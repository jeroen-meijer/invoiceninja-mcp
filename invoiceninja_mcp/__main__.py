import argparse
import asyncio
from fastmcp.tools.tool_transform import ToolTransformConfig
from .server import mcp


async def apply_prefix(prefix: str) -> None:
    tools = await mcp.get_tools()
    for tool_name in tools:
        mcp.add_tool_transformation(tool_name, ToolTransformConfig(name=prefix + tool_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InvoiceNinja MCP Server")
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="Prefix to prepend to all tool names (e.g. --prefix=flint → flint_list_invoices)",
    )
    args, _ = parser.parse_known_args()

    if args.prefix:
        prefix = args.prefix.rstrip("_") + "_"
        asyncio.run(apply_prefix(prefix))

    mcp.run()
