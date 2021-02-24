# etl_csv_to_mongo

Start services as defined in the `docker-compose.yml` file.
To start the *mongo database* and the *database GUI* (Mongo Express):

`docker-compose up -d` 

> Note2: for a local build of the `Dockerfile_etl.yml`, it is first required to prepare the `.env` file with the required env variables

### Environment Variables
```dotenv
[Mongo DB]
MONGODB_URL=mongodb://root:admin@localhost:27017/?authSource=admin

[Kaggle]
KAGGLE_USERNAME={{your_user_here}}
KAGGLE_KEY={{your_api_here}}
```
#### Option 1: run locally
Then execute the `etl.py` script to perform the Extract-Transform-Load operation.
`pip install -r requirements.txt`
`python src/project/etcl.py`

#### Option 2: run through Docker
`docker build -t etl .`
`docker run --env-file ./src/project/.env --network=mongodb_network etl`
#### Mongo Database GUI (Mongo Express)
Use the following credentials to access the database GUI (`http://localhost:8081/`)
* user: admin
* password: admin