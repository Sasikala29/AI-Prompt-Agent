import asyncio

from groq import AsyncGroq
from backend.core.config import settings


async def main():
    client = AsyncGroq(api_key=settings.groq_api_key)

    response = await client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence.",
            }
        ],
        temperature=0.2,
        max_tokens=50,
    )

    print(response)
    print("\nMESSAGE:")
    print(response.choices[0].message)
    print("\nCONTENT:")
    print(repr(response.choices[0].message.content))


asyncio.run(main())
