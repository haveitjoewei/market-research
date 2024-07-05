"""
Author: Joseph Wei
Date: 2024-07-05
Last Modified: 2024-07-05
Description: This script scrapes data from city-data.com and saves it to a spreadsheet. 
License: MIT License

To use, add your Google Maps API key to line 164: 

geolocator = GoogleV3(api_key='<your api key>')

And add your state to line 274. eg:

STATES_TO_ANALYZE = {
    'North Carolina', 'Alabama', 'Georgia'
}

"""

import requests
import json
from lxml import html
import pandas as pd
import re
from datetime import datetime
from shapely.geometry import Point
import geopandas as gpd
from geopy.geocoders import GoogleV3
from geopy.distance import geodesic

state_initials = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

state_code_map = {
    "All States":"00","Alabama":"01","Alaska":"02","Arizona":"04","Arkansas":"05",
    "California":"06","Colorado":"08","Connecticut":"09","Delaware":"10",
    "District of Columbia":"11","Florida":"12","Georgia":"13","Hawaii":"15",
    "Idaho":"16","Illinois":"17","Indiana":"18","Iowa":"19","Kansas":"20",
    "Kentucky":"21","Louisiana":"22","Maine":"23","Maryland":"24","Massachusetts":"25",
    "Michigan":"26","Minnesota":"27","Mississippi":"28","Missouri":"29","Montana":"30",
    "Nebraska":"31","Nevada":"32","New Hampshire":"33","New Jersey":"34","New Mexico":"35",
    "New York":"36","North Carolina":"37","North Dakota":"38","Ohio":"39","Oklahoma":"40",
    "Oregon":"41","Pennsylvania":"42","Rhode Island":"44","South Carolina":"45",
    "South Dakota":"46","Tennessee":"47","Texas":"48","Utah":"49","Vermont":"50",
    "Virginia":"51","Washington":"53","West Virginia":"54","Wisconsin":"55",
    "Wyoming":"56","Puerto Rico":"72","Virgin Islands":"78","All Metropolitan Statistical Areas":"99"
}
    
# Function to scrape job data from city-data.com
def scrape_city_data(url, fields):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}: {response.status_code}")
        return None

    tree = html.fromstring(response.content)
    
    data = {}
    
    for field_name, field_xpath in fields.items():
        elements = tree.xpath(field_xpath)
        if elements:
            element_text = get_first_num_from_arr(elements[0].split(' '))
            # Extract the percentage value
            match = re.search(r'(\d+(\.\d+)?)%', element_text)
            if match:
                value = element_text
            else:
                # Handle other types of values (e.g., integer values)
                try:
                    value = int(element_text)
                except ValueError:
                    value = element_text
            data[field_name] = value
        else:
            print(f"Failed to find the text '{field_name}' in {url}.")
            data[field_name] = None

    return data

def get_first_num_from_arr(text_arr):
    for num_string in text_arr:
        cleaned_int = clean_int(num_string)
        if cleaned_int != '':
            return cleaned_int

def clean_int(number_string):
    return number_string.strip(' ').replace(',', '').strip('(').strip(')').strip('+').strip('$')

# Function to scrape job data from the BLS website
def scrape_bls_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}: {response.status_code}")
        return None

    tree = html.fromstring(response.content)
    
    # Extract the data for the most recent month and the same month in the previous year
    values = tree.xpath('//*[@id="table0"]/tbody/tr/td[1]/text()')

    if not values:
        print(f"Failed to extract job data from {url}")
        return None

    try:
        most_recent_value = float(values[-1].replace(',', ''))
        previous_year_value = float(values[-2].replace(',', ''))

        return {
            'most_recent_value': most_recent_value,
            'previous_year_value': previous_year_value
        }
    except Exception as e:
        print(f"Error parsing job data: {e}")
        return None

