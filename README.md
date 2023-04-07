# gpt-job-app
flask app that uses OpenAI's gpt api to help you write documents to help you get a job like resumes, cover letters, stories to tell in interviews.

# How to run

## Install dependencies
First install dependencies by running
```
pip install -r requirements.txt
```

## Set up .env file in root directory
Rename .env.template to .env and enter your OpenAI API key This project uses gpt-3.5-turbo so it should be very cheap to run and test.

## Run the code
Once you have set the above up you can run
```
python main.py
```

Then follow the prompts to get a resume generated for you. The resume output is currently JSON stored in {DB_OUTPUT_DIR}/user_data.json.

To test out the interactive chat functionality, try uncommenting lines 137 and 154 and commenting out lines 138 and 155. This will create a back and forth to gather more data from the user about activities, skills, and impact that the bot can use to extract key points.

# Limitations

- Still working on finishing touches on storing the resume, right now it just dumps each description for each job into an ugly JSON, need to tweak that
- The prompts could be much better.
