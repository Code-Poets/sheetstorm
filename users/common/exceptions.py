from typing import Optional
from typing import Union

from users.common.constants import ErrorCode


class SheetStormBaseException(Exception):
    def __init__(self, error_message: Optional[str], error_code: ErrorCode) -> None:
        assert isinstance(error_message, Union[str, None].__args__)  # pylint: disable=no-member
        assert isinstance(error_code, ErrorCode)
        self.error_code = error_code
        self.error_message = "" if error_message is None else error_message
        super().__init__(error_message)
