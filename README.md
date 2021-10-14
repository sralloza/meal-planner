# Meal Planner

Meal planning microservice.

Features:

- Rest API (FastAPI)
- Cron scripts to:

  - Update menu in Notion everyday
  - Add tasks to Todoist if some meal needs unfreezing the day before
  - Dabatase backup to AWS

- Notion integration.
- Todoist integration.

## Deploy

Deployment is done via docker.

Notes:

- Remember you can use the tag you like.
- The Dockerfile is designed to work on ARM systems, like a Raspberry Pi.

```shell
# ARM (Raspberry Pi like) pushing it to dockerhub
docker buildx build -t sralloza/meal-planner:stable-arm --platform=linux/arm/v7 --push .

# ARM (Raspberry Pi like) without pushing it to dockerhub
docker buildx build -t sralloza/meal-planner:stable-arm --platform=linux/arm/v7 --load .

# Normal build
docker build -t sralloza/meal-planner:stable .

# You'll probably want to push it to dockerhub
docker push sralloza/meal-planner:stable
```

## Environment

You need to supply the following environment variables (required ones are marked with 🚩). Settings are grouped in categories.

### Server

- 🚩 API_TOKEN (str): token of the API. In order to use the API, users will have to provide this token in their requests via the `X-TOKEN` header.
- ENABLE_PROMETHEUS (bool): if true, the API will enable the prometheus endpoint `/metrics`. Defaults to false.
- PRODUCTION (bool): if true the server will run on production environment. Defaults to false.

### AWS

- 🚩 AWS_ACCESS_KEY_ID (str): AWS access key id.
- 🚩 AWS_SECRET_ACCESS_KEY (str): AWS secret access key.
- 🚩 S3_BUCKET_NAME (str): name of the S3 bucket to save the backups.
- S3_FILE_NAME (str): filename to save the backups in the AWS S3 Bucket. Defaults to `meals.json`.

### Notion

NOTION_ADD_DAY_AFTER_TOMORROW (bool): if true, the meals of the day after tomorrow will also be added to Notion. Defaults to true.
🚩 NOTION_BLOCK_ID (uuid): id of the notion block where the meals will be showed.
🚩 NOTION_KEY (str): notion key to use the notion API.

### Todoist

🚩 TODOIST_PROJECT_ID (int): todoist project id where the tasks will be added.
🚩 TODOIST_TOKEN (str): todoist token to use the todoist API.

### Database

🚩 MYSQL_DATABASE (str): database name.
🚩 MYSQL_HOST (str): mysql host.
🚩 MYSQL_PASSWORD (str): mysql password.
🚩 MYSQL_PORT (str): mysql port.
🚩 MYSQL_USER (str): mysql user.

## Future

AWS and notion settings are currently needed. If you want to use this app without one of them (or both) add an issue and I'll make it optional and configurable.

As said before, the docker image is designed to work on ARM systems. If you want AMD64 support please fill an issue.
