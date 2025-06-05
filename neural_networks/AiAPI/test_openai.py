import asyncio

from environs import Env

from neural_networks.AiAPI import connect_to_openAI





#
#
# client = get_llm_client(api_key=api_key, base_url=base_url)
#
response = client.chat.completions.create(
model="gpt-4.1-nano",
messages=[{"role": "user", "content": "Привет, с какой версией gpt я общаюсь и каково её контекстное окно?"}]
#,stream=True
#,timeout=600
)

print(response.choices[0].message.content)


# async def main() -> None:
#     env = Env()
#     env.read_env()
#     api_key = env.str("OPENAI_API_KEY")
#     base_url = env.str("OPENAI_BASE_URL")
#
#     result = await check_correct_openai_api_key(api_key=api_key, base_url=base_url)
#     print(result)
#
# if __name__ == "__main__":
#     asyncio.run(main())