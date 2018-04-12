import string
import random


def unicode_id():
    """
    生成一个10位数的唯一标识符
    :return:
    """
    choices_str = string.ascii_lowercase + string.digits
    result_list = random.sample(choices_str, 10)
    return "".join(result_list)