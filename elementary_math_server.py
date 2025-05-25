from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Elementary Math Operations")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers and return the result.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Sum of a and b
    """
    result = a + b
    print(f"Elementary Math: {a} + {b} = {result}")
    return result


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two integers and return the result.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Product of a and b
    """
    result = a * b
    print(f"Elementary Math: {a} × {b} = {result}")
    return result


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract the second integer from the first and return the result.

    Args:
        a: First integer (minuend)
        b: Second integer (subtrahend)

    Returns:
        Difference of a and b
    """
    result = a - b
    print(f"Elementary Math: {a} - {b} = {result}")
    return result


@mcp.tool()
def divide(a: int, b: int) -> dict:
    """Divide the first integer by the second and return quotient and remainder.

    Args:
        a: Dividend
        b: Divisor (must not be zero)

    Returns:
        Dictionary with quotient and remainder

    Raises:
        ValueError: If divisor is zero
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed")

    quotient = a // b
    remainder = a % b

    print(f"Elementary Math: {a} ÷ {b} = {quotient} remainder {remainder}")

    return {"quotient": quotient, "remainder": remainder, "original_dividend": a, "original_divisor": b}


if __name__ == "__main__":
    print("Starting Elementary Math MCP Server...")
    mcp.run(transport="stdio")
