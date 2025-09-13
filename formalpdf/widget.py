from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, List, Optional
from PIL import Image

from .utils import get_pdfium_string, FieldTypeToStr

import pypdfium2.raw as pdfium_c
import pypdfium2.internal as pdfium_i
import pypdfium2 as pdfium
import ctypes


class Document:
    def __init__(self, path: str):
        self.document = pdfium.PdfDocument(path)
        self._init_formenv()

    def _init_formenv(self):
        if self.form_type is not None:
            self.document.init_forms()
            self.formenv = self.document.formenv

    @property
    def form_type(self) -> str:
        formtype = self.document.get_formtype()

        if formtype != pdfium_c.FORMTYPE_NONE:
            return pdfium_i.FormTypeToStr.get(formtype)

        return None

    def page(self, number: int) -> Page:
        return Page(self.document[number], self, number=number)
    
    def __getitem__(self, key):
        """
        Support indexing like doc[n] and slicing like doc[start:stop].
        Returns Page for int indices, and a list[Page] for slices.
        """
        if isinstance(key, slice):
            # Normalize slice to a range of valid indices
            start, stop, step = key.indices(len(self))
            return [self.page(i) for i in range(start, stop, step)]
        if not isinstance(key, int):
            raise TypeError("Document indices must be integers or slices")

        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError("Document index out of range")

        return self.page(key)
    
    def __len__(self) -> int:
        return len(self.document)

    def __iter__(self) -> Iterator[Page]:
        for i, _ in enumerate(self.document):
            yield self.page(i)

    @property
    def is_tagged(self) -> bool:
        return bool(pdfium_c.FPDFCatalog_IsTagged(self.document))

    def save(self, dest, version=None, flags: int = 0):
        """
        Save the current document (pass-through to pypdfium2)
        """
        return self.document.save(dest, version=version, flags=flags)

    
class Page:
    """
    Class to store the page
    """
    def __init__(
        self,
        pdfium_page,
        document,
        number
    ):
        self._page = pdfium_page
        self.parent = document
        self.number = number

    def widgets(self):
        total_annotations = pdfium_c.FPDFPage_GetAnnotCount(self._page)

        widgets = []
        for i in range(total_annotations):
            annotation = pdfium_c.FPDFPage_GetAnnot(self._page, i)

            if pdfium_c.FPDFAnnot_GetSubtype(annotation) == pdfium_c.FPDF_ANNOT_WIDGET:
                widgets.append(Widget.from_pdfium(annotation, self.parent.formenv))

        return widgets

    def render(
            self,
            dpi: int = 72
    ) -> Image.Image:
        bitmap = self._page.render(
            scale = dpi / 72,
            rotation = 0
        )
        pil_image = bitmap.to_pil()
        return pil_image


class Point:
    ...


class Quat:
    ...


@dataclass
class Rect:
    """
    The Rect class has all the necessary transforms.
    """
    top: float
    left: float
    bottom: float
    right: float

    @classmethod
    def from_pdfium(cls, rect: pdfium_c.FS_RECTF) -> Rect:
        return cls(top=rect.top, left=rect.left, bottom=rect.bottom, right=rect.right)


@dataclass
class Widget:
    field_name: str
    field_label: str
    field_value: str
    choice_values: Optional[List[str]]
    # field_flags: int
    field_type: int
    field_type_string: str | None
    rect: Rect

    # keep a reference to the underlying PDFium annotation so we can mutate it
    _annotation: object | None = None

    def update(self, value: str) -> None:
        """
        Update the widget's value in-place for text fields.

        Currently only supports textboxes (FPDF_FORMFIELD_TEXTFIELD).
        """
        if self.field_type != pdfium_c.FPDF_FORMFIELD_TEXTFIELD:
            raise NotImplementedError("update() currently supports only textboxes")

        if self._annotation is None:
            raise RuntimeError("Underlying annotation handle is missing; cannot update.")

        # PDFium expects a UTF-8 C string for the key and a UTF-16-LE wide string for the value.
        key = b"V"  # the standard PDF key for a field's value
        utf16 = value.encode("utf-16-le") + b"\x00\x00"
        buffer = ctypes.create_string_buffer(utf16)
        buffer_ptr = ctypes.cast(buffer, ctypes.POINTER(pdfium_c.FPDF_WCHAR))

        ok = pdfium_c.FPDFAnnot_SetStringValue(self._annotation, key, buffer_ptr)
        if not ok:
            raise RuntimeError("PDFium failed to set the text field value")

        # reflect the change in our Python object
        self.field_value = value

    def reset():
        pass

    @classmethod
    def from_pdfium(cls, annotation, formenv: pdfium.PdfFormEnv) -> Widget:
        pdfium_rect = pdfium_c.FS_RECTF()
        pdfium_c.FPDFAnnot_GetRect(annotation, pdfium_rect)
        rect = Rect.from_pdfium(pdfium_rect)

        field_name = get_pdfium_string(
            pdfium_c.FPDFAnnot_GetFormFieldName, formenv.raw, annotation
        )
        field_value = get_pdfium_string(
            pdfium_c.FPDFAnnot_GetFormFieldValue, formenv.raw, annotation
        )
        field_type = pdfium_c.FPDFAnnot_GetFormFieldType(formenv.raw, annotation)
        field_type_string = FieldTypeToStr.get(field_type)

        field_label = get_pdfium_string(
            pdfium_c.FPDFAnnot_GetFormFieldAlternateName, formenv.raw, annotation
        )

        choice_values: Optional[List[str]] = None
        try:
            option_count = pdfium_c.FPDFAnnot_GetOptionCount(formenv.raw, annotation)
        except Exception:
            option_count = 0

        if option_count and option_count > 0:
            choice_values = []
            for i in range(option_count):
                label = get_pdfium_string(
                    pdfium_c.FPDFAnnot_GetOptionLabel, formenv.raw, annotation, i
                )
                choice_values.append(label)

        return cls(
            field_name=field_name,
            field_label=field_label,
            field_value=field_value,
            field_type=field_type,
            field_type_string=field_type_string,
            choice_values=choice_values,
            rect=rect,
            _annotation=annotation,
        )

