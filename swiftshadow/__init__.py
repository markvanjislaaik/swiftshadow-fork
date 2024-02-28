from swiftshadow.providers import proxyscrape, scrapingant


def QuickProxy(countries: list = [], protocol: str = "http"):
    """
    This function is a faster alternative to `Proxy` class.
    No caching is done.

    Args:
     countries: ISO 3166-2 Two letter country codes to filter proxies.
     protocol: HTTP/HTTPS protocol to filter proxies.

    Returns:
                    proxyObject (dict): A working proxy object.
    """
    try:
        return proxyscrape(1, countries=countries, protocol=protocol)[0]
    except:
        return scrapingant(1, countries=countries, protocol=protocol)[0]
