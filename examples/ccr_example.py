"""Example: Using claude-code-router (ccr) with its default config directory.

This example demonstrates how to use the Claude Agent SDK with ccr,
allowing you to route requests to custom models (DeepSeek, Gemini, etc.)
through ccr's configuration.

Prerequisites:
1. Install ccr: npm install -g @musistudio/claude-code-router
2. Install claude CLI: npm install -g @anthropic-ai/claude-code
3. Configure your ccr config.json (see ../ccr-config/config.json for an example)
4. Set environment variables for API keys (OPENROUTER_API_KEY, DEEPSEEK_API_KEY, etc.)

Usage:
    python examples/ccr_example.py
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock, ResultMessage


# ccr always looks in ~/.claude-code-router by default
CCR_HOME_DIR = Path.home() / ".claude-code-router"
SAMPLE_CONFIG = Path(__file__).parent.parent.parent / "ccr-config" / "config.json"


async def basic_query_example():
    """Basic example using ccr with custom config directory."""
    print("=== Basic Query Example ===\n")

    options = ClaudeAgentOptions(
        use_ccr=True,  # Enable ccr mode
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is 2 + 2? Answer briefly.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Response: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"\nSession ID: {message.session_id}")
                if message.total_cost_usd:
                    print(f"Cost: ${message.total_cost_usd:.6f}")


async def conversation_example():
    """Multi-turn conversation example using ccr."""
    print("\n=== Conversation Example ===\n")

    options = ClaudeAgentOptions(
        use_ccr=True,
    )

    async with ClaudeSDKClient(options=options) as client:
        # First turn
        await client.query("Remember this number: 42")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Turn 1: {block.text[:100]}...")

        # Second turn - ccr maintains conversation context
        await client.query("What number did I ask you to remember?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Turn 2: {block.text}")


async def with_tools_example():
    """Example using ccr with tools enabled."""
    print("\n=== Tools Example ===\n")

    options = ClaudeAgentOptions(
        use_ccr=True,
        allowed_tools=["Bash", "Read"],  # Allow specific tools
        permission_mode="acceptEdits",  # Auto-accept tool usage
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("What is the current directory? Use bash to find out.")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Response: {block.text}")


async def main():
    """Run all examples."""
    print(f"Using ccr config from: {CCR_HOME_DIR}\n")

    # Check if config exists in the default location
    config_file = CCR_HOME_DIR / "config.json"
    if not config_file.exists():
        print(f"Warning: Config file not found at {config_file}")
        if SAMPLE_CONFIG.exists():
            print(f"Copy the sample: cp {SAMPLE_CONFIG} {config_file}")
        else:
            print("Please create the config file first.")
        return

    try:
        await basic_query_example()
        await conversation_example()
        await with_tools_example()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. ccr is installed: npm install -g @musistudio/claude-code-router")
        print("2. claude CLI is installed: npm install -g @anthropic-ai/claude-code")
        print("3. API keys are set in environment variables")


if __name__ == "__main__":
    asyncio.run(main())
