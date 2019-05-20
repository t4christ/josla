from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = 'The requested profile does not exist.'



from rest_framework.views import exception_handler
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # check if exception has dict items
        if hasattr(exc.detail, 'items'):
            # remove the initial value
            response.data = {}
            errors = []
            for key, value in exc.detail.items():
                # append errors into the list
                errors.append("{} : {}".format(key, " ".join(value)))
            
            # add property errors to the response
            response.data['errors'] = errors

        # serve status code in the response
        response.data['status_code'] = response.status_code

    return response
