import json
import logging

import azure.functions as func
from time import time
from requests import get, Response


def invoke_get_request() -> Response:
    single_starttime = time()
    single_result = get('https://docs.microsoft.com/en-us/azure'
                        '/azure-functions/functions-reference-python')
    single_endtime = time()
    return {
        'StartTime': single_starttime,
        'EndTime': single_endtime,
        'Duration': single_endtime - single_starttime,
        'StatusCode': single_result.status_code
    }

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Invoke get request 10 times
    starttime = time()
    responses = [invoke_get_request() for _ in range(10)]
    endtime = time()

    # Calculate total time from summing up individual request
    duration_in_serial = sum([
        responses[i].get(f'Duration') for i in range(10)
    ])

    # Result
    result = {
        'StartTime': starttime,
        'EndTime': endtime,
        'Duration': endtime - starttime,
        'DurationIfRunInSerial': duration_in_serial,
        'Number of Response': len(responses),
        'Responses': responses
    }

    return func.HttpResponse(body=json.dumps(result), mimetype='application/json')
