# Fully build working app to edit image using own website

# Frontend Requirements
- Language : Typescript
- Currently skipped

# BE Requirements
- Language : python
- Framework : Fastapi
- Features : 
    - Upload Image (single or multiple or from copy)
    - Save uploaded image in data/uploaded/{uploaded_image_id}.{ext}
    - uploaded_image_id -> generated from current BE timestamp + random integer
    - Resize image working like ezgif -> can resize gif