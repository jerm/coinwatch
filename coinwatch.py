#!/usr/bin/env python
""" Coinwatch - get and do stuff with cryptocoin price data """

import ConfigParser
import json
import logging
import pprint
import time

from datadog import initialize as doginitialize
from datadog import ThreadStats as dogThreadStats
import requests
from requests.exceptions import ConnectionError

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
DEBUG = False
formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "progname":' +
    ' "%(name)s", "loglevel": "%(levelname)s", "message":, "%(message)s"}')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
log.addHandler(ch)

Config = ConfigParser.ConfigParser()
Config.read("coinwatch.ini")

COINS_CONFIG = Config.items("coins")

try:
    HEALTHCHECK_URL = Config.get("healthcheck", "url")
except ConfigParser.NoOptionError:
    HEALTHCHECK_URL = None

try:
    DATADOG = Config.get("general", "use_datadog").lower()
except ConfigParser.NoOptionError:
    DATADOG = None

if DATADOG in ['true', 'yes', 'y', 'ja', 'si', 'word']:
    DATADOG = True
    try:
        datadog_stat_prefix = Config.get("datadog", "stat_prefix")
        dd_options = {
            'api_key': Config.get("datadog", "dd_api_key"),
            'app_key': Config.get("datadog", "dd_app_key"),
        }
        log.debug("using DataDog")
    except ConfigParser.NoOptionError:
        log.warn("use_datadog set to true, but problem loading datadog configs")
        DATADOG = None
    doginitialize(**dd_options)
    stats = dogThreadStats()
    stats.start()
else:
    DATADOG = None


def coindata_to_datadog(coindata, coinname):
    """ Send latest reading to datadog. Maybe create events on some critera
    """
    for statname in coindata.keys():
        dd_stat_name = "{}.{}.{}".format(datadog_stat_prefix, coinname, statname)
        stats.gauge(dd_stat_name, coindata[statname])
    log.debug("Sent {}: {} to Datadog".format(dd_stat_name, coindata[statname]))


def collect():
    """ Main action area for our collection program """

    coins_name_list = []
    coinsdict = {}
    for coin in COINS_CONFIG:
        coinsdict[coin[0].upper()] = {}
        coinsdict[coin[0].upper()]['volume'] = float(coin[1])
        coins_name_list.append(coin[0].upper())
    try:
        coin_exchange_url = "https://min-api.cryptocompare.com/data/pricemulti"
        request = requests.get(
            "{}?fsyms={}&tsyms=USD".format(coin_exchange_url, ','.join(coins_name_list)))
    except ConnectionError:
        log.error("Error talking to coin API")
        exit(2)
    if request.ok:
        coins_requestdata = request.json()
    else:
        log.error(request)
        exit(1)
    if DEBUG:
        pprint.pprint(coins_requestdata)

    coinsdict['totalvalue'] = 0
    for coinname in coins_requestdata.keys():
        coinsdict[coinname]['price'] = coins_requestdata[coinname]['USD']
        coinsdict[coinname]['value'] = (float(coins_requestdata[coinname]['USD']) *
                                        float(coinsdict[coinname]['volume']))
        coinsdict['totalvalue'] += coinsdict[coinname]['value']
        if DATADOG:
            coindata_to_datadog(coinsdict[coinname], coinname)
    if DATADOG:
        dd_stat_name = "{}.all.value".format(datadog_stat_prefix)
        stats.gauge(dd_stat_name, coinsdict['totalvalue'])
        stats.flush(time.time() + 10)
    if HEALTHCHECK_URL:
        requests.get(HEALTHCHECK_URL)
    return coinsdict


if __name__ == '__main__':
    """ create logger """

    log = logging.getLogger(__file__)
    log.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(Config.get("general", "logfile"))
    fh.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "progname":' +
        '"%(name)s", "loglevel": "%(levelname)s", "message":, "%(message)s"}')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    print json.dumps(collect(), sort_keys=True, indent=4)
