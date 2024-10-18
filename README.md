# business-search
Search for business in cities

## Running
```
export GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
python -m venv .
source ./bin/activate  
pip install -r requirements.txt
python3 ./src/main.py
```

## Considerations
The Google Places API must be enabled in your Google Developer Account: https://developers.google.com/maps/documentation/places/web-service/cloud-setup
This uses quite a few credits, you should lower the search grid size in the getBusinessForCity script if you're just testing the waters
It should take about 45 mins to run