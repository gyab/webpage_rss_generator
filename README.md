Single Python file to generate and update a RSS file based on a certain webpage. The script is uploaded to GCP as a Cloud Function and then using Cloud Scheduler is run for example every day to get the latest content.

The only thing to do is to change the values in the .env file.

Two main functions, create_feed and check_for_update. create_feed initializes a blank RSS file and check_for_update will update the file if new content has been uploaded.
