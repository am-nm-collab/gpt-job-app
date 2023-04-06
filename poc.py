from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.document_loaders import UnstructuredURLLoader
from pydantic import BaseModel, Field, validator
from typing import List
from dotenv import load_dotenv
import json
import os
import validators

# CONFIG
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_OUTPUT_DIR = os.getenv('DB_OUTPUT_DIR').strip("/")
chat = ChatOpenAI(model_name="gpt-3.5-turbo")
system_message = "You are a career coach who helps people write great resumes that get noticed, so they can land their dream job."
# UTILS

def pretty_print_resume(resume_json):
  # For a base resume or a completed resume, pretty print it to the commandline.
  return None

def pretty_print_job_history(job_history):
  # For a single job history, pretty print it to the commandline.
  return None

# DB LOGIC
# Note: These functions will be modified heavily when we move to a real datastore. Right now its just a flat file.

def read_json(file_path: str = f'{DB_OUTPUT_DIR}/user_data.json') -> str:
  # temp function to use while we use local storage
  with open(file_path, 'r') as f:
    return json.load(f)

def update_json(data: dict = None, key: str = None, file_path: str = f'{DB_OUTPUT_DIR}/user_data.json') -> None:
  # Temp function to use while we use local storage.
  if not key:
    with open(file_path, 'w') as f:
      json.dump(data, f)
  else:
    j_data = read_json(file_path)
    j_data[key] = data
    with open(file_path, 'w') as f:
      json.dump(j_data, f)


  # Read a JSON file and return the data as a dict
def set_conversation_history(conversation_history: dict) -> None:
  # Save the entire conversation history in the DB.
  data = read_json()
  data['conversation_history'] = conversation_history
  update_json(data)

def set_work_history(work_history: dict) -> None:
  # Save the linkedin work history provided by the user in the DB
  data = read_json()
  data['work_history'] = work_history
  update_json(data)

def set_base_resume(base_resume: dict) -> None:
  # Save the base resume generated by the LLM from the complete work history given by the user in the database
  data = read_json()
  data['base_resume'] = base_resume
  update_json(data)

def set_resume(resume_id: str, resume: dict) -> None:
  # Save the taiilored resume along with the job description data (either extracted or provided by the user) in the database
  data = read_json()
  data['resumes'] = []
  data['resumes'][resume_id] = {}
  data['resumes'][resume_id] = resume
  update_json(data)

def set_resume_markdown(resume: dict) -> None:
  # Save the taiilored resume as a markdown file in the filesystem and return the path.
  return None


def get_all_user_data(user_id: str = None) -> None:
  # Read back the entire JSON data stored for a user. This is used temporarily while we wait for a real database, as we need to read, update, and write back the entire dataset when we update any fields in flat files.
  return read_json()

def get_conversation_history() -> dict:
  # Load the entire conversation history from the DB.
  return read_json()['conversation_history']

def get_work_history() -> dict:
  # Load the work history provided by the user from the DB
  return read_json()['work_history']

def get_base_resume() -> dict:
  # Load the base resume generated by the LLM from the complete work history given by the user from the DB
  return read_json()['base_resume']

def get_resume(resume_id: str) -> dict:
  # Load the taiilored resume along with the job description data (either extracted or provided by the user) from the DB
  return read_json()['resumes'][resume_id]


# EXTERNAL API LOGIC

def save_linkedin_work_history(linkedin_url: str = "") -> None:
  # Placeholder of dummy data until we get real API access to linkedin
  linkedin_work_history = {
    "work_history": [
      {
        "company": {
          "id": "123456",
          "name": "ABC Corporation",
          "industry": "Information Technology and Services"
        },
        "position": {
          "id": "987654",
          "title": "Software Engineer",
          "description": "Responsible for developing and maintaining web applications using modern web technologies. Cut latency in half and delivered solution for half the projected cost"
        },
        "location": "San Francisco, California, United States",
        "start_date": "2018-06-01",
        "end_date": "2021-08-31"
      },
      {
        "company": {
          "id": "234567",
          "name": "XYZ Inc.",
          "industry": "Computer Software"
        },
        "position": {
          "id": "876543",
          "title": "Senior Software Engineer",
          "description": "Led a team of software engineers to build scalable and reliable software solutions. Grew team to 10 engineers and delivered 3x the value in half the time."
        },
        "location": "New York, New York, United States",
        "start_date": "2021-09-01",
        "end_date": "present"
      }
    ]
  }
  # We need to store our generated work history, user inputs, etc in the JSON file, and the best place to store it is in the work_history field returned by the linkedin API. So we need to do some prep to make sure we don't get errors for missing keys.
  for job in linkedin_work_history["work_history"]:
    job["position"]["app_data"] = {}
    # We want to store all user inputs about the role now and in the future as list of strings. We copy the input from LinkedIn to get started.
    job["position"]["app_data"]["user_description_inputs"] = [job["position"]["description"]]
  update_json(linkedin_work_history)
  return None

