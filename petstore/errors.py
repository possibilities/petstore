class ApiError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class NotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__("Not found", 404)


class BadRequestError(ApiError):
    def __init__(self) -> None:
        super().__init__("Bad request", 400)
