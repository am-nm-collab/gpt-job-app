import openai
import json
from dotenv import load_dotenv
import os
import supabase


# CONFIG
load_dotenv()

## OpenAI Config
openai.api_key = os.getenv('OPENAI_API_KEY')
max_tokens=1000
system_prompt = "You are a helpful assistant who helps people turn rough notes on their job histories into clear, structured resumes."

## DB config (local for POC)
output_folder = 'db/'


# DB FUNCTIONS

# Put to store basic Linkedin data in S3 for a user If it already exists, update it, preserving any pargraph data they input about their work history in our app
# Note untl we have a database, this same function can be used to create a user, update any paragraph info about that user's job history, etc. It will read that user's data out, add data to fields, and overwrite the whole object in S3.
def put_user_data(user_id: str, payload: dict = {}) -> None:
  data = payload
  with open(f"{output_folder}{user_id}.json", "w") as f:
    json.dump(data,f)

# Read the user's data into a json object
def get_user_data(user_id: str) -> dict:
  with open(f"{output_folder}{user_id}.json", "r") as f:
    data = json.load(f)
  return data


# API FUNCTIONS

# Get basic info from linkedin profile. For now let's use mock data. Need to figure out how to auuth too. Call this any time the user wants to update their work history.
def get_linkedin_profile() -> dict:
  return {
    "id": "123456789",
    "firstName": "Jane",
    "lastName": "Doe",
    "headline": "Senior Software Engineer at TechCorp Inc.",
    "positions": {
      "_total": 3,
      "values": [
        {
          "id": 987654321,
          "title": "Senior Software Engineer",
          "company": {
            "id": 12345,
            "name": "TechCorp Inc.",
            "type": "Privately Held",
            "industry": "Information Technology and Services"
          },
          "startDate": {
            "month": 3,
            "year": 2021
          },
          "isCurrent": true
        },
        {
          "id": 123456789,
          "title": "Software Engineer",
          "company": {
            "id": 23456,
            "name": "Innovative Solutions Ltd.",
            "type": "Privately Held",
            "industry": "Information Technology and Services"
          },
          "startDate": {
            "month": 8,
            "year": 2019
          },
          "endDate": {
            "month": 2,
            "year": 2021
          },
          "isCurrent": false
        },
        {
          "id": 567891234,
          "title": "Junior Developer",
          "company": {
            "id": 34567,
            "name": "StartupXYZ",
            "type": "Privately Held",
            "industry": "Computer Software"
          },
          "startDate": {
            "month": 6,
            "year": 2018
          },
          "endDate": {
            "month": 7,
            "year": 2019
          },
          "isCurrent": false
        }
      ]
    }
  }


# LLM FUNCTIONS

# Take a user's paragraph inputs and generate a distilled breakdown of their work history with better structure. This will be used to generate the resume.
# Note that we use put_user() here at the end as we will have added a "structured_work_history" field to the user's data in S3.
def structure_work_history(user_id: str, brain_dump: str) -> dict:
  prompt = f'''
  Turn this brain dump of my experience at a company into a structured JSON of relevant information about a work history that can go into a resume.
  Include only the following fields, and no other fields: "Activities" (A list of key activites involved), "Responsibilities" (A list of responsibilities involved), "Skills" (a list of skills used), and "Impact" (a list of JSON objects containing all measurable impacts, comprised of a "metric" field of what the impact was, and a "value" field of the numerical result) as fields in the json:
  {brain_dump}
  '''
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      max_tokens=max_tokens,
      messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": prompt}
          ]
  )
  data = json.loads(response["choices"][0]["message"]["content"])
  try:
    user_data = get_user_data(user_id)
  except FileNotFoundError:
    user_data = {}
  user_data["structured_work_history"] = data
  put_user_data(user_id, user_data)
  return user_data

# Given text a user copies into a field representing a job description, and a user's structured work history, generate resume data in JSON form, and store it in S3 under the user's file in a new field with a UUID.
# Include the job title and company name. In future we can accept Lever or LinkedIn or whatever job posting links and know how to pull the title, JD etc.
def generate_resume_json(user_id: str, company: str, job_title: str, job_description: str) -> dict:
  structured_work_history = get_user_data(user_id)["structured_work_history"]
  prompt = f'''
  Turn the following json data into lines of a resume that will be attractive to a hiring manager looking for a {job_title} at {company}.
  Store the lines in a list of JSON objects, where each object has the key "line" with the value as the text of the resume line. Only return the list of JSON objects in your response, nothing else:
  {structured_work_history}
  '''
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      max_tokens=max_tokens,
      messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": prompt}
          ]
  )
  data = json.loads(response["choices"][0]["message"]["content"])
  try:
    user_data = get_user_data(user_id)
  except FileNotFoundError:
    raise Exception("User data not found")
  user_data["resumes"] = {}
  user_data["resumes"][f"{company}_{job_title}"] = data
  put_user_data(user_id, user_data)
  return user_data


# Convert JSON into a markdown and then convert to PDF
def json_to_pdf(user_id: str, resume_json: str):
  return None


# Edit these values to create different work histories and resume points.
user_id = "123123"
brain_dump = '''
I started this startup Vorstella, I was responsible for go to market including product strategy and sales. I hired 8 engineers, I raised 3.4mm in venture capital, I built a pipeline of $5MM out of a 10 enterprise prospects including Walmart, Walgreens, Macquarie bank, FireEye, and more. I coded our first prototype that showed that our product was viable, and that contributed to our fundraise. I was on the board, I communicated progress to that board every month, I trained and managed support staff and product management staff, and I worked with engineering to build our MVP. I finally sold the company in a talent acquisition to First Republic Bank. Skills included coding in python, using python ml libraries like scikit-learn, setting up our entire pipeline and marketing outreach program and executing it with tools like Outreach.io, pipeline management with Salesforce, etc.
'''

print("Structuring work history")
structure_work_history(user_id, brain_dump)
print("Generating resume bullet points")
generate_resume_json(user_id, "First Republic Bank", "Senior Software Engineer", "")
print("Look at the db/ folder to see the output.")
