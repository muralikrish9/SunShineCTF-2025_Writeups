# Forensics Challenge Writeup

## Challenge Description
We were given a suspicious DOCX file from a CCDC inject. The business team member seemed obsessed with a cat image, but the note explicitly stated that *this is not a steganography challenge*. The flag format was specified as `sun{}`.

---

## Step 1: Inspect the DOCX File
A `.docx` is just a ZIP archive. Unzipping it revealed the usual `word/` directory structure. Inside, there was an interesting file:

```
word/embeddings/oleObject1.bin
```

This suggested an embedded OLE object.

---

## Step 2: Examine the OLE Object
Opening `oleObject1.bin` revealed a Base64-encoded string:

```
fha{g0yr_g0yr_zl_o3y0i3q!}
```

---

## Step 3: Decode the Hidden String
The string already looked close to the target format (`fha{}`). Notably, the challenge text inside the document mentioned “tOle tOle my beloved,” hinting at a ROT13 transformation.

Applying ROT13 produced:

```
sun{t0le_t0le_my_b3l0v3d!}
```

---

## Step 4: Verify
- Format matches `sun{}`.
- Transformation (ROT13) is supported by the hint.
- No need for image steganography, as explicitly stated.

---

## Final Flag
```
sun{t0le_t0le_my_b3l0v3d!}
```

