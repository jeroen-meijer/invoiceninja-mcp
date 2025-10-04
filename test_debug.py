"""Debug test to see exact request details."""

import asyncio
import httpx
import sys
sys.path.insert(0, 'src')

from invoiceninja_mcp.config import settings


async def main():
    """Test with debug output."""
    print("🔍 Debug Information:")
    print(f"   API URL: {settings.api_url}")
    print(f"   API KEY: {settings.api_key[:20]}...{settings.api_key[-10:]}")
    print()

    base_url = settings.api_url.rstrip("/")
    headers = {
        "X-API-Token": settings.api_key,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print("📤 Request headers:")
    for key, value in headers.items():
        if key == "X-API-Token":
            print(f"   {key}: {value[:20]}...{value[-10:]}")
        else:
            print(f"   {key}: {value}")
    print()

    url = f"{base_url}/clients?per_page=5"
    print(f"🔗 Full URL: {url}")
    print()

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            print("📡 Making request...")
            response = await client.get(url, headers=headers)
            print(f"✅ Status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            print(f"📄 Response body: {response.text[:500]}")
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"📥 Response headers: {dict(e.response.headers)}")
            print(f"📄 Response body: {e.response.text}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
