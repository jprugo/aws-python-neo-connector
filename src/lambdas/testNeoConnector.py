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

    bucket = event['bucket']
    file = event['file']

    try:
        signal.alarm(int(context.get_remaining_time_in_millis() / 1000)-1)
        print('Executing query...')
        response = DB_NAME.execute_query(
            bucket=bucket, file=file)
        print('fetched data')
        response = json.loads(response)
        if len(response) == 0:
            status_code = 204,
            response = "There is no content to show"
    except (QueryingException, NoSuchConnectionException, AttributeError) as e:
        response = str(e)
        print(response)
        status_code = 502
    except TimeoutError:
        response = "Endpoint request timeout"
        status_code = 403
    except NameError as e:
        response = str(e)
        print(response)
        status_code = 500

    body = {
        "results" if status_code == 200 else "message" : response,
    }
    
    print(f'body formed: {body}')
    
    signal.alarm(0)# This line fixed the issue above!
    
    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }




