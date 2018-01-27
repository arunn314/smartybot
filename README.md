# smartybot
Raspberry Pi based Chat bot for home automation.

# Supported Features
adt_handler.py - Scrap ADT site to control ADT security system.<br>
camera.py - Class to take snapshots, live stream video using Raspberry pi Camera.<br>
gdrive_handler.py - Upload, delete files to/from Google Drive.<br>
gmail_handler.py - Read new emails, search emails.<br>
gmaps_handler.py - Get traffic updates for given destination using Google Maps.<br>
life360_handler.py - Scrap life360 website to track location of users.<br>
plaid_handler.py - Track transactions done using credit card, debit card.<br>
plug_handler.py - Control TP-Link plug to on/off.<br>
stock_handler.py - Pull Stock updates.<br>
weather_handler.py - Get Weather updates for any city.<br>
wiki_handler.py - Search and provide summary of Wiki articles.<br>

# Chat Bot Scripts
server.py - Flask Server to handle requests from FB Messenger.<br>
queryparser.py - Parse Natural Language queries to extract intent and entities.<br>
processor.py - Delegate to appropriate handlers based on intent and entities.<br>


config.py - Config file to put credentials, API keys, Access tokens.<br>
utils.py - Utilities script for sending FB messages, images, and output to speaker.<br>

# Monitor Scripts
location_server.py - Track users' location every minute and send FB messenger when they reach home, office.<br>
expenses_server.py - Pull Transactions periodically and send weekly/monthly updates in a Pie Chart, Send alerts when expenses exceed weekly budget for a category.<br>
updates_notifier.py - Send daily updates about emails, weather, traffic, security monitoring, Switch on/off lights while outside.<br>
