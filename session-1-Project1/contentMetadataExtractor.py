# Made by: Thomas Magnussen
# Description: Extract actors from IMDb using a predefined list of known series content IMDb ids.
# Disclaimer: 
# Provided as-is. This is _not_ production-level code. Use this code at your own risk.
# Also note, setting simulatedExecutionMode = False may violate IMDb's terms of service.

# IMDb blocks automated requests, so the code simulates the process without actual HTTP requests.
# These blocks can be circumvented, but are out of scope for this exercise.
# As an alternative, local HTML files based on actual IMDb http respones are used to simulate.

import os
import requests
from bs4 import BeautifulSoup

# Simulate or perform actual HTTP requests
simulatedExecutionMode = True

actorLimit = 10  # Limit the number of actors to extract per series

# Define a set of known series with their IMDb IDs
# This set is used to filter the content metadata to only include these series.
explicitSeriesSet = {
  "The Day of the Jackal": "tt24053860",
  "The Night Manager": "tt1399664",
  "Chernobyl": "tt7366338",
  "True Detectives": "tt2356777", # Has multiple seasons with different actors - could filter.
  "Das Boot": "tt0081834"
}

# Define the HTTP request pattern for fetching full credits from IMDb
# The pattern includes a placeholder for the IMDb ID of the series.
httpRequestPattern = "https://www.imdb.com/title/{}/fullcredits/"

# Define the Actor class to represent each actor
class Actor:
    def __init__(self, actor, character, imdbActorId):
        self.actor = actor
        self.character = character
        self.imdbActorId = imdbActorId

    def to_dict(self):
        return {
            'actor': self.actor,
            'character': self.character,
            'imdbActorId': self.imdbActorId
        }

# Define the Series class to represent a series and its actors
class Series:
    def __init__(self, seriesName, imdbSeriesId):
        self.series_name = seriesName  # Placeholder, will be set later
        self.actors = [] # No type-safety for simplicity at this point
        self.imdbSeriesId = imdbSeriesId
        
    def add_actor(self, actor_instance):
        if isinstance(actor_instance, Actor):
            self.actors.append(actor_instance)
        else:
            raise TypeError("Only instances of Actor can be added.")

    def to_dict(self):
        return {
            'series': self.series_name,
            'actors': [actor.to_dict() for actor in self.actors],
            'imdbSeriesId': self.imdbSeriesId
        }

# Initialize an empty dictionary to store the HTTP responses
httpResponsesSet = {}

# Initialize an empty list to store Series instances   
seriesList = []

# Loop through the IMDb IDs and fetch the full credits page for each series
for series_name, imdb_id in explicitSeriesSet.items():
    url = httpRequestPattern.format(imdb_id)
    print(f"SimMode: {simulatedExecutionMode} - Requesting " + series_name +": " + url)
    
    # Each response is stored in the dictionary with the IMDb ID as the key.
    if not simulatedExecutionMode:
        httpResponsesSet[imdb_id] = requests.get(url)
    else:
        # Simulate the HTTP response for demonstration purposes
        # In a real scenario, you would use requests.get(url) to fetch the data.
        # Instead we read from a local file to simulate the response, the file naming convention is based on the IMDb ID.
        current_directory = os.getcwd() + "\\session-1-Project1\\"
        fileName = f'{imdb_id}.html'
        with open(current_directory+fileName, 'r', encoding='utf-8') as file:
            customeHTTPResponse = requests.Response()
            customeHTTPResponse.status_code = 200
            customeHTTPResponse._content = file.read().encode('utf-8')
            httpResponsesSet[imdb_id] = customeHTTPResponse
    
# Precondition / Assumption: Responses are segmented on Series, hence creating series instance for each response
# Each response is parsed to find the cast list and extract actor names and their characters.
for imdb_id, response in httpResponsesSet.items():
    
    # Check if the response was successful        
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Fragile, as IMDb may change the HTML structure.
        imdbSeriesTitle = soup.find('h2', {'data-testid': 'subtitle'}).text.strip()
        seriesInstance = Series(imdbSeriesTitle, imdb_id)

        # Scraping the Cast section
        cast_section = soup.find_all("div", {"data-testid": "sub-section-cast"})
        # Extracting rows of actors
        # Fragile, as IMDb may change the HTML structure.
        cast_list = cast_section[0].find_all('li', class_='ipc-metadata-list-summary-item sc-2578cde7-0 gSIobG full-credits-page-list-item')

        # Limit the number of actors to process
        cast_list_subset = cast_list[:actorLimit]

        for actor in cast_list_subset:
            
            # Actors are divided into Name and Character div/a, i.e. 2 elements per actor.
            # Fragile, as IMDb may change the HTML structure.
            actorName       = actor.find('a', class_='ipc-link ipc-link--base name-credits--title-text name-credits--title-text-big').text.strip()
            characterName   = actor.find('a', class_='ipc-link ipc-link--base ipc-link--inherit-color').text.strip()
            # href pattern is: /name/nm1519666/..., so splitting by '/' and taking the 4th element gives us the IMDb actor ID.
            actorId         = actor.find('a', class_='ipc-link ipc-link--base ipc-link--inherit-color')['href'].split('/')[4]
            actorInstance = Actor(actorName, characterName, actorId)
            
            seriesInstance.add_actor(actorInstance)
        
        seriesList.append(seriesInstance)

    else:
        print(f"Failed to retrieve data for {series_name}. Status code: {response.status_code}")

print("All responses processed.")
print("")

for series in seriesList:
    print(f"Series: {series.series_name} (IMDb ID: {series.imdbSeriesId})")
    for actor in series.actors:
        print(f"ActorId: {actor.imdbActorId}, Actor: {actor.actor}, Character: {actor.character}")
    
    print("")
       
print("Execution completed.")