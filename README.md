# Multi-User Voice Assistant with Pipecat

This project builds a multi-user voice assistant application that uses:
- **[Pipecat](https://github.com/daily-co/pipecat)** for the audio/voice pipeline
- **Daily WebRTC** for multi-user rooms
- **OpenAI realtime API** for the AI voice assistant

## Features

- Users connect to a shared voice room
- AI assistant processes audio from all users
- AI responses are broadcast to all users
- New users can join existing rooms
- All users in the same room hear the AI responses

## Setup

### Prerequisites

- Python 3.10 or higher
- A [Daily](https://www.daily.co/) account (for WebRTC rooms)
- An [OpenAI](https://platform.openai.com/) API key with access to realtime API models

### Installation

1. Clone this repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   # Daily.co configuration
   DAILY_API_KEY=your_daily_api_key
   
   # OpenAI API configuration
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### 1. Create a Daily Room

Use the provided script to create a Daily room:

```bash
python create_daily_room.py
```

This will output:
- A Daily room URL
- A room token
- A command to start the voice assistant

### 2. Start the AI Voice Assistant

Run the app using the command from the previous step, or manually:

```bash
DAILY_ROOM_URL=your_room_url DAILY_TOKEN=your_token python app.py
```

The AI assistant will join the room and be ready for conversation.

### 3. Connect Users to the Room

Open `client.html` in a web browser and:
1. Enter the Daily room URL
2. Enter your name
3. Click "Join Room"

Multiple users can connect to the same room from different devices/browsers.

## How It Works

1. **Daily WebRTC**: Handles multi-user room creation and management
2. **OpenAI Realtime API**: Processes audio in real-time for natural conversations
3. **Pipecat Pipeline**: Connects these components for seamless voice interactions:
   - Input: Audio from all users in the room
   - Processing: OpenAI realtime model handles conversations
   - Output: AI responses are broadcast to all users

## License

This project uses the same license as Pipecat (BSD 2-Clause).
