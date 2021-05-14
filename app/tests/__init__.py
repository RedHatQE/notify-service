from functools import wraps
from typing import Callable, Optional, Type

from fastapi_cache.coder import Coder

from unittest.mock import patch


def mock_cache(
    expire: int = None,
    coder: Type[Coder] = None,
    key_builder: Callable = None,
    namespace: Optional[str] = "",
):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            nonlocal coder
            nonlocal expire
            nonlocal key_builder
            return await func(*args, **kwargs)

    return wrapper


# Patch cache decorator without access cache at init
patch('fastapi_cache.decorator.cache', mock_cache).start()
