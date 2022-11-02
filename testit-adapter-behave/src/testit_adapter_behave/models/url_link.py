# TODO: Add model to python-commons; implement via attrs
def get_url_link_model(label):
    return {
        'url': label,
        # TODO: Make optional in Converter python-commons
        'title': None,
        'type': None,
        'description': None
    }
