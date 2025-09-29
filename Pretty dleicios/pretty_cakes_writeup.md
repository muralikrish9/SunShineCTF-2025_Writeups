# Intergalactic Copyright Infringement — Forensics Writeup

**Category:** Forensics  
**Points:** 455  
**Author:** tsuto  
**Flag format:** `sun{...}`

---

## Summary

We were given a PDF named `prettydeliciouscakes.pdf` with the hint:

> “This cake is out of this world! … something else is out of place too. Note: This is not a steganography challenge.”

The PDF contains an **embedded file** (not an image-stego payload). The embedded file is a short JavaScript-like text that holds a Base64-encoded string. Decoding that string yields the flag.

**Flag:** `sun{p33p_d1s_fl@g_y0!}`

---

## Files

- `prettydeliciouscakes.pdf` (provided)

---

## Tools and environment

Any of the following approaches work:

- Hex viewer or `strings` to triage the PDF
- PDF object inspection (manual or with a parser)
- Python (for quick extraction/decompression of streams)

I used a minimal Python script to extract embedded objects and inspect their streams.

---

## Methodology

1. **Sanity checks**  
The prompt explicitly says it’s not steganography, so rather than hunting for LSBs in images, check the PDF’s internal objects. PDF flags often live in:
   - Embedded files (`/Type /EmbeddedFile`), or
   - JavaScript actions (`/AA`, `/OpenAction`, `/S /JavaScript`).

2. **Scan the PDF structure**  
Look for telltale markers in the raw bytes:
   - `/EmbeddedFile`, `/Names`, `/AA`  
In this PDF, `/EmbeddedFile` and `/Names` are present, confirming there is an embedded file.

3. **Extract the embedded stream**  
The embedded object uses `FlateDecode`. Decompress the stream and read the content.

4. **Decode the payload**  
The embedded content is a one-liner:

```
const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';
```

That string is Base64. Decoding it gives the flag.

---

## Replication (Python snippet)

```python
import re, zlib, base64

pdf = open("prettydeliciouscakes.pdf","rb").read()

# Locate objects; extract those marked as EmbeddedFile
for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj(.*?)endobj", pdf, flags=re.DOTALL):
    body = m.group(3)
    if b"/EmbeddedFile" not in body:
        continue
    sm = re.search(rb">>\s*stream\r?\n", body)
    if not sm:
        continue
    sstart = sm.end()
    send = body.find(b"endstream", sstart)
    stream = body[sstart:send].rstrip(b"\r\n")

    # Decompress if Flate encoded
    if b"/FlateDecode" in body:
        stream = zlib.decompress(stream)

    print(stream.decode("utf-8","ignore"))
    # -> const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';
    print(base64.b64decode("c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==").decode())
    # -> sun{p33p_d1s_fl@g_y0!}
```

---

## Findings

- **PDF indicators**
  - `/EmbeddedFile`: present
  - `/Names`: present
  - `/AA`: present (no direct JavaScript action was required for this solve)
- **Embedded object content**  
```
const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';
```
- **Decoded flag**  
```
sun{p33p_d1s_fl@g_y0!}
```

---

## Lessons learned

- When a challenge says “not steganography,” believe it. PDFs can carry embedded files or actions that are easy to miss if you only inspect images.
- Check PDF object trees for `/EmbeddedFile`, `/Names`, `/AA`, `/OpenAction`, and filters like `/FlateDecode` that you may need to decompress.

---

## Appendix

- **Key strings found:** `/EmbeddedFile`, `/Names`, `/AA`  
- **Embedded file size (decompressed):** 49 bytes  
- **Embedded content preview:** `const data = 'c3Vue3AzM3BfZDFzX2ZsQGdfeTAhfQ==';`
