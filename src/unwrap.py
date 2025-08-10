from typing import TypeVar

T = TypeVar("T")

def unwrap(value: T | Exception) -> T:
    """
    unwrap function return value and raise error

    Args:
        value:
            return variable of the function
    
    Returns:
        the value itself
    """
    if isinstance(value, Exception):
        raise value # Do error handling here
    else:
        return value