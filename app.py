import asyncio
import os
import sys
from loguru import logger
from dotenv import load_dotenv

from pipecat.frames.frames import TextFrame, StartFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.services.openai_realtime_beta.openai import OpenAIRealtimeBetaLLMService
from pipecat.services.openai_realtime_beta.events import SessionProperties

# Configure logging
logger.remove(0)
logger.add(sys.stderr, level="INFO")

# Load environment variables
load_dotenv(override=True)

async def configure_daily():
    """Set up Daily room and token - in a real app, use Daily REST API for this"""
    # Use environment variables or provide directly
    room_url = os.getenv("DAILY_ROOM_URL")
    token = os.getenv("DAILY_TOKEN", "")  # leave empty if not using token
    
    if not room_url:
        raise ValueError("No Daily room URL provided. Set DAILY_ROOM_URL environment variable.")
    
    return (room_url, token)

async def main():
    # Configure Daily room and token
    (room_url, token) = await configure_daily()
    
    # Configure Daily transport
    transport = DailyTransport(
        room_url=room_url,
        token=token,
        bot_name="AI Voice Assistant",
        params=DailyParams(
            audio_in_enabled=True,  # Allow audio input from users
            audio_out_enabled=True,  # Allow audio output to users
            microphone_out_enabled=True,  # Enable microphone for output
            camera_out_enabled=False,  # Disable camera (audio-only)
        )
    )
    
    # Configure OpenAI Realtime service
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
    
    openai_realtime = OpenAIRealtimeBetaLLMService(
        api_key=openai_api_key,
        model="gpt-4o-realtime-preview-2024-12-17",  # Use the latest realtime model
        session_properties=SessionProperties(
            instructions="You are a helpful voice assistant in a group call. Anyone can speak to you, and your responses will be heard by everyone. Keep your responses concise and clear.",
            turn_detection=None  # Use OpenAI's built-in turn detection
        )
    )
    
    # Create pipeline connecting Daily transport with OpenAI Realtime
    pipeline = Pipeline([
        transport.input(),  # Audio from all users in the room
        openai_realtime,    # Process with OpenAI Realtime
        transport.output()  # Output responses to all users in the room
    ])
    
    # Create and configure pipeline task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=24000,  # Match OpenAI's preferred sample rate
            audio_out_sample_rate=24000,
            allow_interruptions=True,
            enable_metrics=True
        )
    )
    
    # Set up event handlers for participant management
    
    # Handle when the first participant joins
    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        participant_name = participant.get("info", {}).get("userName", "New user")
        logger.info(f"First participant joined: {participant_name}")
        await task.queue_frame(TextFrame(f"Hello {participant_name}! Welcome to the voice assistant room. Feel free to ask me anything."))
    
    # Handle when additional participants join
    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        # Skip if this is the first participant (already handled)
        if transport.participant_counts().get("present", 0) > 1:
            participant_name = participant.get("info", {}).get("userName", "New user")
            logger.info(f"Participant joined: {participant_name}")
            await task.queue_frame(TextFrame(f"{participant_name} has joined the room."))
    
    # Handle when participants leave
    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        participant_name = participant.get("info", {}).get("userName", "A user")
        logger.info(f"Participant left: {participant_name}")
        
        # Only shut down when all participants have left
        if transport.participant_counts().get("present", 0) == 0:
            logger.info("All participants have left. Shutting down...")
            await task.cancel()
        else:
            await task.queue_frame(TextFrame(f"{participant_name} has left the room."))
    
    # Create pipeline runner and run the task
    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main()) 