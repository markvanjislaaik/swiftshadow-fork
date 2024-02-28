from requests import get
from random import choice
import json
from swiftshadow.providers import proxyscrape, scrapingant, Providers
import swiftshadow.cache as cache
import os

import logging

logger = logging.getLogger(__name__)


class Proxy:
    def __init__(
        self,
        countries: list = [],
        protocol: str = "http",
        max_proxies: int = 10,
        auto_rotate: bool = False,
        cache_period: int = 10,
        cache_folder: str = "",
    ):
        """
        The one class for everything.

        Proxy class contains all necessary methods required to use swiftshadow.

        Args:
                countries: ISO 3166-2 Two letter country codes to filter proxies.
                protocol: HTTP/HTTPS protocol to filter proxies.
                max_proxies: Maximum number of proxies to store and rotate from.
                auto_rotate: Rotates proxy when `Proxy.proxy()` function is called.
                cache_period: Time to cache proxies in minutes.
                cache_folder: Folder to store cache file.

        Returns:
                proxyClass (swiftshadow.Proxy): `swiftshadow.Proxy` class instance

        Examples:
                Simplest way to get a proxy
                >>> from swiftshadow.swiftshadow import Proxy
                >>> swift = Proxy()
                >>> print(swift.proxy())
                {'http':'192.0.0.1:8080'}
        Note:
                Proxies are sourced from **Proxyscrape** and **Scrapingant** websites which are freely available and validated locally.
        """
        self.countries = [i.upper() for i in countries]
        self.protocol = protocol
        self.max_proxies = max_proxies
        self.auto_rotate = auto_rotate
        self.cache_period = cache_period
        if cache_folder != "":
            self.cache_file_path = ".swiftshadow.json"
        else:
            self.cache_file_path = f"{cache_folder}/.swiftshadow.json"

        self.update()

    def validate(self, ip, cc, protocol):
        if (ip[1] == cc or cc is None) and ip[2] == protocol:
            proxy = {ip[2]: ip[0]}
            try:
                oip = get(f"{protocol}://ipinfo.io/ip", proxies=proxy).text
            except:
                return False
            if oip.count(".") == 3 and oip != self.mip:
                return True
            else:
                return False
        return False

    def update(self):
        try:
            with open(self.cache_file_path, "r") as file:
                data = json.load(file)
                self.expiry = data[0]
                expired = cache.check_expiry(self.expiry)
            if not expired:
                logger.info("Loaded proxies from cache")
                self.proxies = data[1]
                self.expiry = data[0]
                self.current = self.proxies[0]
                return
            else:
                logger.info("Cache expired. Updating cache...")
        except FileNotFoundError:
            logger.error("No cache found. Cache will be created after update")

        self.proxies = []
        self.proxies.extend(proxyscrape(self.max_proxies, self.countries, self.protocol))
        if len(self.proxies) != self.max_proxies:
            self.proxies.extend(
                scrapingant(self.max_proxies, self.countries, self.protocol)
            )
        if len(self.proxies) == 0:
            # TODO: Investigate why this would cause a runtime error and fix that at source, rather than logging an error about it
            # log(
            #     "warning",
            #     "No proxies found for current settings. To prevent runtime error updating the proxy list again.",
            # )
            logger.warning("No proxies found for current settings. Updating again...")
            self.update()
        with open(self.cache_file_path, "w") as file:
            self.expiry = cache.get_expiry(self.cache_period).isoformat()
            json.dump([self.expiry, self.proxies], file)
        self.current = self.proxies[0]

    def rotate(self):
        """
        Rotate the current proxy.

        Sets the current proxy to a random one from available proxies and also validates cache.

        Note:
                Function only for manual rotation. If `auto_rotate` is set to `True` then no need to call this function.
        """
        if cache.check_expiry(self.expiry):
            self.update()
        self.current = choice(self.proxies)

    def proxy(self):
        """
        Returns a proxy dict.

        Returns:
                proxyDict (dict):A proxy dict of format `{protocol:address}`
        """
        if cache.check_expiry(self.expiry):
            self.update()
        if self.auto_rotate == True:
            return choice(self.proxies)
        else:
            return self.current


class ProxyChains:
    def __init__(self, countries: list = [], protocol: str = "http", max_proxies: int = 10):
        self.countries = [i.upper() for i in countries]
        self.protocol = protocol
        self.max_proxies = max_proxies
        self.update()

    def update(self):
        proxies = []
        for provider in Providers:
            logger.info(f"Proxy Count: {len(proxies)}")
            if len(proxies) == self.max_proxies:
                break
            logger.info(f"{provider}")
            for proxyDict in provider(self.max_proxies, self.countries, self.protocol):
                proxyRaw = list(proxyDict.items())[0]
                proxy = f'{proxyRaw[0]} {proxyRaw[1].replace(":"," ")}'
                proxies.append(proxy)
        proxies = "\n".join(proxies)
        configFileName = "swiftshadow-proxychains.conf"
        config = f"random_chain\nchain_len=1\nproxy_dns\n[ProxyList]\n{proxies}"
        with open(configFileName, "w") as file:
            file.write(config)
        cmd = f"proxychains -f {os.path.abspath(configFileName)}"
        os.system(cmd)
