import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from browser_use import Agent

llm = ChatOpenAI(model='openai', base_url='https://text.pollinations.ai/openai', api_key='/')


async def run_search():
	agent = Agent(
		task=(
			'Go to url r/LocalLLaMA subreddit and search for "browser use" in the search bar and click on the first post and find the funniest comment'
		),
		llm=llm,
		max_actions_per_step=4,
	)

	await agent.run(max_steps=25)


if __name__ == '__main__':
	asyncio.run(run_search())