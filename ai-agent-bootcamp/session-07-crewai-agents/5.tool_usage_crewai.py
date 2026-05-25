from crewai_tools import ScrapeWebsiteTool
from crewai import Agent, Task, Crew
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
os.environ['OPENAI_API_KEY'] = api_key

# Scrape the Wikipedia page directly
scraper = ScrapeWebsiteTool(website_url='https://en.wikipedia.org/wiki/Artificial_intelligence')
wiki_text = scraper.run()

# Define the agent
data_analyst = Agent(
    role='Educator',
    goal="Answer questions based on Wikipedia content about AI.",
    backstory="You are a data expert specializing in AI and NLP.",
    verbose=True,
    allow_delegation=False,
)

# Correct Task usage
test_task = Task(
    description=f"Using the following Wikipedia content, answer: What is Natural Language Processing?\n\n{wiki_text}",
    agent=data_analyst,
    expected_output="An accurate explanation of NLP based on the Wikipedia article."
)

# Create the crew
crew = Crew(
    agents=[data_analyst],
    tasks=[test_task]
)

# Run the crew
output = crew.kickoff()
print(output)
