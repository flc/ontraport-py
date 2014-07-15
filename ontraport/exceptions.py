class APIError(Exception):
    pass


class APINonOKResponseError(APIError):
    pass


class APIFailureError(APIError):
    pass
