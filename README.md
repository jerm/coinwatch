# Description
Script to collect and report a list of cryptocurrency values and (optionally) send the data to datadog for history and graphing and alerting

# Datadog
I chose datadog because it has a great stat visualizing interface, can do alerting, and is free. 
Set up an account, an api and app key, put the values into the ini file, and datadog will graph things for you

# Installation

clone the repo

$ cd coinwatch

$ pip install --user -r requirements.txt

# There are many config files like these, but these are yours.
$ for i in coinwatch.ini zappa_settings.json; do cp $i.example $i; done

# Edit configs
Fill-in your coin symbols and owned amounts.

# Usage

$ python coinwatch.py

$ zappa deploy 

