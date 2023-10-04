
class BaseException(Exception):
    def __str__(self):
        return self.msg


class InvalidJsonError(BaseException):
    msg = 'Invalid json request'
