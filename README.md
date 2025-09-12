# formalpdf

`formalpdf` is an Apache-licensed python library for PDF forms.
It's a unified API for extracting, creating, filling, and flattening forms. 
It has a similar, but _not_ drop-in, high-level API to PyMuPDF.
All of this is possible by wrapping `pdfium`, thanks to the low-level bindings made available through `pypdfium2`.

## Installation

### Using `uv`

```sh
uv pip install formalpdf
```

### Using `pip`

```sh
pip install formalpdf
```

## CLI Usage

🚧 Soon you can use `formalpdf` to fill a PDF from an FDF document using:

```sh
formalpdf fill <input.pdf> <input.fdf> <output.pdf>
```

## Programmatic Usage

### Get All `Widget` Objects in a PDF

```py
from formalpdf import Document

doc = Document("/path/to/your.pdf")

for page in doc:
    widgets = page.widgets()
```

A `Widget` object has information about the location, type, and contents of form fields/wdigets in the PDF.
For isntance, a widget might look like:

```py
Widget(
    # name of the widget
    field_name='Text110',
    # label/alternate name, if provided
    field_label='Date (MM/DD/YYYY)',
    # current value (always a string, even if checkbox or combobox)
    field_value='',
    # widget type enum value
    field_type=6,
    # widget type string value 
    field_type_string='Text',
    # widget location Rect
    rect=Rect(
        top=36.95610046386719,
        left=473.5320129394531,
        bottom=24.171100616455078,
        right=587.177978515625
    )
)

```


### Filling out Forms: Updating `Widget` Values

Let's say we had some textbox widget:

```py
w = doc[0].widgets()[0]
```

We can update it with:

```py
w.update("New Value")

doc.save("new_doc.pdf")
```

And when we open `new_doc.pdf` we'll find a the value filled out!

### Creating Forms

🚧 Work in Progress

### Adding Annotations (Highlights, Links, etc.)

🚧 Work in Progress

### Rendering, Extracting Text, Extracting Images

🚧 Work in Progress

### Navigating Unsupported Operations

You can access the raw `PdfDocument` from `pypdfium2` using by calling:

```py
from formalpdf import Document

doc = Document("/path/to/your.pdf")

pdfium_doc = doc.document
```

You can use this to do lower-level operations that aren't yet supported by `formalpdf`.
For instance, if you want to render the first page of the document (currently an unsupported option):

```py
from formalpdf import Document

doc = Document("/path/to/your.pdf")

pdfium_doc = doc.document
bmp = pdfium_doc[0].render(scale=scale)
pil = bmp.to_pil()
```

## Testing

```
uv run pytest
```

There are a large number of test PDFs found in `tests/data`.


## Roadmap

- [x] create PyPI package
- [x] finish widget extraction 
- [ ] widget updating
  - [x] textbox
  - [ ] checkbox
  - [ ] combobox
- [ ] widget creation
- [x] tests
