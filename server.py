# server.py
import os
import requests
from fastmcp import FastMCP
from dhanhq import dhanhq

mcp = FastMCP(name="DhanHQ MCP Server")

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

if not client_id or not access_token:
    raise EnvironmentError("[ERROR] Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN environment variables")

@mcp.tool()
def get_holdings_summary() -> dict:
    """
    Fetch holdings summary via DhanHQ SDK.
    """

    client = dhanhq(client_id, access_token)
    holdings = client.get_holdings()
    # maybe reduce fields
    return {"holdings": holdings}

@mcp.tool()
def get_all_orders() -> dict:
    """
    Fetch all orders from DhanHQ account.
    Returns a list of all orders with their details including order ID, status, quantity, price, etc.
    """
    client = dhanhq(client_id, access_token)
    orders = client.get_order_list()
    return {"orders": orders}

@mcp.tool()
def renew_access_token() -> dict:
    """
    Renew the DhanHQ access token for another 24 hours.
    This expires the current token and provides a new token with 24 hours validity.
    Note: Only works with tokens generated from Dhan Web (web.dhan.co).
    Returns the new access token that should be updated in your environment variables.
    """
    url = "https://api.dhan.co/v2/RenewToken"
    headers = {
        "access-token": access_token,
        "dhanClientId": client_id
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        # The response should contain the new token
        result = response.json()

        return {
            "status": "success",
            "message": "Token renewed successfully. Update your DHAN_ACCESS_TOKEN environment variable with the new token.",
            "new_token": result.get("data", {}).get("token") if "data" in result else result.get("token"),
            "expires_in": "24 hours"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Failed to renew token: {str(e)}",
            "error_details": str(e)
        }

def main():
    """Main entry point for the MCP server."""
    print("[INFO] Using environment credentials")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
