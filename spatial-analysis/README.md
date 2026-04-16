This project takes as input a point layer (crs:4326) and queries the EFA API for public transport connections.
If the api response contains more than one connection the fastet one is choosen.

Basically, the script fetches all responses from the api and stores them in "trips" folder.
Consequentlly, the fastest trip from each origin is chosen and converted into a GEOJSON.
The final output is one GEOJSON file with the fastest connection from each origin to the destination. 

https://www.opendata-oepnv.de/ht/de/api

Python dependcies: pydantic, requests

Usage: 
- open Main.py and scroll down to main method.
- specify the input file with points in crs:4326, key = "fid"
- specify one destination by name and coordinates in crs:4326
- run the script
- output: geojson with fastest connection, key = "fid"


