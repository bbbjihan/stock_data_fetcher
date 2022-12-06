import re


def only_KOR_chosung(string: str) -> bool:
    """
    초성만 있는지 확인
    """
    return bool(re.search("^[ㄱ-ㅎ]*$", string))


def only_KOR_char(string: str) -> bool:
    """
    음절(완성된 글자)만 있는지 확인
    """
    return bool(re.search("^[가-힣]*$", string))


def only_ENG(string: str) -> bool:
    """
    영어만 있는지 확인
    """
    return bool(re.search("^[a-zA-Z]*$", string))


def only_NUM(string: str) -> bool:
    """
    숫자만 있는지 확인
    """
    return bool(re.search("^[0-9]*$", string))


def is_ISU_CODE(string: str) -> bool:
    """
    ISIN 코드인지 확인
    """
    if not bool(re.search("^([A-Z]){2}.*$", string)):
        return False
    return bool(re.search("^[0-9]*$", string))
