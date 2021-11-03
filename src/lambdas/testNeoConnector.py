import json
import signal
# from layers
from NeoConnector.DBConnector import DBConnector
from NeoConnector.extras import ConnectionException, NoSuchConnectionException, QueryingException


def timeout_handler(_signal, _frame):
    raise TimeoutError()


try:
    print('establishing connection')
    DB_NAME = DBConnector(
        secret_id="arn:aws:secretsmanager:region:account:secret:funny_name", timeout=5)
    print('connection created!')
except (ConnectionException, NotImplementedError) as e:
    print(str(e))


signal.signal(signal.SIGALRM, timeout_handler)


def handler(event, context):

    status_code = 200

    try:
        signal.alarm(int(context.get_remaining_time_in_millis() / 1000)-1)
        bucket = event['queryStringParameters']['bucket']
        file = event['queryStringParameters']['file']
        date = event['queryStringParameters']['date']
        print('Executing query...')
        response = DB_NAME.execute_query(
            bucket=bucket, file=file, params = {"fecha": date})
        response = json.loads(response)
        print(f'fetched data: {response}')
        if len(response) == 0:
            status_code = 204
            response = "There is no content to show"
    except (QueryingException, NoSuchConnectionException, AttributeError) as e:
        response = str(e)
        status_code = 502
    except NameError as e:
        response = str(e)
        status_code = 500
    except TimeoutError:
        response = "Endpoint request timeout"
        status_code = 403

    body = {
        "results" if status_code == 200 else "message": response,
    }

    signal.alarm(0)  # This line fixed the issue above!

    return {
        'statusCode': status_code,
        'body': json.dumps(body, default= str)
    }
