import asyncio
import json
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import requests
import websockets


SOCKET_IO_URL = (
    "wss://www.livepriceofgold.com/sio/p7012/socket.io/"
    "?EIO=4&transport=websocket"
)
GOLD_PRICE_API_URL = (
    "https://sambathreasmey1app.pythonanywhere.com/api/gold/price/github"
)
PRICE_PRECISION = Decimal("0.000001")
TROY_OUNCE_TO_DAMLUNG = Decimal("1.2")


def _decode_update_packet(response):
    if isinstance(response, bytes):
        response = response.decode("utf-8", errors="replace")
    if not isinstance(response, str) or not response.startswith("42"):
        return None

    try:
        packet = json.loads(response[2:])
    except json.JSONDecodeError:
        return None
    if not isinstance(packet, list) or len(packet) < 2 or packet[0] != "update":
        return None

    payload = packet[1]
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    return payload if isinstance(payload, dict) else None


def _price_per_damlung(ounce_price):
    try:
        parsed_price = Decimal(str(ounce_price))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("XAUUSD must be a positive number")
    if not parsed_price.is_finite() or parsed_price <= 0:
        raise ValueError("XAUUSD must be a positive number")
    return (parsed_price * TROY_OUNCE_TO_DAMLUNG).quantize(
        PRICE_PRECISION,
        rounding=ROUND_HALF_UP,
    )


async def fetch_price_per_damlung():
    async with websockets.connect(
        SOCKET_IO_URL,
        open_timeout=10,
        close_timeout=5,
        ping_interval=20,
        ping_timeout=20,
    ) as websocket:
        handshake = await websocket.recv()
        if isinstance(handshake, bytes):
            handshake = handshake.decode("utf-8", errors="replace")
        if not isinstance(handshake, str) or not handshake.startswith("0"):
            raise RuntimeError("Unexpected Socket.IO handshake response")
        await websocket.send("40")

        while True:
            response = await websocket.recv()
            if response == "2":
                await websocket.send("3")
                continue

            data = _decode_update_packet(response)
            if data is None or "XAUUSD" not in data:
                continue

            try:
                return _price_per_damlung(data["XAUUSD"])
            except ValueError:
                continue


def update_backend_price(price_per_damlung, api_key):
    response = requests.post(
        GOLD_PRICE_API_URL,
        json={"price_per_damlung": str(price_per_damlung)},
        headers={"X-Gold-Update-Key": api_key},
        timeout=(5, 15),
    )
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict) or result.get("code") != 0:
        raise RuntimeError("Gold price API returned an unsuccessful response")

    data = result.get("data") or {}
    if not isinstance(data, dict):
        raise RuntimeError("Gold price API returned an invalid response")
    if data.get("updated") is False:
        print("Gold price update skipped: GitHub Action updates are disabled in Admin settings.")
        return
    price = (data.get("price") or {}).get("price_per_damlung")
    if not price:
        raise RuntimeError("Gold price API response did not include the updated price")
    print(f"Gold price updated to ${price} per damlung.")
    if data.get("triggered_alerts"):
        print(f"Triggered {data['triggered_alerts']} user price alert(s).")
    if data.get("notification_failures"):
        print(f"Failed to deliver {data['notification_failures']} user price alert(s).")


async def main():
    api_key = os.getenv("GOLD_PRICE_UPDATE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GOLD_PRICE_UPDATE_API_KEY GitHub secret is not configured")

    price_per_damlung = await asyncio.wait_for(fetch_price_per_damlung(), timeout=45)
    update_backend_price(price_per_damlung, api_key)


if __name__ == "__main__":
    asyncio.run(main())
