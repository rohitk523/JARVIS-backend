"""JARVIS voice agent — LiveKit Agents entrypoint.

This module boots a LiveKit VoiceAssistant that combines:
- VAD   : Silero (local, low-latency)
- STT   : Deepgram Nova-3
- LLM   : Anthropic Claude claude-sonnet-4-6
- TTS   : Cartesia Sonic-2
"""

from __future__ import annotations

import logging

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import anthropic, cartesia, deepgram, silero

from agent.prompts import SYSTEM_PROMPT
from agent.tools import register_tools

logger = logging.getLogger("jarvis.agent")


async def entrypoint(ctx: JobContext) -> None:
    """Called once per LiveKit room session.

    Sets up the voice pipeline and starts the assistant.
    """
    logger.info("Agent joining room %s", ctx.room.name)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # ── Build the function-calling context ────────────────────────────────
    fnc_ctx = llm.FunctionContext()
    register_tools(fnc_ctx)

    # ── Voice pipeline components ─────────────────────────────────────────
    vad = silero.VAD.load()
    stt = deepgram.STT(model="nova-3")
    llm_instance = anthropic.LLM(model="claude-sonnet-4-6")
    tts = cartesia.TTS(
        voice="87748186-23bb-4571-8b6b-d0c9e8a1b8a4",  # "British Lady"
        model="sonic-2",
    )

    # ── Assemble the assistant ────────────────────────────────────────────
    assistant = VoiceAssistant(
        vad=vad,
        stt=stt,
        llm=llm_instance,
        tts=tts,
        fnc_ctx=fnc_ctx,
        chat_ctx=llm.ChatContext().append(role="system", text=SYSTEM_PROMPT),
    )

    assistant.start(ctx.room)
    logger.info("Voice assistant started for room %s", ctx.room.name)

    # Keep alive until the participant leaves
    await assistant.say("Hello. I'm Jarvis, your AI assistant. How can I help you?")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