# LLM LOGIC

def generate_structured_role_description(role_description: List) -> dict:
  # Given a description of an individual job, extract the salient points and return a structured format
  class StructuredRoleDescription(BaseModel):
    activities: List[str] = Field(description="List of activities the user performed in the role.")
    skills: List[str] = Field(description="List of skills the user developed in the role.")
    impact: List[str] = Field(description="List of measurable impact the user had in the role.")

  parser = PydanticOutputParser(pydantic_object=StructuredRoleDescription)
  prompt = PromptTemplate(
    template = "Given the following description of what an employee did in a role, extract the activities performed, skills developed, and measurable impact the employee had. If any of those pieces of information is not avialable and clearly defined in the role description, leave the field empty.\n{format_instructions}.\nDo not return anything other than the structured JSON object in your response.\n{role_description}\n",
    input_variables = ["role_description"],
    partial_variables = {"format_instructions": parser.get_format_instructions()}
  )
  input = prompt.format_prompt(role_description=role_description)
  messages = [
    SystemMessage(content=system_message),
    HumanMessage(content=input.to_string())
  ]
  output = chat(messages).content
  try:
    parser.parse(output)
    output = json.loads(output)
  except:
    new_parser = OutputFixingParser.from_llm(parser=parser, llm=chat)
    new_parser.parse(output)
    output = json.loads(output)
  return output

def generate_base_resume(work_history: dict) -> None:
  # Given a complete structured work history, distill down to the salient points in a "base resume" in JSON form to make rendering easier
  for job in work_history:
    job["position"]["app_data"]["structured_role_description"] = generate_structured_role_description(job["position"]["app_data"]["user_description_inputs"])
  set_work_history(work_history)

def generate_missing_work_history_request(base_resume: dict, job_description: str):
  # Given a linkedin work history, distill down to a structured format and generate a list of questions to prompt the user for more information to create a more complete base resume with required fields like activities, skills, and measurable impact.
  # Note that you may want to code some more complex logic here to enter into and come out of holes based on user responses. An example is if you ask for impact the user had, but they don't give you something measurable, prompt until you get the info you need.
  return None

def generate_specific_work_history_request(base_resume: dict, job_description: str):
  # Given a base resume and a job description, generate a list of questions to prompt the user for more information in order to better tailor their resume for the role.
  return None

def generate_final_resume(job_description: str) -> dict:
  # Given a base resume and a job description, generate a final resume that is tailored to the job description. This is the final product that will be presented to the user.
  work_history = get_work_history()
  if validators.url(job_description):
    urls = [job_description]
    loader = UnstructuredURLLoader(urls=urls)
    job_description = loader.load()

  prompt = PromptTemplate(
    template = "The following JSON represents a candidate's work experience, including activities, skills, and measurable impact at each job:\n{work_history}\nGiven the candidates experience, construct a list of resume points for each job they have had that is specifically tailored to this job description:\n{job_description}\n. In addition to the list of resume points for each job, give a brief assessment of whether or not the candidate is a good fit for the role.",
    input_variables = ["work_history", "job_description"],
    partial_variables = {}
  )
  input = prompt.format_prompt(work_history=work_history, job_description=job_description)
  messages = [
    SystemMessage(content=system_message),
    HumanMessage(content=input.to_string())
  ]
  output = chat(messages).content
  return output


  return None

# COMMANDLINE LOGIC

def gather_missing_work_history(work_history: dict) -> None:
  # Given a LinkedIn work history, gather any missing work history from the user via commandline prompts. Save the updated data in the DB.
  return None

def gather_specific_work_history(base_resume: dict, job_description: str) -> None:
  # Given a base resume and a specific job description, gather any additional information that might help make the resume better tailored to the job description. Update the base_resume with the new information.
  return None

# MAIN LOGIC
def main():

  # POC FLOW

  # Get work history from linkedin, create a base resume, and save it to the DB
  #linkedin_url = "https://www.linkedin.com/in/username/"
  #save_linkedin_work_history(linkedin_url)
  #work_history = get_work_history()
  #generate_base_resume(work_history)

  # Get a job posting (copy paste or url) and combine it with the base resume to generate a final resume
  job_description = "https://www.linkedin.com/jobs/view/3533892617"
  output = generate_final_resume(job_description)
  print(output)


  # STARTING FLOW

  # Main flow of commandline requests

  # Prompt user for linkedin profile

  # Enter flow of gathering missing work history via prompts

  # Create base resume and present it to the user with the pretty print utils

  # WHILE TRUE LOOP (stay until user exits)

  # Prompt user for job description

  # Enter flow of gathering specific work history via prompts

  # Create final resume and present it to the user with the pretty print utils. Tell them the directory where the resume markdown file is stored

  # Prompt user for another job description

if __name__ == '__main__':
  main()