# Function to construct the BLS URL from series components: https://www.bls.gov/help/hlpforma.htm#SM
def construct_bls_url(state, area_code):
    series_id = f"SMU{state_code_map[state]}{area_code}0000000001"
    bls_url = f"https://data.bls.gov/timeseries/{series_id}"
    return bls_url

"""
UNCOMMENT IF WE NEED TO RE-GENERATE area_data.json
"""

# area_code_df = pd.DataFrame({
#     "area_code": ["10180", "10380", "10420", "10500", "10540", "10580", "10740", "10780", "10900", "11020", "11100", "11180", "11244", "11260", "11460", "11500", "11540", "11640", "11700", "12020", "12060", "12100", "12220", "12260", "12420", "12540", "12580", "12940", "12980", "13020", "13140", "13220", "13380", "13460", "13740", "13780", "13820", "13900", "13980", "14010", "14020", "14100", "14260", "14500", "14540", "14740", "15180", "15260", "15380", "15500", "15680", "15804", "15940", "15980", "16020", "16060", "16180", "16220", "16300", "16540", "16580", "16620", "16700", "16740", "16820", "16860", "16940", "16974", "16980", "17020", "17140", "17300", "17420", "17460", "17660", "17780", "17820", "17860", "17900", "17980", "18020", "18140", "18580", "18700", "18880", "19060", "19100", "19124", "19140", "19180", "19300", "19340", "19380", "19460", "19500", "19660", "19740", "19780", "19804", "19820", "20020", "20100", "20220", "20260", "20500", "20524", "20700", "20740", "20940", "20994", "21060", "21140", "21300", "21340", "21420", "21500", "21660", "21780", "21820", "22020", "22140", "22180", "22220", "22380", "22420", "22500", "22520", "22540", "22660", "22744", "22900", "23060", "23104", "23420", "23460", "23540", "23580", "23844", "23900", "24020", "24140", "24220", "24260", "24300", "24340", "24420", "24500", "24540", "24580", "24660", "24780", "24860", "25020", "25060", "25180", "25220", "25260", "25420", "25500", "25620", "25860", "25940", "25980", "26140", "26300", "26380", "26420", "26580", "26620", "26820", "26900", "26980", "27060", "27100", "27140", "27180", "27260", "27340", "27500", "27620", "27740", "27780", "27860", "27900", "27980", "28020", "28100", "28140", "28420", "28660", "28700", "28740", "28940", "29020", "29100", "29180", "29200", "29340", "29404", "29420", "29460", "29540", "29620", "29700", "29740", "29820", "29940", "30020", "30140", "30300", "30460", "30620", "30700", "30780", "30860", "30980", "31020", "31080", "31084", "31140", "31180", "31340", "31420", "31460", "31540", "31740", "31860", "31900", "32420", "32580", "32780", "32820", "32900", "33100", "33124", "33140", "33220", "33260", "33340", "33460", "33540", "33660", "33700", "33740", "33780", "33860", "33874", "34060", "34100", "34580", "34620", "34740", "34820", "34900", "34940", "34980", "35004", "35084", "35100", "35380", "35614", "35620", "35660", "35840", "36084", "36100", "36140", "36220", "36260", "36420", "36500", "36540", "36740", "36780", "36980", "37100", "37340", "37460", "37620", "37860", "37900", "37964", "37980", "38060", "38220", "38300", "38540", "38660", "38900", "38940", "39140", "39340", "39380", "39460", "39540", "39580", "39660", "39740", "39820", "39900", "40060", "40140", "40220", "40340", "40380", "40420", "40580", "40660", "40900", "40980", "41060", "41100", "41140", "41180", "41420", "41500", "41540", "41620", "41660", "41700", "41740", "41860", "41884", "41900", "41940", "41980", "42020", "42034", "42100", "42140", "42200", "42220", "42340", "42540", "42644", "42660", "42680", "42700", "43100", "43300", "43340", "43420", "43524", "43580", "43620", "43780", "43900", "44060", "44100", "44180", "44220", "44300", "44420", "44700", "44940", "45060", "45104", "45220", "45300", "45460", "45500", "45540", "45780", "45820", "45940", "46060", "46140", "46220", "46300", "46340", "46520", "46540", "46660", "46700", "47020", "47220", "47260", "47300", "47380", "47460", "47580", "47664", "47894", "47900", "47940", "48060", "48140", "48260", "48300", "48424", "48540", "48620", "48660", "48700", "48864", "48900", "49020", "49180", "49420", "49620", "49660", "49700", "49740", "70750", "70900", "71650", "71654", "71950", "72104", "72400", "72850", "73050", "73104", "73450", "73604", "74204", "74500", "74650", "74804", "74854", "74950", "75404", "75550", "75700", "76450", "76524", "76600", "76750", "76900", "77200", "78100", "78254", "78700", "79600", "92581", "92811", "92812", "93561", "93562", "93563", "93565", "94781", "94783", "97961", "97962"],
#     "area_name": ["Abilene, TX", "Aguadilla-Isabela, PR", "Akron, OH", "Albany, GA", "Albany, OR", "Albany-Schenectady-Troy, NY", "Albuquerque, NM", "Alexandria, LA", "Allentown-Bethlehem-Easton, PA-NJ", "Altoona, PA", "Amarillo, TX", "Ames, IA", "Anaheim-Santa Ana-Irvine, CA", "Anchorage, AK", "Ann Arbor, MI", "Anniston-Oxford-Jacksonville, AL", "Appleton, WI", "Arecibo, PR", "Asheville, NC", "Athens-Clarke County, GA", "Atlanta-Sandy Springs-Roswell, GA", "Atlantic City-Hammonton, NJ", "Auburn-Opelika, AL", "Augusta-Richmond County, GA-SC", "Austin-Round Rock, TX", "Bakersfield, CA", "Baltimore-Columbia-Towson, MD", "Baton Rouge, LA", "Battle Creek, MI", "Bay City, MI", "Beaumont-Port Arthur, TX", "Beckley, WV", "Bellingham, WA", "Bend-Redmond, OR", "Billings, MT", "Binghamton, NY", "Birmingham-Hoover, AL", "Bismarck, ND", "Blacksburg-Christiansburg-Radford, VA", "Bloomington, IL", "Bloomington, IN", "Bloomsburg-Berwick, PA", "Boise City, ID", "Boulder, CO", "Bowling Green, KY", "Bremerton-Silverdale, WA", "Brownsville-Harlingen, TX", "Brunswick, GA", "Buffalo-Cheektowaga-Niagara Falls, NY", "Burlington, NC", "California-Lexington Park, MD", "Camden, NJ", "Canton-Massillon, OH", "Cape Coral-Fort Myers, FL", "Cape Girardeau, MO-IL", "Carbondale-Marion, IL", "Carson City, NV", "Casper, WY", "Cedar Rapids, IA", "Chambersburg-Waynesboro, PA", "Champaign-Urbana, IL", "Charleston, WV", "Charleston-North Charleston, SC", "Charlotte-Concord-Gastonia, NC-SC", "Charlottesville, VA", "Chattanooga, TN-GA", "Cheyenne, WY", "Chicago-Naperville-Arlington Heights, IL", "Chicago-Naperville-Elgin, IL-IN-WI", "Chico, CA", "Cincinnati, OH-KY-IN", "Clarksville, TN-KY", "Cleveland, TN", "Cleveland-Elyria, OH", "Coeur d'Alene, ID", "College Station-Bryan, TX", "Colorado Springs, CO", "Columbia, MO", "Columbia, SC", "Columbus, GA-AL", "Columbus, IN", "Columbus, OH", "Corpus Christi, TX", "Corvallis, OR", "Crestview-Fort Walton Beach-Destin, FL", "Cumberland, MD-WV", "Dallas-Fort Worth-Arlington, TX", "Dallas-Plano-Irving, TX", "Dalton, GA", "Danville, IL", "Daphne-Fairhope-Foley, AL", "Davenport-Moline-Rock Island, IA-IL", "Dayton, OH", "Decatur, AL", "Decatur, IL", "Deltona-Daytona Beach-Ormond Beach, FL", "Denver-Aurora-Lakewood, CO", "Des Moines-West Des Moines, IA", "Detroit-Dearborn-Livonia, MI", "Detroit-Warren-Dearborn, MI", "Dothan, AL", "Dover, DE", "Dubuque, IA", "Duluth, MN-WI", "Durham-Chapel Hill, NC", "Dutchess County-Putnam County, NY", "East Stroudsburg, PA", "Eau Claire, WI", "El Centro, CA", "Elgin, IL", "Elizabethtown-Fort Knox, KY", "Elkhart-Goshen, IN", "Elmira, NY", "El Paso, TX", "Enid, OK", "Erie, PA", "Eugene, OR", "Evansville, IN-KY", "Fairbanks, AK", "Fargo, ND-MN", "Farmington, NM", "Fayetteville, NC", "Fayetteville-Springdale-Rogers, AR-MO", "Flagstaff, AZ", "Flint, MI", "Florence, SC", "Florence-Muscle Shoals, AL", "Fond du Lac, WI", "Fort Collins, CO", "Fort Lauderdale-Pompano Beach-Deerfield Beach, FL Metropolitan", "Fort Smith, AR-OK", "Fort Wayne, IN", "Fort Worth-Arlington, TX", "Fresno, CA", "Gadsden, AL", "Gainesville, FL", "Gainesville, GA", "Gary, IN", "Gettysburg, PA", "Glens Falls, NY", "Goldsboro, NC", "Grand Forks, ND-MN", "Grand Island, NE", "Grand Junction, CO", "Grand Rapids-Wyoming, MI", "Grants Pass, OR", "Great Falls, MT", "Greeley, CO", "Green Bay, WI", "Greensboro-High Point, NC", "Greenville, NC", "Greenville-Anderson-Mauldin, SC", "Guayama, PR", "Gulfport-Biloxi-Pascagoula, MS", "Hagerstown-Martinsburg, MD-WV", "Hammond, LA", "Hanford-Corcoran, CA", "Harrisburg-Carlisle, PA", "Harrisonburg, VA", "Hattiesburg, MS", "Hickory-Lenoir-Morganton, NC", "Hilton Head Island-Bluffton-Beaufort, SC", "Hinesville, GA", "Homosassa Springs, FL", "Hot Springs, AR", "Houma-Thibodaux, LA", "Houston-The Woodlands-Sugar Land, TX", "Huntington-Ashland, WV-KY-OH", "Huntsville, AL", "Idaho Falls, ID", "Indianapolis-Carmel-Anderson, IN", "Iowa City, IA", "Ithaca, NY", "Jackson, MI", "Jackson, MS", "Jackson, TN", "Jacksonville, FL", "Jacksonville, NC", "Janesville-Beloit, WI", "Jefferson City, MO", "Johnson City, TN", "Johnstown, PA", "Jonesboro, AR", "Joplin, MO", "Kahului-Wailuku-Lahaina, HI", "Kalamazoo-Portage, MI", "Kankakee, IL", "Kansas City, MO-KS", "Kennewick-Richland, WA", "Killeen-Temple, TX", "Kingsport-Bristol-Bristol, TN-VA", "Kingston, NY", "Knoxville, TN", "Kokomo, IN", "La Crosse-Onalaska, WI-MN", "Lafayette, LA", "Lafayette-West Lafayette, IN", "Lake Charles, LA", "Lake County-Kenosha County, IL-WI", "Lake Havasu City-Kingman, AZ", "Lakeland-Winter Haven, FL", "Lancaster, PA", "Lansing-East Lansing, MI", "Laredo, TX", "Las Cruces, NM", "Las Vegas-Henderson-Paradise, NV", "Lawrence, KS", "Lawton, OK", "Lebanon, PA", "Lewiston, ID-WA", "Lexington-Fayette, KY", "Lima, OH", "Lincoln, NE", "Little Rock-North Little Rock-Conway, AR", "Logan, UT-ID", "Longview, TX", "Longview, WA", "Los Angeles-Long Beach-Anaheim, CA", "Los Angeles-Long Beach-Glendale, CA", "Louisville/Jefferson County, KY-IN", "Lubbock, TX", "Lynchburg, VA", "Macon-Bibb County, GA", "Madera, CA", "Madison, WI", "Manhattan, KS", "Mankato-North Mankato, MN", "Mansfield, OH", "Mayaguez, PR", "McAllen-Edinburg-Mission, TX", "Medford, OR", "Memphis, TN-MS-AR", "Merced, CA", "Miami-Fort Lauderdale-West Palm Beach, FL", "Miami-Miami Beach-Kendall, FL", "Michigan City-La Porte, IN", "Midland, MI", "Midland, TX", "Milwaukee-Waukesha-West Allis, WI", "Minneapolis-St. Paul-Bloomington, MN-WI", "Missoula, MT", "Mobile, AL", "Modesto, CA", "Monroe, LA", "Monroe, MI", "Montgomery, AL", "Montgomery County-Bucks County-Chester County, PA Metropolitan", "Morgantown, WV", "Morristown, TN", "Mount Vernon-Anacortes, WA", "Muncie, IN", "Muskegon, MI", "Myrtle Beach-Conway-North Myrtle Beach, SC-NC", "Napa, CA", "Naples-Immokalee-Marco Island, FL", "Nashville-Davidson--Murfreesboro--Franklin, TN", "Nassau County-Suffolk County, NY", "Newark, NJ-PA", "New Bern, NC", "New Orleans-Metairie, LA", "New York-Jersey City-White Plains, NY-NJ", "New York-Newark-Jersey City, NY-NJ-PA", "Niles-Benton Harbor, MI", "North Port-Sarasota-Bradenton, FL", "Oakland-Hayward-Berkeley, CA", "Ocala, FL", "Ocean City, NJ", "Odessa, TX", "Ogden-Clearfield, UT", "Oklahoma City, OK", "Olympia-Tumwater, WA", "Omaha-Council Bluffs, NE-IA", "Orlando-Kissimmee-Sanford, FL", "Oshkosh-Neenah, WI", "Owensboro, KY", "Oxnard-Thousand Oaks-Ventura, CA", "Palm Bay-Melbourne-Titusville, FL", "Panama City, FL", "Parkersburg-Vienna, WV", "Pensacola-Ferry Pass-Brent, FL", "Peoria, IL", "Philadelphia, PA", "Philadelphia-Camden-Wilmington, PA-NJ-DE-MD", "Phoenix-Mesa-Scottsdale, AZ", "Pine Bluff, AR", "Pittsburgh, PA", "Pocatello, ID", "Ponce, PR", "Portland-Vancouver-Hillsboro, OR-WA", "Port St. Lucie, FL", "Prescott, AZ", "Provo-Orem, UT", "Pueblo, CO", "Punta Gorda, FL", "Racine, WI", "Raleigh, NC", "Rapid City, SD", "Reading, PA", "Redding, CA", "Reno, NV", "Richmond, VA", "Riverside-San Bernardino-Ontario, CA", "Roanoke, VA", "Rochester, MN", "Rochester, NY", "Rockford, IL", "Rocky Mount, NC", "Rome, GA", "Sacramento--Roseville--Arden-Arcade, CA", "Saginaw, MI", "St. Cloud, MN", "St. George, UT", "St. Joseph, MO-KS", "St. Louis, MO-IL", "Salem, OR", "Salinas, CA", "Salisbury, MD-DE", "Salt Lake City, UT", "San Angelo, TX", "San Antonio-New Braunfels, TX", "San Diego-Carlsbad, CA", "San Francisco-Oakland-Hayward, CA", "San Francisco-Redwood City-South San Francisco, CA Metropolitan", "San German, PR", "San Jose-Sunnyvale-Santa Clara, CA", "San Juan-Carolina-Caguas, PR", "San Luis Obispo-Paso Robles-Arroyo Grande, CA", "San Rafael, CA", "Santa Cruz-Watsonville, CA", "Santa Fe, NM", "Santa Maria-Santa Barbara, CA", "Santa Rosa, CA", "Savannah, GA", "Scranton--Wilkes-Barre--Hazleton, PA", "Seattle-Bellevue-Everett, WA", "Seattle-Tacoma-Bellevue, WA", "Sebastian-Vero Beach, FL", "Sebring, FL", "Sheboygan, WI", "Sherman-Denison, TX", "Shreveport-Bossier City, LA", "Sierra Vista-Douglas, AZ", "Silver Spring-Frederick-Rockville, MD", "Sioux City, IA-NE-SD", "Sioux Falls, SD", "South Bend-Mishawaka, IN-MI", "Spartanburg, SC", "Spokane-Spokane Valley, WA", "Springfield, IL", "Springfield, MO", "Springfield, OH", "State College, PA", "Staunton-Waynesboro, VA", "Stockton-Lodi, CA", "Sumter, SC", "Syracuse, NY", "Tacoma-Lakewood, WA", "Tallahassee, FL", "Tampa-St. Petersburg-Clearwater, FL", "Terre Haute, IN", "Texarkana, TX-AR", "The Villages, FL", "Toledo, OH", "Topeka, KS", "Trenton, NJ", "Tucson, AZ", "Tulsa, OK", "Tuscaloosa, AL", "Twin Falls, ID", "Tyler, TX", "Urban Honolulu, HI", "Utica-Rome, NY", "Valdosta, GA", "Vallejo-Fairfield, CA", "Victoria, TX", "Vineland-Bridgeton, NJ", "Virginia Beach-Norfolk-Newport News, VA-NC", "Visalia-Porterville, CA", "Waco, TX", "Walla Walla, WA", "Warner Robins, GA", "Warren-Troy-Farmington Hills, MI", "Washington-Arlington-Alexandria, DC-VA-MD-WV Metropolitan Divis", "Washington-Arlington-Alexandria, DC-VA-MD-WV", "Waterloo-Cedar Falls, IA", "Watertown-Fort Drum, NY", "Wausau, WI", "Weirton-Steubenville, WV-OH", "Wenatchee, WA", "West Palm Beach-Boca Raton-Delray Beach, FL Metropolitan Divisi", "Wheeling, WV-OH", "Wichita, KS", "Wichita Falls, TX", "Williamsport, PA", "Wilmington, DE-MD-NJ", "Wilmington, NC", "Winchester, VA-WV", "Winston-Salem, NC", "Yakima, WA", "York-Hanover, PA", "Youngstown-Warren-Boardman, OH-PA", "Yuba City, CA", "Yuma, AZ", "Bangor, ME", "Barnstable Town, MA", "Boston-Cambridge-Nashua, MA-NH", "Boston-Cambridge-Newton, MA", "Bridgeport-Stamford-Norwalk, CT", "Brockton-Bridgewater-Easton, MA", "Burlington-South Burlington, VT", "Danbury, CT", "Dover-Durham, NH-ME", "Framingham, MA", "Hartford-West Hartford-East Hartford, CT", "Haverhill-Newburyport-Amesbury Town, MA-NH", "Lawrence-Methuen Town-Salem, MA-NH", "Leominster-Gardner, MA", "Lewiston-Auburn, ME", "Lowell-Billerica-Chelmsford, MA-NH", "Lynn-Saugus-Marblehead, MA", "Manchester, NH", "Nashua, NH-MA", "New Bedford, MA", "New Haven, CT", "Norwich-New London-Westerly, CT-RI", "Peabody-Salem-Beverly, MA", "Pittsfield, MA", "Portland-South Portland, ME", "Portsmouth, NH-ME", "Providence-Warwick, RI-MA", "Springfield, MA-CT", "Taunton-Middleborough-Norton, MA", "Waterbury, CT", "Worcester, MA-CT", "Baltimore City, MD", "Kansas City, MO", "Kansas City, KS", "New York City, NY", "Orange-Rockland-Westchester, NY", "Bergen-Hudson-Passaic, NJ", "Middlesex-Monmouth-Ocean, NJ", "Calvert-Charles-Prince George's, MD", "Northern Virginia, VA", "Philadelphia City, PA", "Delaware County, PA"]
# })

