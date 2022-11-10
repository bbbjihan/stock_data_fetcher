from abc import *
from functools import partial


class KRX_data_interface(metaclass=ABCMeta):
    """
    interface class for crawling data from
        https://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
    """

    @abstractmethod
    def is_empty(self):
        raise NotImplementedError

    @abstractmethod
    def to_csv(self):
        """
        얘가 하는건 base가 되는 데이터 제공자
        sql append하기 전에 일단 다 저장하기
        """
        raise NotImplementedError

    @abstractproperty
    def csv_path(self):
        raise NotImplementedError

    @abstractmethod
    async def get_data(self):
        raise NotImplementedError

    @abstractmethod
    def run(self, *args, **kwargs):
        return partial(self.get_data, *args, **kwargs)
