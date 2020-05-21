import json, csv
import pandas as pd

from shpprocess import SHPProcessor


'''
Q3. are less trusting areas tweeting more about covid19?

tweet[is_covid_relevant] --> Tweet is covid relevant (count for each area)
each stat area has "trust_1_3_pc_synth" --> percentage of people with low trust

'''
def setup_geo_trust_data():
    with open("json/trust_data.json") as f:
        data = json.load(f)
        trust_data = []
        state_code_map = {"1" : "New South Wales",
                        "2": "Victoria",
                        "3": "Queensland",
                        "4": "South Australia",
                        "5": "Western Australia",
                        "6": "Tasmania",
                        "7": "Northern Territory",
                        "8": "Australian Capital Territory",
                        "9": "Other Territories"}

        '''
            Load trust data from each SA2
            relevant fields for analysis:
            "trust_1_3_pc_synth" --> how many have trust between 1 and 3 (low)
            "trust_5_7_pc_synth" --> how many have trust between 5 and 7 (high)
        '''
        for entry in data["features"]:
            properties = entry['properties'] # contains SA2 ID, which we can cross-ref with ABS data
            properties["panic_buying_tweets_count"] = 0 # append count of panic buying tweets here
            properties["panic_buying_tweets"] = [] # append text/id of tweets here
            properties["doc_type"] = "q3_data"

            # use state name instead of code for consistency
            properties["state"] = state_code_map[properties["state"]]

            trust_data.append(properties)

        # print(trust_data[0].keys())
        return trust_data

'''
Q2. does positive/negative tweet sentiment correlate with 2019 election results (coalition support)?

tweet[score] --> individual tweet sentiment (take an average for each area)

tpp_liberal_national_coalition_votes --> # number of liberal party votes
tpp_australian_labor_party_votes --> # number of labor party votes

coalition support = (liberal vote / liberal vote + labor vote)

'''
def setup_geo_election_data():
    with open("json/election_data.json") as f:
        data = json.load(f)

        election_data_polling_place = {}
        election_data_polling_place["Latitude"] = []
        election_data_polling_place["Longitude"] = []
        election_data_polling_place["tpp_liberal_national_coalition_votes"] = []
        election_data_polling_place["tpp_australian_labor_party_votes"] = []
        election_data_polling_place["polling_place_name"] = []

        '''
            Load 2019 two-party-preferred election data, then
            aggregate each polling place's results into SA2

            relevant fields for processing/analysis
            "tpp_liberal_national_coalition_votes"
            "tpp_australian_labor_party_votes"
            "latitude"/"longitude" --> use these to aggregate

        '''
        for entry in data["features"]:
            properties = entry['properties']


            lat = properties["latitude"]
            long = properties["longitude"] # or use point
            libvote = properties["tpp_liberal_national_coalition_votes"]
            labvote = properties["tpp_australian_labor_party_votes"]
            polling_place = properties["polling_place_name"]


            # gather polling data for each polling place
            election_data_polling_place["polling_place_name"].append(polling_place)
            election_data_polling_place["Latitude"].append(lat)
            election_data_polling_place["Longitude"].append(long)
            election_data_polling_place["tpp_liberal_national_coalition_votes"].append(libvote)
            election_data_polling_place["tpp_australian_labor_party_votes"].append(labvote)


        # match coordinates to their SA2 area
        election_data_sa2 = {}

        matched_coordinates_obj = json.loads(SHPProcessor("SA2").match_coordinates(election_data_polling_place))

        # aggregate data: sum total liberal and labour votes for each SA2 area
        for x in matched_coordinates_obj["features"]:
            entry = x["properties"]
            sa2code = entry["SA2_MAIN16"]
            if sa2code not in election_data_sa2:
                newEntry = {}
                newEntry["sa2_code16"] = entry["SA2_MAIN16"]
                newEntry["sa2_name16"] = entry["SA2_NAME16"]
                newEntry["latitude"] = entry["Latitude"]
                newEntry["longitude"] = entry["Longitude"]
                newEntry["state"] = entry["STE_NAME16"]
                newEntry["tpp_australian_labor_party_votes"] = entry["tpp_australian_labor_party_votes"]
                newEntry["tpp_liberal_national_coalition_votes"] = entry["tpp_liberal_national_coalition_votes"]
                newEntry["average_sentiment"] = 0
                newEntry["doc_type"] = "q2_data"

                election_data_sa2[sa2code] = newEntry
            else:
                # entry exists, just update counts
                election_data_sa2[sa2code]["tpp_australian_labor_party_votes"] += entry["tpp_australian_labor_party_votes"]
                election_data_sa2[sa2code]["tpp_liberal_national_coalition_votes"] += entry["tpp_liberal_national_coalition_votes"]

        # print(election_data_sa2["311061333"].keys())
        #return list(election_data_sa2.values())
        return election_data_sa2
        '''
            ready to insert into couchdb.
            Insert the SA2 code, and the aggregate results for each SA2 region in election_data_sa2
        '''


'''
Q1. are people tweeting about covid19 living in more economically unequal areas?

is_covid_relevant --> tweet is covid relevant (count all for each area)
"gini_coefficient_no" --> income inequality for each area

'''
def setup_geo_economy_data():
    with open("json/income_data.json") as f:
        data = json.load(f)
        income_data = []

        sa3_id_name_map = {}
        with open("sadata/SA3_2016_AUST.csv", mode="r") as sa3csv:
            csv_reader = csv.DictReader(sa3csv)
            for row in csv_reader:
                code = row['SA3_CODE_2016']
                name = row['SA3_NAME_2016']
                state  = row['STATE_NAME_2016']
                sa3_id_name_map[code] = (name, state)


        '''
            Load income data from each SA3 (a larger area than SA2)
            relevant fields for analysis:
            "gini_coefficient_no" --> gini in an SA3 area
            "median_aud" --> median income in area
            "income_share_top_10pc" --> share of top 10% of earners in an SA3 area
        '''
        for entry in data["features"]:
            properties = entry['properties']
            properties["stimulus_tweets"] = 0
            properties["doc_type"] = "q1_data"

            # get the SA3 name from the code
            code = properties['sa3_code_2016']
            sa3name = sa3_id_name_map[code][0]
            state = sa3_id_name_map[code][1]

            properties["sa3_name16"] = sa3name
            properties["state"] = state

            # rename key for consistency
            properties["sa3_code16"] = properties.pop("sa3_code_2016")

            income_data.append(properties)

        # print(income_data[0].keys())
        return income_data
        '''
            ready to insert into couchdb aggregate income data for each SA3 area

        '''
'''
Q4: do the number of non-english tweets in different languages
show a relationship with the migration rate of their neighbourhood

tweet[lang] --> language of each tweet (aggregate for each area)
total_migration_rate --> percentage of migrants in each area

'''
def setup_migration_data():
    with open("json/migration_data.json") as f:
        data = json.load(f)
        migration_data = []

        for entry in data['features']:
            properties = entry['properties']
            properties['doc_type'] = "q4_data"
            properties['sa2_code16'] = properties.pop("sa2_main11")
            properties['sa2_name16'] = properties.pop("sa2_name11")
            migration_data.append(properties)

        return migration_data