# for i in area_code_df.index:
#     area = area_code_df.loc[i, "area_name"]
#     area_code = area_code_df.loc[i, "area_code"]
    
#     # If the city is not in the cached data, fetch its coordinates
#     if area not in area_data:
#         # Add the city, area code, and coordinates to the dictionary
#         area_data[area] = {
#             "area_code": area_code,
#             "coordinates": get_area_coordinates(area)
#         }
    
#     # Get the coordinates from the cache
#     coordinates = area_data[area]['coordinates']

# # Save the data to a JSON file
# with open("area_data.json", "w") as json_file:
#     json.dump(area_data, json_file, indent=4)

# Create a dictionary to cache city coordinates
# ADD YOUR OWN API KEY HERE
geolocator = GoogleV3(api_key='')

with open("area_data.json", "r") as json_file:
    area_data = json.load(json_file)

with open("city_data.json", "r") as json_file:
    city_data = json.load(json_file)

def get_city_coordinates(city_name):
    if city_name in city_data:
        return city_data[city_name]['coordinates']
    else:
        location = geolocator.geocode(city_name)
        if location:
            coordinates = (location.latitude, location.longitude)
            city_data[city_name] = {
                "coordinates": coordinates
            }
            with open("city_data.json", "w") as json_file:
                json.dump(city_data, json_file, indent=4)
            return coordinates
        else:
            return None

