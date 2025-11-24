from typing import Optional, Union, List
from pydantic import BaseModel
from starlette import status


class Result:
    def __init__(
        self,
        message: str = "",
        data: Optional[Union[BaseModel, List[BaseModel]]] = None,
        status: int = status.HTTP_204_NO_CONTENT,
    ):
        self.data: Optional[Union[BaseModel, List[BaseModel]]] = data
        self.message = message
        self.status = status


class ServicesResult:
    def __init__(
        self,
        message="",
        data=None,
        status_code=status.HTTP_200_OK,
        status=True,
    ):
        self.data = data
        self.status_code = status_code
        self.message = message
        self.status = status

    @property
    def is_error(self):
        return not self.status
