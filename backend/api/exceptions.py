from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, AuthenticationFailed):
        logger.warning('Unauthorized access attempt: {}'.format(exc))

    return response
