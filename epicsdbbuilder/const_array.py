from decimal import Decimal
from .recordbase import quote_string
from .parameter import Parameter

__all__ = ['ConstArray']


class ConstArray:
    """Constant Link Values. EPICS Base 3.16.1 and above.

    Example: PY Source
    ------------------
    `r = records.lsi('r', INP=ConstArray(['Plain String not DBLINK']))`

    Example: Generated DB
    ---------------------
    `field(INP, ["Plain String not DBLINK"])`
    """

    def __init__(self, value):
        """Constructor.

        Parameters
        ----------
        value : iterable
            Iterable which can provide a homogeneous non-empty list of values.
        """
        self.__value = self._sanitize(value)

    def _sanitize(self, raw_value):
        # ConstArray allows iterable only.
        value_list = list(raw_value)

        # EPICS 7.0.3.1 does not consider "[]" as constant.
        assert len(value_list) > 0, \
            f'ConstArray: Empty iterable is not allowed.'

        # EPICS does not allow mixing of strings and numbers.
        numbers = False
        strings = False
        valid_types = (Parameter, str, int, float, bool, Decimal)
        for index, value in enumerate(value_list):
            assert isinstance(value, valid_types), \
                f'ConstArray: expects a string or parameter as element' \
                f' but an element at the index {index} is {type(value)}.'

            if isinstance(value, (Parameter, str)):
                assert not numbers, \
                    f'ConstArray: cannot mix strings' \
                    f' with an element at index {index} which is {type(value)}.'
                strings = True
            else:
                assert not strings, \
                    f'ConstArray: cannot mix numbers' \
                    f' with an element at index {index} which is {type(value)}.'
                numbers = True

        return value_list

    def _format_constant(self, value):
        if isinstance(value, Parameter):
            return f'"{str(value)}"'
        if isinstance(value, str):
            return quote_string(value)
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)

    def Validate(self, record, fieldname):
        """epicsdbbuilder callback
        """
        # Validation has been done on inside constructor already.
        # ConstArray is meant to be used with fields
        # which can contain a DB link (e.g. INLINK).
        # Unfortunately, dbVerify() does not verify
        # format of DB links. Therefore, it is not used here.
        pass

    def FormatDb(self, record, fieldname):
        """epicsdbbuilder callback
        """
        formatted = [self._format_constant(v) for v in self.__value]
        return '[{}]'.format(','.join(formatted))

    def __repr__(self):
        return f'<ConstArray {repr(self.__value)}>'
