"""Module to query covid APIs."""

import logging
import requests
import time

import pyspark
from pyspark import SparkContext
from pyspark.sql.session import SparkSession

SPARK_CONTEXT =SparkContext()
SPARK_SESSION = SparkSession(SPARK_CONTEXT)

logging.getLogger(__name__).addHandler(logging.NullHandler())

API_BASE_URL="https://api.covid19api.com/"

def _get_data(api):
    """Retrieves the covid data"""
    url = API_BASE_URL + api
    print(url)
    logging.info("Querying URL: %s", url)
    response = requests.get(url)
    count = 0
    retry_count = 50
    if response.status_code == 404:
        logging.error("Received 404")
        return None
    while response.status_code != 200:
        count += 1
        if count == retry_count:
            break
        logging.error("Received status code %s, expected 200",
                      response.status_code)
        time.sleep(2)
        try:
            response = requests.get(url)
        except:
            pass
    if response.status_code != 200:
        # Send emoty dataframe. Remove None
        return None
    rdd = SPARK_CONTEXT.parallelize([response.json()])
    data_frame = SPARK_SESSION.read.json(rdd)
    return data_frame

def get_global_info():
  """Get covid19 info in global level.

  Returns dictionary contains 'NewConfirmed', 'NewDeaths', 'NewRecovered',
      'TotalConfirmed', 'TotalDeaths', 'TotalRecovered'  
  """
  data_frame = _get_data("summary")
  return data_frame.select("Global")

def get_country_info(country):
  api = "dayone/country/{}".format(country)
  return _get_data(api)
