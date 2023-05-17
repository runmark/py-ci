"""
1）找出偶数
2）乘以3
3）转成字符串返回

force(nums | even_filter | multiply_by_three | convert_to_string | echo)
"""


class Pipe:
    def __init__(self, func):
        self._func = func

    def __ror__(self, other):
        def generator():
            for obj in other:
                if obj is not None:
                    yield self._func(obj)

        return generator()


@Pipe
def even_filter(num):
    return num if num % 2 == 0 else None


@Pipe
def multiply_by_three(num):
    return num * 3


@Pipe
def convert_to_string(num):
    return f"The number is {num}"


@Pipe
def echo(item):
    print(item)
    return item


def force(sqs):
    for item in sqs:
        pass


nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
force(nums | even_filter | multiply_by_three | convert_to_string | echo)
