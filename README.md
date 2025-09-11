# conformal

`conformal` is an Apache-licensed python library for PDF forms.
It's a 
It has a similar, but _not_ drop-in, high-level API to PyMuPDF.
All of this is possible by wrapping `pdfium`, thanks to the low-level bindings made available through `pypdfium2`.

## Installation


```sh
uv pip install conformal
```

## Usage

### Get All `Widget` Objects in a PDF

```py
doc = Document("/path/to/your.pdf")

for page in doc:
    widgets = page.widgets()
```

### Navigating Unsupported Operations

You can access the raw `PdfDocument` from `pypdfium2` using by calling:

```py
doc = Document("/path/to/your.pdf")

pdfium_doc = doc.document
```

You can use this to do lower-level operations that aren't yet supported by `conformal`.

## Roadmap

- [ ] create PyPI package
- [ ] finish widget extraction 
- [ ] widget updating
- [ ] widget creation
- [ ] tests
