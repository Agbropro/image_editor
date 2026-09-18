from PIL import Image

image = Image.open("/home/agbropro/Downloads/primarina.gif")

print("Format:", image.format)
print("Size:", image.size)
print("Frames:", image.n_frames)

for i in range(image.n_frames):
    image.seek(i)
    print("Frame:", i, "Size:", image.size)
    
image.seek(91)
frame = image.copy()
frame.save("frame0.png")