import datetime as dt
import os
from pathlib import Path
from typing import List
from zipfile import ZipFile

import pandas as pd
import pymongo.errors
from pymongo import MongoClient

# Workaround: loading .env at helper_functions import, before import Kaggle
from src.project.utils.helper_functions import set_logger, silent_remove_file
import kaggle


# Extract
def extract_kaggle_single_file(dataset_name: str, file_name: str) -> pd.DataFrame:
    """Extracts single file from Kaggle dataset, saves raw copy and returns loaded dataframe

    Notes:
        It is a good idea to store raw data for eventual debugging/re-processing.
        Typically it would be saved in a blob storage (S3, Cloud Storage etc.).
        But keeping it locally for this exercise, under the folder: **src/project/data/0_raw**

    Args:
        dataset_name: kaggle dataset name, as `[owner]/dataset`
        file_name: kaggle file name to be extracted and loaded

    Returns:
        Pandas dataframe
    """
    logger = set_logger('Extract')

    logger.info(f'Extracting data from Kaggle -> Dataset: {dataset_name} | File: {file_name}')

    # Download Zipped File
    kaggle.api.authenticate()  # > Note: Kaggle api credentials in .env file
    kaggle.api.dataset_download_file(dataset=dataset_name, file_name=file_name)

    zipped_file_name = file_name + '.zip'

    try:
        # Unzip
        logger.info(f'Unzipping the file: {zipped_file_name}')
        with ZipFile(zipped_file_name, mode='r') as zf:
            zf.extractall()

        # Read CSV
        logger.info(f'Loading the file: {file_name}')
        df = pd.read_csv(file_name)

        # Store raw copy
        today = dt.date.today()

        raw_data_path = Path(__file__).parent / 'data' / '0_raw'
        raw_data_file_path = raw_data_path / file_name.replace('.csv', f'_{str(today)}.csv')

        df.to_csv(raw_data_file_path, index=False)

    except Exception as e:
        logger.error(f'Unzipping: {e}')
        raise

    finally:
        # Executes code block on success or error, deleting downloaded/extracted files (if existing)
        silent_remove_file(zipped_file_name)
        silent_remove_file(file_name)

    return df


# Transform
def transform_dataframe(df: pd.DataFrame) -> List[dict]:
    """Performs data transformations, arranging it as nested JSON to be loaded into document-oriented database.

    Args:
        df: dataframe to be transformed

    Returns:
        List of dictionaries, as a JSON format
    """

    # TODO: Challenge: handling bad characters (tried different encodings to no avail)
    #   Example: df.Name[39644]: tom\u00e1s Ram\u00edrez
    #   Similarly with column `FirstAppearance`, seems to have corrupted records

    # Dropping column with bad/corrupted records
    df = df.drop(columns=['FirstAppearance'])

    # Replace Empty/Null with 0
    df.Appearances = df.Appearances.fillna(0)

    # > Good idea to keep track of when the data was migrated
    execution_date = str(dt.date.today())

    # Arrange dataframe into nested JSON structure, grouping similar data together

    #   > Fast, list comprehension approach, but not so readable. S.O: https://stackoverflow.com/a/55557758
    documents = [{'id': row[0],
                  'name': row[1],
                  'attributes':
                      {'identity': row[2],
                       'alignment': row[3],
                       'status': row[4],
                       },
                  'physicalAttributes':
                      {'eyeColor': row[5],
                       'hairColor': row[6],
                       'gender': row[7]
                       },
                  'appearancesCount': row[8],
                  'year': row[9],
                  'universe': row[10],
                  'dateMigrated': execution_date
                  } for row in zip(df.ID, df.Name,
                                   df.Identity, df.Alignment, df.Status,
                                   df.EyeColor, df.HairColor, df.Gender,
                                   df.Appearances, df.Year, df.Universe)]

    return documents


# Load
def load_list_of_dict_into_mongodb(documents: List[dict], db_name: str, collection_name: str) -> None:
    """Loads list of dictionaries into the respective Mongo Database.

    Args:
        documents: list of dictionaries (JSON-like structure)
        db_name: database name to be used
        collection_name: collection name to be stored

    Raises:
        Gracefully terminates if loading duplicated data. Raises Exception if any other error.
    """
    logger = set_logger('Load')

    client = MongoClient(os.environ['MONGODB_URL'])
    db = client[db_name]
    collection = db[collection_name]

    # Set unique ID fields, to avoid duplicate records (IDEMPOTENT)
    collection.create_index([('id', pymongo.ASCENDING)], unique=True)

    try:
        logger.info(f'Loading {len(documents):,} records into Mongo DB...')
        collection.insert_many([document for document in documents])

    except pymongo.errors.BulkWriteError as e:
        other_than_duplicates = list(filter(lambda x: x['code'] != 11000, e.details['writeErrors']))
        if len(other_than_duplicates) > 0:
            raise

        else:
            logger.warning('Data is already in the database')


if __name__ == '__main__':
    # Extract
    dataset_name = 'dannielr/marvel-superheroes'
    file_name = 'marvel_dc_characters.csv'

    df = extract_kaggle_single_file(dataset_name=dataset_name, file_name=file_name)

    # Transform
    documents = transform_dataframe(df=df)

    # Load
    database_name = 'heroes'
    collection_name = 'characters'
    load_list_of_dict_into_mongodb(documents=documents, db_name=database_name, collection_name=collection_name)
