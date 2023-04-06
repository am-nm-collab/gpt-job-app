# gpt-job-app
flask app that uses OpenAI's gpt api to help you write documents to help you get a job like resumes, cover letters, stories to tell in interviews.

# How to run

## Install dependencies
First install dependencies by running
```
pip install -r requirements.txt
```

## Set up .env file in root directory
This is a POC branch so the code is in poc.py.

You have to create a .env file in the root directory. It should look like this, with the data filled out replacing the <> placeholders.

```
OPENAI_API_KEY=<your openai API key. This project uses gpt-3.5-turbo so it should be very cheap to run and test.>
DB_OUTPUT_DIR=<path of the folder where you will store user data, like "db">
```

## Running the code
Once you have set the above up you can run
```
python poc.py
```
