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
```javascript
{
    "BTC": {
        "price": 2597.87,
        "value": 264.98274,
        "volume": 0.102
    },
    "DOGE": {
        "price": 0.002573,
        "value": 25.665675,
        "volume": 9975.0
    },
 
    "totalvalue": 290.648415
}
// (Where volume is how much you own as defined in coinwatch.ini)
```
 

$ zappa deploy 

