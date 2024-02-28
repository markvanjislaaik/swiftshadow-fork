import requests
from requests.exceptions import Timeout
from swiftshadow.helpers import get_country_code, validate_proxy


def scrapingant(max, countries=[], protocol="http"):
    result = []
    count = 0
    raw = requests.get("https://scrapingant.com/proxies", timeout=5).text
    rows = [i.split("<td>") for i in raw.split("<tr>")]

    def clean(text):
        return text[: text.find("<")].strip()

    for row in rows[2:]:
        if count == max:
            return result
        zprotocol = clean(row[3]).lower()
        if zprotocol != protocol:
            continue
        cleaned = [
            clean(row[1]) + ":" + clean(row[2]),
            protocol,
            get_country_code(clean(row[4].split(" ", 1)[1])),
        ]
        if validate_proxy(cleaned, countries):
            result.append({cleaned[1]: cleaned[0]})
            count += 1
    return result


def proxyscrape(max, countries=[], protocol="http"):
    result = []
    count = 0
    request_url = "https://api.proxyscrape.com/v2/?timeout=5000&request=displayproxies&protocol=http"
    if countries == []:
        request_url += "&country=all"
    else:
        request_url += "&country=" + ",".join(countries)
    if protocol == "https":
        request_url += "&ssl=yes"
    ips = requests.get(request_url).text
    for ip in ips.split("\n"):
        if count == max:
            return result
        proxy = [ip.strip(), protocol, "all"]
        if validate_proxy(proxy, []):
            result.append({proxy[1]: proxy[0]})
            count += 1
    return result


providers = [proxyscrape, scrapingant]