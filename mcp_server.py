import logging
from fastmcp import FastMCP
from pathlib import Path

logging.getLogger("fastmcp").setLevel(logging.WARNING)   

mcp = FastMCP("lab-server")      # tạo server, đặt tên
BASE_DIR = Path.cwd()            # thư mục đang đứng khi chạy lệnh
OUTPUT_DIR = BASE_DIR / "output" # nơi write_file ghi file ra


@mcp.tool()
def echo(text: str) -> str:
    """Echo back the input text."""
    return f"Echo: {text}"


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file inside the output directory."""
    file_path = (OUTPUT_DIR / path).resolve()
    if not file_path.is_relative_to(OUTPUT_DIR.resolve()):  # chặn "../" thoát ra ngoài output/
        return f"Error: path must stay inside output/: {path}"
    file_path.parent.mkdir(parents=True, exist_ok=True)   # tạo thư mục cha nếu chưa có
    file_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote to output/{path}"


@mcp.resource("file://resources/{filename}")
def read_resource_file(filename: str) -> str:
    """Read a file from the resources directory."""
    file_path = BASE_DIR / "resources" / filename
    if not file_path.exists():
        return f"File not found: {filename}"
    return file_path.read_text(encoding="utf-8")


@mcp.prompt()
def review_file(filename: str) -> str:
    """Generate a prompt to review a file's contents."""
    return f"""Please review the file '{filename}' and provide:
                1. A summary of its contents
                2. Key points or sections
                3. Any suggestions for improvement
                4. Overall quality assessment

                Use the appropriate tools to read the file if needed."""


if __name__ == "__main__":
    mcp.run()        # chạy server, mặc định dùng STDIO