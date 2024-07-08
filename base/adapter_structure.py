from collections import defaultdict
from base.templates import Problem, Algorithm
from typing import Dict, Tuple, Callable

__QL_TRANSLATIONS: Dict[type, Tuple[type, Callable]] = {}


def adapter(translates_from: str, translates_to: str):
    def outer(func):
        def inner(func2):
            def inner_inner(*args, **kwargs):
                return func(func2(*args, **kwargs))
            return inner_inner
        __QL_TRANSLATIONS[translates_to] = (translates_from, inner)
        return inner
    return outer


__QL_ADAPTERS: Dict[type, Dict[type, Callable]] = defaultdict(lambda: {})


def formatter(problem: Problem, format: str):
    def wrapper(func):
        __QL_ADAPTERS[problem][format] = func
        return func
    return wrapper


def get_formatter(problem_id: Problem, alg_format: str):
    if alg_format in __QL_ADAPTERS[problem_id]:
        return __QL_ADAPTERS[problem_id][alg_format]
    if alg_format in __QL_TRANSLATIONS:
        origin_format, translation = __QL_TRANSLATIONS[alg_format]
        raw_adapter = get_formatter(problem_id, origin_format)
        return translation(raw_adapter)
    return None
