# webpage_rss_generator 

Single Python file to generate and update a RSS file based on a certain webpage. The script is uploaded to GCP as a Cloud Function and then using Cloud Scheduler is run for example every day to get the latest content.

To upload the file to GCP, you will need to [generate a key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) to represent your service account. Place the newly created JSON file at the root of the project.

The only left thing to do is to change the values in the .env file that represents the website that you want to create a RSS feed from.

The main.py file contains two main functions, create_feed and check_for_update. create_feed initializes a empty RSS file and check_for_update will update the file if new content has been uploaded.
