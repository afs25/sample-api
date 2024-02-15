import json
import uuid
from http import HTTPStatus
from datetime import timedelta
from jsonpatch import JsonPatch, JsonPatchException


BASE_USER_SELECT_SQL = str()


def get_user_by_id_api(event, context):
    start_time = get_start_time()
    logger = get_logger()
    correlation_id = None

    if triggered_by_heartbeat(event):
        logger.info('API call (heartbeat)', extra={'event': event})
        return

    try:
        correlation_id = get_correlation_id(event)
        user_id = event['pathParameters']['id']
        logger.info('API call', extra={'user_id': user_id, 'correlation_id': correlation_id, 'event': event})

        result = get_user_by_id(user_id, correlation_id)

        if len(result) > 0:
            response = {"statusCode": HTTPStatus.OK, "body": json.dumps(result[0])}
        else:
            errorjson = {'user_id': user_id, 'correlation_id': str(correlation_id)}
            raise ObjectDoesNotExistError('user does not exist', errorjson)

    except ObjectDoesNotExistError as err:
        response = {"statusCode": HTTPStatus.NOT_FOUND, "body": err.as_response_body()}

    except DetailedValueError as err:
        response = {"statusCode": HTTPStatus.BAD_REQUEST, "body": err.as_response_body()}

    except Exception as ex:
        errorMsg = ex.args[0]
        logger.error(errorMsg, extra={'correlation_id': correlation_id})
        response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": error_as_response_body(errorMsg, correlation_id)}

    logger.info('API response', extra={'response': response, 'correlation_id': correlation_id, 'elapsed_ms': get_elapsed_ms(start_time)})
    return response


def get_user_by_email_api(event, context):
    start_time = get_start_time()
    logger = get_logger()
    correlation_id = None
    logger.info('debugging', extra={'event': event})

    if triggered_by_heartbeat(event):
        logger.info('API call (heartbeat)', extra={'event': event})
        return

    try:
        user_email = event['queryStringParameters']['email']
        correlation_id = get_correlation_id(event)
        logger.info('API call', extra={'user_email': user_email, 'correlation_id': correlation_id, 'event': event})

        result = get_user_by_email(user_email, correlation_id)

        if len(result) > 0:
            response = {"statusCode": HTTPStatus.OK, "body": json.dumps(result[0])}
        else:
            errorjson = {'user_email': user_email, 'correlation_id': str(correlation_id)}
            raise ObjectDoesNotExistError('user does not exist', errorjson)

    except ObjectDoesNotExistError as err:
        response = {"statusCode": HTTPStatus.NOT_FOUND, "body": err.as_response_body()}

    except Exception as ex:
        errorMsg = ex.args[0]
        logger.error(errorMsg, extra={'correlation_id': correlation_id})
        response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": error_as_response_body(errorMsg, correlation_id)}

    logger.info('API response', extra={'response': response, 'correlation_id': correlation_id, 'elapsed_ms': get_elapsed_ms(start_time)})
    return response


def patch_user_api(event, context):
    start_time = get_start_time()
    logger = get_logger()
    correlation_id = None

    if triggered_by_heartbeat(event):
        logger.info('API call (heartbeat)', extra={'event': event})
        return

    try:
        correlation_id = get_correlation_id(event)
        # get info supplied to api call
        user_id = event['pathParameters']['id']
        user_jsonpatch = JsonPatch.from_string(event['body'])

        logger.info('API call', extra={'user_id': user_id, 'user_jsonpatch': user_jsonpatch, 'correlation_id': correlation_id, 'event': event})

        modified_time = now_with_tz()

        # create an audit record of update, inc 'undo' patch
        entity_update = create_user_entity_update(user_id, user_jsonpatch, modified_time, correlation_id)

        patch_user(user_id, user_jsonpatch, modified_time, correlation_id)

        response = {"statusCode": HTTPStatus.NO_CONTENT, "body": json.dumps('')}

        # on successful update save audit record
        entity_update.save()

    except ObjectDoesNotExistError as err:
        response = {"statusCode": HTTPStatus.NOT_FOUND, "body": err.as_response_body()}

    except (PatchAttributeNotRecognisedError, PatchOperationNotSupportedError, PatchInvalidJsonError, DetailedValueError) as err:
        response = {"statusCode": HTTPStatus.BAD_REQUEST, "body": err.as_response_body()}

    except Exception as ex:
        errorMsg = ex.args[0]
        logger.error(errorMsg, extra={'correlation_id': correlation_id})
        response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": error_as_response_body(errorMsg, correlation_id)}

    logger.info('API response', extra={'response': response, 'correlation_id': correlation_id, 'elapsed_ms': get_elapsed_ms(start_time)})

    return response

def create_user_api(event, context):
    start_time = get_start_time()
    logger = get_logger()
    correlation_id = None

    if triggered_by_heartbeat(event):
        logger.info('API call (heartbeat)', extra={'event': event})
        return

    try:
        user_json = json.loads(event['body'])
        correlation_id = get_correlation_id(event)
        logger.info('API call', extra={'user_json': user_json, 'correlation_id': correlation_id, 'event': event})

        new_user = create_user(user_json, correlation_id)

        response = {"statusCode": HTTPStatus.CREATED, "body": json.dumps(new_user)}

    except DuplicateInsertError as err:
        response = {"statusCode": HTTPStatus.CONFLICT, "body": err.as_response_body()}

    except DetailedValueError as err:
        response = {"statusCode": HTTPStatus.BAD_REQUEST, "body": err.as_response_body()}

    except Exception as ex:
        errorMsg = ex.args[0]
        logger.error(errorMsg, extra={'correlation_id': correlation_id})
        response = {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": error_as_response_body(errorMsg, correlation_id)}

    logger.info('API response', extra={'response': response, 'correlation_id': correlation_id, 'elapsed_ms': get_elapsed_ms(start_time)})
    return response


# IGNORE ANYTHING BELOW THIS LINE
class Logger:
    @staticmethod
    def info(s, extra):
        pass

    @staticmethod
    def error(s, extra):
        pass

def get_start_time():
    pass

def get_logger():
    return Logger()

def triggered_by_heartbeat(event):
    pass

def get_correlation_id(event):
    pass

def patch_user(id_to_update, patch_json, modified_time, correlation_id):
    pass


def get_user_by_email(user_email, correlation_id):
    pass

def validate_status(s):
    pass


def append_avatar_to_list(user_list):
    pass


def append_avatar(user):
    pass


def append_calculated_properties_to_list(user_list):
    pass


def append_calculated_properties(user):
    pass


def get_user_by_id(user_id, correlation_id):
    return list()

def error_as_response_body(s, z):
    pass


def get_elapsed_ms(s):
    pass

def create_user(user_json, correlation_id):
    pass

def now_with_tz():
    pass


def create_user_entity_update():
    pass

class DetailedValueError(ValueError):
    def __init__(self, message: str, details: dict):
        self.message = message
        self.details = details

    def as_response_body(self):
        pass


class DeliberateError(DetailedValueError):
    pass


class ObjectDoesNotExistError(DetailedValueError):
    pass


class DuplicateInsertError(DetailedValueError):
    pass


class PatchOperationNotSupportedError(DetailedValueError):
    pass


class PatchAttributeNotRecognisedError(DetailedValueError):
    pass


class PatchInvalidJsonError(DetailedValueError):
    pass


class DetailedIntegrityError(DetailedValueError):
    pass