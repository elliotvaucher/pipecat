#!/usr/bin/env python

import os
import argparse
import asyncio
import aiohttp
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv(override=True)

async def create_daily_room(session, api_key, room_name=None):
    """Create a new Daily room with appropriate properties for our voice assistant."""
    url = "https://api.daily.co/v1/rooms"
    
    # Generate a room name if not provided
    if not room_name:
        room_name = f"voice-assistant-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Configure room properties
    room_properties = {
        "name": room_name,
        "properties": {
            "enable_chat": True,
            "enable_knocking": False,
            "enable_screenshare": False,
            "enable_recording": "cloud",
            "start_video_off": True,  # Start with video off
            "start_audio_off": False, # Start with audio on
            "exp": int((datetime.now() + timedelta(days=1)).timestamp()),  # 24-hour expiration
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    async with session.post(url, json=room_properties, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            error_text = await response.text()
            raise Exception(f"Failed to create room: {response.status} {error_text}")

async def create_room_token(session, api_key, room_name):
    """Create a token for the specified room."""
    url = f"https://api.daily.co/v1/meeting-tokens"
    
    # Configure token properties
    token_properties = {
        "properties": {
            "room_name": room_name,
            "is_owner": True,
            "exp": int((datetime.now() + timedelta(days=1)).timestamp()),  # 24-hour expiration
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    async with session.post(url, json=token_properties, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return data.get("token")
        else:
            error_text = await response.text()
            raise Exception(f"Failed to create token: {response.status} {error_text}")

async def main():
    parser = argparse.ArgumentParser(description="Create a Daily room for voice assistant")
    parser.add_argument("--room-name", type=str, help="Name for the Daily room")
    args = parser.parse_args()
    
    api_key = os.getenv("DAILY_API_KEY")
    if not api_key:
        print("Error: DAILY_API_KEY environment variable is not set")
        return 1
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create room
            room_data = await create_daily_room(session, api_key, args.room_name)
            room_name = room_data.get("name")
            room_url = room_data.get("url")
            
            # Create token
            token = await create_room_token(session, api_key, room_name)
            
            # Display information
            print(f"\nRoom created successfully:")
            print(f"Room Name: {room_name}")
            print(f"Room URL: {room_url}")
            print(f"Token: {token}")
            print(f"\nTo start the voice assistant, run:")
            print(f"DAILY_ROOM_URL={room_url} DAILY_TOKEN={token} python app.py")
            print(f"\nTo connect to the room from a web browser, open client.html and enter the room URL.")
            
        except Exception as e:
            print(f"Error: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 