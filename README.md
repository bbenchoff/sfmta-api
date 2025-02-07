# sfmta-api

These are a few experiments and data collection expeditions with the dataset found at [511.org](https://511.org/). Specifically, I was looking at geotagged route and stop information for all public transit run by the SFMTA -- every bus stop, every cable car stop, and every subway stop. This was all in support of my [multi-stop bus tracker](https://bbenchoff.github.io/pages/BusTideDisplay.html) project.

## What this data is

* **stops.xml** is a list of every bus stop in San Francisco. It's literally every bus stop, lat/long, and a description of the stop (basically the street intersection, e.x. Geary and Masonic).
* **lines.xml** is just a list of all the bus/train/cable car routes. There's no stop data in there, this is just a list of routes. Did you know the [714 bus exists?](https://www.sfmta.com/routes/714-bart-early-bird). It runs one hour per day on weekdays, 4am to 5am. This data was used to answer the question of what lines should I make graphics for in my multi-stop bus tracker.
* **Routes** in the /Routes folder in this repo contains a JSON file for every individual route the SFMTA runs. This gives you each stop on that route along with whether it's running inbound or outbound (or the terminus it's heading to when it stops at that route).

There are various scripts that use this data. One output of these scripts is stops_routes_data.csv, a file which gives stop number, a description of that stop (Market & 3rd, for example), and the number of routes that use that stop. This gives you the busiest stops in the system, which are all on Market from 3rd to the Embarcadero.

## Building the thing I needed

For the Multi-stop bus tracker to be useful, I need a way to look up bus stops on a map and get the lines serving that stop, along with the terminus from that stop. To build this, I combined the data from the stops.xml, lines.xml, and the various route JSON files. This was plotted on an interactive map:

![showing what the map looks like](/Docu/screenshot.png)

Clicking on any of the points on this map shows the stop name, stop ID, and what lines are served by this stop. It's what you need if you want a visual map to determine what stop IDs to use when programming the Multi-stop bus tracker.


