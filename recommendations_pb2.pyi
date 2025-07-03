from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BookCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MYSTERY: _ClassVar[BookCategory]
    SCIENCE_FICTION: _ClassVar[BookCategory]
    SELF_HELP: _ClassVar[BookCategory]
    FANTASY: _ClassVar[BookCategory]
    HISTORY: _ClassVar[BookCategory]
    THRILLER: _ClassVar[BookCategory]
    ROMANCE: _ClassVar[BookCategory]
    BIOGRAPHY: _ClassVar[BookCategory]
    POETRY: _ClassVar[BookCategory]
    CLASSICS: _ClassVar[BookCategory]
MYSTERY: BookCategory
SCIENCE_FICTION: BookCategory
SELF_HELP: BookCategory
FANTASY: BookCategory
HISTORY: BookCategory
THRILLER: BookCategory
ROMANCE: BookCategory
BIOGRAPHY: BookCategory
POETRY: BookCategory
CLASSICS: BookCategory

class RecommendationRequest(_message.Message):
    __slots__ = ("user_id", "category", "max_results")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    MAX_RESULTS_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    category: BookCategory
    max_results: int
    def __init__(self, user_id: _Optional[int] = ..., category: _Optional[_Union[BookCategory, str]] = ..., max_results: _Optional[int] = ...) -> None: ...

class BookRecommendation(_message.Message):
    __slots__ = ("id", "title")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...

class RecommendationResponse(_message.Message):
    __slots__ = ("recommendations",)
    RECOMMENDATIONS_FIELD_NUMBER: _ClassVar[int]
    recommendations: _containers.RepeatedCompositeFieldContainer[BookRecommendation]
    def __init__(self, recommendations: _Optional[_Iterable[_Union[BookRecommendation, _Mapping]]] = ...) -> None: ...
