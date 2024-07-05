To run (for mac):
1. Download and install python: https://www.python.org/downloads/
2. [Create a google maps api key](https://developers.google.com/maps/documentation/embed/get-api-key#create-api-keys)
3. Add the key to the geolocator initializer in `market_research.py`: 
```
geolocator = GoogleV3(api_key='ExAmPle-KeY')
```
4. Add your state(s) to STATES_TO_ANALYZE (comma separated, single quotes, first letter capitalized):
```
STATES_TO_ANALYZE = {
    'North Carolina', 'Alabama', 'Georgia'
}
```
5. Run the python script:
```
cd ~/Path/to/repo/market-research
```
```
python market_research.py
```

If you get any errors about missing packages or libraries, you'll need to run `pip install <package-name>` for each package you're missing before running the script.
