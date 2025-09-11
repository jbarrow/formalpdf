from typing import Callable

import pypdfium2.raw as pdfium_c
import ctypes


def get_pdfium_string(f: Callable, *args) -> str:
    """
    get_pdfium_string
        - f: Callable C++ function that fills a buffer
        - *args: all arguments except the buffer pointer and buffer length

    Helper function to get a python string from a PDFium C++ function that populates
    a buffer.
    """
    # first call with a null pointer to get the number of bytes necessary
    n_bytes = f(*args, None, 0)

    # create the buffer and cast a buffer pointer
    buffer = ctypes.create_string_buffer(n_bytes)
    buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(pdfium_c.FPDF_WCHAR))

    # second call to the same function to populate the buffer
    f(*args, buffer_ptr, n_bytes)

    # convert to a python string
    string = buffer.raw[: n_bytes - 2].decode("utf-16-le")

    return string

