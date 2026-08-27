import asyncio

from backend.providers.groq import GroqProvider
from backend.schemas.llm import LLMRequest


async def main():
    provider = GroqProvider()

    request = LLMRequest(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Say hello in one sentence.",
            }
        ],
        temperature=0.2,
        top_p=0.9,
        max_tokens=200,
    )

    response = await provider.generate(request)

    print("PROVIDER:", response.provider)
    print("MODEL:", response.model)
    print("RESPONSE:", response.content)


if __name__ == "__main__":
    asyncio.run(main())
