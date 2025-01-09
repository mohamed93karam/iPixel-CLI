import json
import asyncio
import websockets
from websockets.server import serve
from bleak import BleakClient

from mledcontrol import *

COMMANDS = {
    "clear": clear,
    "set_brightness": set_brightness,
    
    "set_clock_mode": set_clock_mode,
    "set_fun_mode": set_fun_mode,
    
    "delete_screen": delete_screen,
    
    "set_text": send_text,
    "set_animation": send_animation,
}

# Socket server
async def handle_websocket(websocket, path):
    async with BleakClient(address) as client:      # Connection established here
        print("[INFO] Connected to the device")
        try:
            while True:
                # Wait for a message from the client
                message = await websocket.recv()

                # Parse JSON
                try:
                    command_data = json.loads(message)
                    command_name = command_data.get("command")
                    parameter = command_data.get("parameter")

                    if command_name in COMMANDS:
                        # generate the data to send
                        data = COMMANDS[command_name](parameter)

                        # Send the data to the device
                        await client.write_gatt_char(
                            "0000fa02-0000-1000-8000-00805f9b34fb", data
                        )

                        # Prepare the response
                        response = {"status": "success", "command": command_name}
                    else:
                        response = {"status": "error", "message": "Commande inconnue"}
                except Exception as e:
                    response = {"status": "error", "message": str(e)}

                # Send the response to the client
                await websocket.send(json.dumps(response))
        except websockets.ConnectionClosed:
            print("[INFO] Websocket connection has been closed")

PORT = 4444
IP = "localhost"

# Start the server
if __name__ == "__main__":
    start_server = serve(handle_websocket, IP, PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    print("WebSocket server started on ws://" + IP + ":" + str(PORT))
    asyncio.get_event_loop().run_forever()
