import win32com.client
import pythoncom
import time
import logging

_DELAY = 0.05  # seconds
_TIMEOUT = 60.0  # seconds


def _com_call_wrapper(f, *args, **kwargs):
    """
    COMWrapper support function.
    Repeats calls when 'Call was rejected by callee.' exception occurs.
    """
    # Unwrap inputs
    args = [arg._wrapped_object if isinstance(arg, ComWrapper) else arg for arg in args]
    kwargs = dict([(key, value._wrapped_object)
                   if isinstance(value, ComWrapper)
                   else (key, value)
                   for key, value in dict(kwargs).items()])

    start_time = None
    while True:
        try:
            result = f(*args, **kwargs)
        except pythoncom.com_error as e:
            if e.strerror == 'Call was rejected by callee.':
                if start_time is None:
                    start_time = time.time()
                    logging.warning('Call was rejected by callee.')

                elif time.time() - start_time >= _TIMEOUT:
                    raise

                time.sleep(_DELAY)
                continue

            raise

        break

    if isinstance(result, win32com.client.CDispatch) or callable(result):
        return ComWrapper(result)
    return result


class ComWrapper(object):
    """
    Class to wrap COM objects to repeat calls when 'Call was rejected by callee.' exception occurs.
    """

    def __init__(self, wrapped_object):
        assert isinstance(wrapped_object, win32com.client.CDispatch) or callable(wrapped_object)
        self.__dict__['_wrapped_object'] = wrapped_object

    def __getattr__(self, item):
        return _com_call_wrapper(self._wrapped_object.__getattr__, item)

    def __getitem__(self, item):
        return _com_call_wrapper(self._wrapped_object.__getitem__, item)

    def __setattr__(self, key, value):
        _com_call_wrapper(self._wrapped_object.__setattr__, key, value)

    def __setitem__(self, key, value):
        _com_call_wrapper(self._wrapped_object.__setitem__, key, value)

    def __call__(self, *args, **kwargs):
        return _com_call_wrapper(self._wrapped_object.__call__, *args, **kwargs)

    def __repr__(self):
        return 'ComWrapper<{}>'.format(repr(self._wrapped_object))


# _xl = win32com.client.dynamic.Dispatch('Excel.Application')
# xl = ComWrapper(_xl)
#
# # Do stuff with xl instead of _xl, and calls will be attempted until the timeout is
# # reached if "Call was rejected by callee."-exceptions are thrown.