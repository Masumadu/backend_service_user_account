query_responses = {
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "error": "Unauthorized",
                    "message": "not authenticated",
                    "internal_code": 401,
                    "internal_message": "",
                }
            }
        },
    },
    403: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "error": "Unauthorized",
                    "message": "not enough permission",
                    "internal_code": 403,
                    "internal_message": "",
                }
            }
        },
    },
    404: {
        "description": "ResourceDoesNotExist",
        "content": {
            "application/json": {
                "example": {
                    "error": "ResourceDoesNotExist",
                    "message": "object does not exist",
                    "internal_code": 404,
                    "internal_message": "",
                }
            }
        },
    },
    422: {
        "description": "OperationError",
        "content": {
            "application/json": {
                "example": {
                    "error": "OperationError",
                    "message": "too many requests",
                    "internal_code": 422,
                    "internal_message": "",
                }
            }
        },
    },
    500: {
        "description": "InternalServerError",
        "content": {
            "application/json": {
                "example": {
                    "error": "InternalServerError",
                    "message": "server error",
                    "internal_code": 500,
                    "internal_message": "",
                }
            }
        },
    },
}

data_responses = {
    400: {
        "description": "ValidationException",
        "content": {
            "application/json": {
                "example": {
                    "error": "ValidationException",
                    "message": f"bad input [('body', 'product_category', 'field required')]",  # noqa
                    "internal_code": 400,
                    "internal_message": None,
                }
            }
        },
    },
}
