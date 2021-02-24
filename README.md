# etl_csv_to_mongo
This project consists of the following objectives:

1. Download data from Kaggle
2. Perform transformations, grouping similar data together
3. Lastly, load data in the appropriate format to a document-oriented database hosted on Docker

Which represents an **E**xtract-**T**ransform-**L**oad (ETL) pipeline
.
#### Summary
+ Data file: [Kaggle | Marvel Superheroes: marvel_dc_characters.csv](https://www.kaggle.com/dannielr/marvel-superheroes?select=marvel_dc_characters.csv)
+ Choosen format: JSON
+ Choosen database: MongoDB

## Installation
In order to replicate this solution it is required to set up the database first, then run the ETL Python script.

> **Please note**: The following instructions assume you already have Docker and Python (3.8) installed

<br>
Start the services by running the following command:
```
docker-compose up -d
```

The instructions defined in the `docker-compose.yml` file will, in the following sequence:
1. Start the **mongo database**
2. Start the **database GUI** (Mongo Express) in the background

> The database GUI can be accessed locally, `http://localhost:8081/`, with the following credentials:
> + **User**: admin
> + **Password**: admin

<hr>

#### Environment Variables
This project uses the `.env` file (located under `src/project`) to make environment variables accessible to the code, without hardcoding/exposing sensitive information, such as credentials.

The Kaggle api requires the following credentials to authenticate and download files. See [link](https://github.com/Kaggle/kaggle-api#api-credentials) for further instructions.
```dotenv
[Mongo DB]
MONGODB_URL=mongodb://root:admin@localhost:27017/?authSource=admin

[Kaggle]
KAGGLE_USERNAME={{your_user_here}}
KAGGLE_KEY={{your_api_here}}
```
<hr>

#### Run ETL locally
Lastly, it is required to install the project dependencies before executing the `etl.py` script.
<br>
After cloning this repo and changing to the project directory (`etl_csv_to_mongo`), run the following commands:
+ **Install dependencies**: `pip install -r requirements.txt`
+ **Execute ETL**: `python src/project/etl.py`
