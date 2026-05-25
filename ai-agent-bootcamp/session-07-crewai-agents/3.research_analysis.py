#####
## Sequential but dependent execution
####
from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not set. Copy .env.example to .env and add your key.")
os.environ['OPENAI_API_KEY'] = api_key


# Define agents
researcher = Agent(
    role='Researcher',
    goal='Conduct thorough research on a given topic',
    backstory='An expert analyst with a knack for detailed insights',

)

writer = Agent(
    role='Writer',
    goal='Write compelling content using research',
    backstory='A skilled writer passionate about storytelling'
)

# Define tasks
    #1. Step 1: research_task
    #Agent: researcher
    #
    #Input: {topic: "Quantum Computing"}
    #
    #Output: A research report (text with sources)
    #
    #This output is captured and passed to write_task via the context=[research_task] reference

research_task = Task(
    description='Investigate the latest trends in {topic}.',
    agent=researcher,
    expected_output='A comprehensive research report with sources.'
)
    ##Step 2: write_task
    #Agent: writer
    #
    #Input: It gets:
    #
    #The original input (e.g., topic)
    #
    #The output from research_task via the context parameter
    #
    #The agent uses the context (i.e., the research findings) to generate a blog post
write_task = Task(
    description='Write a blog post about based on the research findings.',
    agent=writer,
    context=[research_task],  # uses the output of research_task internally
    expected_output='An engaging blog post written in markdown format.'
)


# Process.sequential:
# This tells CrewAI to execute tasks in the order they are defined, one after the other — not in parallel —
# and to pass outputs forward when referenced.

# Assemble the crew

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)

# Run the crew with inputs
#USER INPUT ("Quantum Computing") ──┐
#                                   ▼
#       [research_task] ──> Research Report
#                                   │
#context=[research_task]            ▼
#       [write_task] ──> Blog Post Based on Report

result = crew.kickoff(inputs={'topic': 'Quantum Computing'})
print(result.raw)  # .raw gives the raw output string