def get_area_coordinates(area_name):
    if area_name in area_data:
        return area_data[area_name]['coordinates']
    else:
        print ("Missing area name, uncomment the code below to generate coordinates for: " + area_name)
        # area codes should have all been pre-generated, but uncomment below if needed
        # location = geolocator.geocode(area_name) 
        # if location:
        #     coordinates = (location.latitude, location.longitude)
        #     return coordinates
        # else:
        #     return None

def find_closest_metro_area(target_city_name):
    target_coords = get_city_coordinates(target_city_name)
    if not target_coords:
        return None

    closest_metro_area = None
    min_distance = float('inf')

    for area_name in area_data:
        metro_area_coords = get_area_coordinates(area_name)
        if metro_area_coords:
            distance = geodesic(target_coords, metro_area_coords).kilometers
            if distance < min_distance:
                min_distance = distance
                closest_metro_area = area_name

    return closest_metro_area

# Function to save data to a spreadsheet
def save_to_spreadsheet(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

def calculate_job_growth(most_recent_value, previous_year_value):
    if previous_year_value == 0:
        return None
    return ((most_recent_value - previous_year_value) / previous_year_value)

def scrape_cities(url, state, min_population):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}: {response.status_code}")
        return None

    tree = html.fromstring(response.content)
    cities = {}

    # Find the table with city data
    table_rows = tree.xpath("//table[contains(@class, 'tabBlue')]/tbody/tr")
    for row in table_rows:
        cells = row.xpath("td")
        if len(cells) >= 3:
            city_name = cells[1].text_content().replace(f', {state_initials[state]}', '').strip()
            population_text = cells[2].text_content().strip()
            try:
                population = int(population_text.replace(",", ""))
                if population > min_population:
                    cities[city_name] = population
            except ValueError:
                pass

    return cities

