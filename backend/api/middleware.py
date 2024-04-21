import logging

from foodgram.logging import telegram_handler

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.exception('Произошло необработанное исключение')
            telegram_handler.emit(logging.makeLogRecord({
                'msg': f'Произошло необработанное исключение: {str(e)}',
                'levelname': 'ERROR',
                'name': __name__
            }))
            raise

    def process_exception(self, request, exception):
        pass