# TODO: Add model to python-commons; implement via attrs
def get_test_result_step_model():
    return {
        'title': None,
        'description': '',
        'outcome': None,
        'duration': 0,
        'steps': [],
        'parameters': {},
        'attachments': [],
        # TODO: Add to python-commons
        # 'started_on': '',
        # 'completed_on': None
    }
