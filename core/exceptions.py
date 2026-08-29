import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return Response(
            {
                "status_code": 500,
                "error": "Internal Server Error",
                "details": "An unexpected error occurred on the server."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    logger.warning(f"Handled Exception: {str(exc)}", exc_info=True)
    return Response(
        {
            "status_code": response.status_code,
            "error": exc.__class__.__name__,
            "details": response.data
        },
        status=response.status_code
    )