"""
Custom Exception Handlers
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON response with validation error details
    """
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy exception
        
    Returns:
        JSON response with error message
    """
    logger.error(f"Database error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Database error occurred",
            "detail": "An error occurred while processing your request"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    
    Args:
        request: FastAPI request
        exc: General exception
        
    Returns:
        JSON response with error message
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


def setup_exception_handlers(app):
    """
    Setup exception handlers for the application
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