# Main function
def main():
    base_url_city = 'https://www.city-data.com/city/'

    city_fields = {
        'Population in 2022': '//*[@id="city-population"]/b[1]/following-sibling::text()[1]',
        'Population change since 2000 (%)': '//*[@id="city-population"]/b[2]/following-sibling::text()[1]',
        'Median household income in 2022': '//*[@id="median-income"]/b[1]/following-sibling::text()[1]',
        'Median household income in 2000': '//*[@id="median-income"]/b[2]/following-sibling::text()[1]',
        'Median condo value in 2022': '//*[@id="median-income"]/b[7]/following-sibling::text()[1]',
        'Median condo value in 2000': '//*[@id="median-income"]/b[8]/following-sibling::text()[1]',
        'Median contract rent': '//*[@id="median-rent"]/p/text()',
        'Poverty percentage': '//*[@id="poverty-level"]/b[1]/following-sibling::text()[1]',
        'Largest ethnicity percentage': '//*[@id="races-graph"]/div/ul/li[2]/ul/li[1]/span[2]/text()',
        'Largest ethnicity slice': '//*[@id="races-graph"]/div/ul/li[2]/ul/li[1]/b/text()',
        'Most recent crime index': '//*[@id="crimeTab"]/tfoot/tr/td[last()]//text()',
        'Unemployment rate': '//*[@id="unemployment"]/div[1]/table/tr[1]/td[2]/text()'
    }

    STATES_TO_ANALYZE = {
        'North Carolina', 'Alabama', 'Georgia'
    }

    # Specify the minimum population for inclusion
    MIN_POPULATION = 50000
    for state in STATES_TO_ANALYZE:            
        url = f'https://www.city-data.com/city/{state.replace(' ', '-')}.html'
        cities_data = scrape_cities(url, state, MIN_POPULATION)

        # Setup headers
        data = {
            'City': [],
            'Closest Metro Area': []
        }

        for field in city_fields.keys():
            data[field] = []

        data['Job Growth (%)'] = []

        # Save the data to a JSON file
        with open(f"{state.replace(' ', '').lower()}_cities_population.json", "w") as outfile:
            json.dump(cities_data, outfile, indent=4)
        
        with open(f"{state.replace(' ', '').lower()}_cities_population.json", "r") as json_file:
            cities_to_analyze = json.load(json_file)
        
        for city in cities_to_analyze:
            print(f"Scraping {city}, {state}")
            url_city = f'{base_url_city}{city.replace(' ', '-').replace('\'', '')}-{state.replace(' ', '-')}.html'
            city_data = scrape_city_data(url_city, city_fields)
            if city_data:
                data['City'].append(city.replace('-', ', '))
                for field, value in city_data.items():
                    data[field].append(value)
            
                # Scrape job data and calculate job growth for each city
                closest_metro_area = find_closest_metro_area(f"{city}, {state_initials[state]}")
                if closest_metro_area:
                    bls_url = construct_bls_url(state, area_data[closest_metro_area]['area_code'])
                    job_data = scrape_bls_data(bls_url)
                    if job_data:
                        job_growth = calculate_job_growth(job_data['most_recent_value'], job_data['previous_year_value'])
                        data['Job Growth (%)'].append(job_growth)
                        data['Closest Metro Area'].append(closest_metro_area)
                    else:
                        data['Job Growth (%)'].append(None)
                        data['Closest Metro Area'].append(None)
                else:
                    data['Job Growth (%)'].append(None)
                    data['Closest Metro Area'].append(None)

        if data['City']:
            print(f"Scraping complete for state of {state}")
            filename = f'scraped_population_and_job_data_{state.replace(' ', '').lower()}.xlsx'
            save_to_spreadsheet(data, filename)

    print("Scraping complete for all states")


if __name__ == "__main__":
    main()