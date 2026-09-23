import asyncio
import websockets
import json

async def test_bridge():
    uri = "ws://localhost:8000/ws/officekit"
    async with websockets.connect(uri) as websocket:
        payload = {"ocr_text": "Amoxicillin 500mg - Take 1 tablet twice daily after meals for 5 days."}
        print("[>] Sending test prescription to server...")
        await websocket.send(json.dumps(payload))
        
        response = await websocket.recv()
        print("\n[<] AI Response from Local Llama 3.2:")
        print(response)

asyncio.run(test_bridge())