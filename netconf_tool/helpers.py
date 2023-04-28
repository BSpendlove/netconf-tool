from urllib.parse import urlparse


def parse_rfc3986_uri(uri: str) -> dict:
    parsed_uri = urlparse(uri)
    uri_object = parsed_uri._asdict()
    if parsed_uri.query:
        queries = {}
        for query in parsed_uri.query.split("&"):
            k, v = query.split("=")
            if queries.get(k):
                raise KeyError("Query Key already exists")
            queries[k] = v

        uri_object["queries"] = queries
    return uri_object
