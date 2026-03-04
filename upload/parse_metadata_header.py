import base64
def parse_metadata_header(metadata_header):
    """
    Parses Tus Upload-Metadata header.
    Example: 'filename base64value'
    """
    metadata={}
    pairs = metadata_header.split(",")
    for pair in pairs:
        key, value = pair.strip().split(" ")
        decoded_vaule = base64.b64decode(value).decode("utf-8")
        metadata[key]=decoded_vaule
    return metadata
