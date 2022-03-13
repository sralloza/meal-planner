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

```shell
# Build and push it to dockerhub
docker buildx build -t sralloza/meal-planner:$VERSION --platform=linux/arm/v7,linux/amd64 --push .

# Build without pushing it to dockerhub
docker buildx build -t sralloza/meal-planner:$VERSION --platform=linux/arm/v7,linux/amd64 --load .
```

### Environment

You need to supply the following environment variables (required ones are marked with 🚩). Settings are grouped in categories.

#### Server

- 🚩 **API_TOKEN** (`str`): token of the API. In order to use the API, users will have to provide this token in their requests via the `X-TOKEN` header.
- **ENABLE_PROMETHEUS** (`bool`): if `True`, the API will enable the prometheus endpoint `/metrics`. Defaults to `False`.
- **PRODUCTION** (`bool`): if `True` the server will run on production environment. Defaults to `False`.
- **DISABLE_CRON_INTEGRATION** (`bool`) if `True`, the server will not launch cron jobs. It is useful to launch replicas, enabling cron integration in only one of them. It is also useful to deploy on Kubernetes, as the cron jobs can be implemented via `CronJob`.

#### AWS

- 🚩 **AWS_ACCESS_KEY_ID** (`str`): AWS access key id.
- 🚩 **AWS_SECRET_ACCESS_KEY** (`str`): AWS secret access key.
- 🚩 **S3_BUCKET_NAME** (`str`): name of the S3 bucket to save the backups.
- **S3_FILE_NAME** (`str`): filename to save the backups in the AWS S3 Bucket. Defaults to `meals.json`.

#### Notion

- **NOTION_ADD_DAY_AFTER_TOMORROW** (`bool`): if `True`, the meals of the day after tomorrow will also be added to Notion. Defaults to `True`.
- 🚩 **NOTION_BLOCK_ID** (`uuid`): id of the notion block where the meals will be showed.
- 🚩 **NOTION_KEY** (`str`): notion key to use the notion API.

#### Todoist

- 🚩 **TODOIST_PROJECT_ID** (`int`): todoist project id where the tasks will be added.
- 🚩 **TODOIST_TOKEN** (`str`): todoist token to use the todoist API.

#### Database

- 🚩 **MYSQL_DATABASE** (`str`): database name.
- 🚩 **MYSQL_HOST** (`str`): mysql host.
- 🚩 **MYSQL_PASSWORD** (`str`): mysql password.
- 🚩 **MYSQL_PORT** (`str`): mysql port.
- 🚩 **MYSQL_USER** (`str`): mysql user.
- **WAIT_FOR_IT_ADDRESS** (`str`): if is set, it will wait for the database to be ready for max 120 seconds. Must be set to `$MYSQL_HOST:$MYSQL_PORT`. This switch should not be used in Kubernetes deployments, as `initContainers` are designed to cover this exact use case.

#### Other

- **LOCALE_WEEKDAY_NAMES** (`list(str)`): weekday names, starting with Monday and ending with Sunday. Must contain 7 elements (one for each week day).
- **NULL_STR** (`str`): string to represent an empty `lunch1` or `dinner`. Defaults to `N/A`.
- **VARIABLE_STR** (`str`): string to represent a variable meal. Defaults to `Variable`. It's used in the `/shift` endpoint, where all meals which are equal to `VARIABLE_STR` will be treated as empty meals.

## Future

AWS and notion settings are currently needed. If you want to use this app without one of them (or both) add an issue and I'll make it optional and configurable.
