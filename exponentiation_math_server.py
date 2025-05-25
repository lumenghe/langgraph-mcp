from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Advanced Math Operations")


@mcp.tool()
def power(base: int, exponent: int) -> int:
    """Calculate base raised to the power of exponent.

    Args:
        base: The base number
        exponent: The exponent (power)

    Returns:
        Result of base^exponent
    """
    if exponent < 0:
        raise ValueError("Negative exponents not supported for integer results")

    result = base**exponent
    print(f"Advanced Math: {base}^{exponent} = {result}")
    return result


@mcp.tool()
def square(number: int) -> int:
    """Calculate the square of a number.

    Args:
        number: The number to square

    Returns:
        Square of the input number
    """
    result = number**2
    print(f"Advanced Math: {number}² = {result}")
    return result


@mcp.tool()
def cube(number: int) -> int:
    """Calculate the cube of a number.

    Args:
        number: The number to cube

    Returns:
        Cube of the input number
    """
    result = number**3
    print(f"Advanced Math: {number}³ = {result}")
    return result


@mcp.tool()
def square_root(number: int) -> float:
    """Calculate the square root of a number.

    Args:
        number: The number to find square root of (must be non-negative)

    Returns:
        Square root of the input number

    Raises:
        ValueError: If number is negative
    """
    if number < 0:
        raise ValueError("Square root of negative numbers not supported")

    result = number**0.5
    print(f"Advanced Math: √{number} = {result}")
    return result


if __name__ == "__main__":
    print("Starting Advanced Math MCP Server...")
    mcp.run(transport="stdio")
