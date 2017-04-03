## How to run this
Run the following commands
1. `python survey_server.py create_db`, this will create the file `surveys.db` which will contain the question contents, users, etc.
2. `python survey_server.py add_data sample_data.json`, this populates the database with questions
3. `python survey_server.py add_user jon` to create a user, you will be prompted to enter a password
4. `python survey_server.py run` will start a webserver

## Customizing the survey
1. Edit the file `survey_form.py` to change the HTML for the survey.
2. Edit or generate a JSON file similar to `sample_data.json`
