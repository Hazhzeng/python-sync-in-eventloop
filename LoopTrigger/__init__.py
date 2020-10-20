import asyncio
import concurrent.futures
import json
import logging

import azure.functions as func
from time import time
from requests import get, Response


async def invoke_get_request(executor: concurrent.futures.Executor,
                             eventloop: asyncio.AbstractEventLoop) -> Response:
    single_starttime = time()
    # Wrap synchronous call in executor
    single_result = await eventloop.run_in_executor(
        executor,  # using the default executor
        get,  # each task call invoke_get_request
        'https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python'  # argument needs to parse into the invoke_get_request
    )
    single_endtime = time()
    return {
        'StartTime': single_starttime,
        'EndTime': single_endtime,
        'Duration': single_endtime - single_starttime,
        'StatusCode': single_result.status_code
    }

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')


    starttime = time()
    # Creating your own threadpool with 10 threads and use the current eventloop
    threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    eventloop = asyncio.get_event_loop()

    # Create 10 tasks for synchronous call
    tasks = [
        asyncio.create_task(
            invoke_get_request(threadpool, eventloop)
        ) for _ in range(10)
    ]
    done_tasks, pending = await asyncio.wait(tasks)
    endtime = time()

    # Calculate total time from summing up individual request
    duration_in_serial = sum([
        d.result().get('Duration') for d in done_tasks
    ])

    # Result
    result = {
        'StartTime': starttime,
        'EndTime': endtime,
        'Duration': endtime - starttime,
        'DurationIfRunInSerial': duration_in_serial,
        'Number of Response': len(done_tasks),
        'Responses': [d.result() for d in done_tasks]
    }

    return func.HttpResponse(body=json.dumps(result), mimetype='application/json')
