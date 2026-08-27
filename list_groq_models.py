
import asyncio

from groq import AsyncGroq

from backend.core.config import settings


async def main():
    client = AsyncGroq(api_key=settings.groq_api_key)

    models = await client.models.list()

    print("AVAILABLE GROQ MODELS:")
    for model in models.data:
        print(model.id)


if __name__ == "__main__":
    asyncio.run(main())

