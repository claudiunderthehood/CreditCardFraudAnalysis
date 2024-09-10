import datetime
import requests
import time
import schedule

import pandas as pd
from modules.generatorClass import Generator
from modules.nightCheck import night_indicator

def gen():

    url = "http://logstash:5044"

    # New data generation using the Generator class
    generate: Generator = Generator(num_clients=5000, num_terminals=10000, seed_clients=0, seed_terminals=0)
    transactions_df: pd.DataFrame = generate.dataset(num_days=183, radius=5)

    transactions_df['ON_NIGHT']=transactions_df.TRX_DATETIME.apply(night_indicator)

    transactions_df = transactions_df.drop("TRX_DAYS", axis=1)
    transactions_df = transactions_df.drop("FRAUD_SCENARIO", axis=1)

    transactions_df.rename(columns={"TRX_ID": "V0", "TRX_DATETIME": "V1", "CLIENT_ID": "V2", "TERMINAL_ID": "V3",
                                        "TRX_AMOUNT": "V4", "TRX_SECONDS": "V5", "IS_FRAUD": "V6", 
                                        "ON_NIGHT": "V7"}, inplace=True)

    # Prepare the transactions for Logstash
    json_data = transactions_df.to_json(orient='records')

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json_data, headers=headers)

        if response.status_code == 200:
            print("Data successfully sent to Logstash.")
        else:
            print(f"Failed to send data to Logstash. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

schedule.every().day.at("23:59").do(gen)

gen()

while True:
    schedule.run_pending()
    time.sleep(1)
