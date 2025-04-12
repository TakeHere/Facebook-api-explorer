import requests
from utils import *


mainURL = "https://graph.facebook.com/v22.0/ads_archive"


def sendRequest(params, access_token):
    requestURL = mainURL + "?access_token=" + access_token

    for key, value in params.items():
        if isinstance(value, list):
            if len(list(value)) != 0:        
                requestURL += f"&{key}={listToSTR(value)}"
        else:
            requestURL += f"&{key}={str(value)}"


    requestURL += "&fields=ad_creation_time,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_descriptions,ad_creative_link_titles,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,age_country_gender_reach_breakdown,beneficiary_payers,eu_total_reach,languages,page_name,publisher_platforms,target_ages,target_gender,target_locations,impressions,spend"

    try:
        response = requests.get(requestURL)

        print("Request URL:", requestURL)

        if response.status_code == 200:
            print("Request was successful.")
            #print(response.json())

            return response.json()
        else:
            print("Request failed with status code:", response.status_code)
            print("Request URL:", requestURL)
            print(response.text)
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None