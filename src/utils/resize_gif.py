from PIL import Image, ImageSequence

def resize_pixel_art_gif(input_path, output_path, scale_factor=None, new_size=None):
    img = Image.open(input_path)
    frames = []
    durations = []
    
    # Calculate new dimensions
    orig_width, orig_height = img.size
    if scale_factor:
        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)
    elif new_size:
        new_width, new_height = new_size
    else:
        raise ValueError("Provide either scale_factor or new_size")

    # Process each frame
    for frame in ImageSequence.Iterator(img):
        # Resize using NEAREST to preserve crisp pixels
        resized_frame = frame.resize((new_width, new_height), Image.NEAREST)
        frames.append(resized_frame)
        durations.append(frame.info.get('duration', 100))

    # Save as a new animated GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=img.info.get('loop', 0),
        disposal=2 # Helps clear transparency correctly between frames
    )

# Example usage: double the size of the pixel art
resize_pixel_art_gif("/opt/personal/image_editor/data/images/1789725555439_1049/original.gif", "output_scaled.gif", scale_factor=2.0)