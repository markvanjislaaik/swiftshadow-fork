from swiftshadow.constants import country_codes
import requests
from requests.exceptions import Timeout
from datetime import datetime
import logging

import re

IP_ADDRESS_REGEX = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

logger = logging.getLogger(__name__)



class FailedRequestException(Exception):
    pass

class InvalidProxyException(Exception):
    pass


def get_country_code(country_name):
    country_code = country_codes.get(country_name)
    if country_code:
        return country_code
    
    for name in country_codes.keys():
        if country_name in name:
            return country_codes[name]
        else:
            raise ValueError(f"Country {country_name} not found in country_codes")


def validate_proxy(proxy, countries):
    if countries:
        if proxy[-1].upper() not in countries:
            return False
    proxy_dict = {proxy[1]: proxy[0]}

    try:
        resp = requests.get(f"{proxy[1]}://ipinfo.io/ip", proxies=proxy_dict, timeout=5).text
        logger.debug(f"Proxy {proxy[0]} status: {resp.status_code}")
        if resp.status_code == 200:
            if IP_ADDRESS_REGEX.match(resp.text):
                return True
            else:
                raise InvalidProxyException(f"Invalid IP address returned: {resp.text}")
        else:
            raise FailedRequestException(f"Status code not 200, returned {resp.status_code}")
    except Timeout:
        logger.warning(f"Proxy {proxy[0]} timed out")
        return False
    except Exception as e:
        return False
