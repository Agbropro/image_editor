# Image & GIF Resizing: Concepts, Math, and Pillow Resampling

This document explains how image resizing works, what resampling filters are available in Pillow, and the special concerns that arise when resizing animated GIFs.

---

## 1. Core Concepts

### 1.1 Pixels and Resolution

A digital image is a grid of **pixels**. Each pixel stores one or more numeric values that describe color and, sometimes, opacity.

- **Resolution**: The number of pixels in each dimension, e.g. $W \times H$.
- **Width ($W$)**: Number of pixels across.
- **Height ($H$)**: Number of pixels down.
- **Total pixels**: $W \times H$.

When you resize an image, you are creating a *new* grid of pixels from the old one. You cannot create real detail that was not there, only compute plausible new pixel values.

### 1.2 Scaling Factor

The **scale factor** $s$ tells us how much larger or smaller the output will be:

$$
W_{new} = s \cdot W_{old} \quad \text{and} \quad H_{new} = s \cdot H_{old}
$$

- $s > 1$: **Upscaling** (enlarging). New pixels are invented.
- $0 < s < 1$: **Downscaling** (shrinking). Multiple old pixels are merged into one.
- $s = 1$: No change.

If only one dimension is given and aspect ratio is preserved, the other dimension is computed proportionally:

$$
H_{new} = W_{new} \cdot \frac{H_{old}}{W_{old}}
$$

### 1.3 Aspect Ratio

The **aspect ratio** is the proportional relationship between width and height:

$$
\text{aspect ratio} = \frac{W}{H}
$$

**Maintaining aspect ratio** means keeping $\frac{W}{H}$ constant. If you change width but not height by the same factor, the image becomes stretched or squashed.

### 1.4 Coordinate Systems

Image coordinates are usually zero-indexed:

- Top-left pixel is $(0, 0)$.
- Bottom-right pixel is $(W - 1, H - 1)$.
- A pixel center can be thought of as $(x + 0.5, y + 0.5)$.

When resizing, we map coordinates from the output image back to the input image, because we want to ask: *"For this new pixel, what color should it be based on the old pixels?"*

---

## 2. The Mathematics of Resizing

Resizing is a **resampling** problem: we are sampling a discrete image at new positions.

### 2.1 Forward and Backward Mapping

Imagine we want to map a pixel $(x_{new}, y_{new})$ in the output image to a location $(x_{old}, y_{old})$ in the input image.

The simplest mapping is:

$$
x_{old} = \frac{W_{old}}{W_{new}} \cdot x_{new}
\quad \text{and} \quad
y_{old} = \frac{H_{old}}{H_{new}} \cdot y_{new}
$$

This is a **backward mapping**. We walk over every output pixel, find where it comes from in the input, and read a color.

### 2.2 The Problem: Rarely Lands on an Exact Pixel

Usually, $(x_{old}, y_{old})$ falls *between* four input pixels. The new pixel value must be estimated from nearby pixels. This estimation is called **interpolation**.

For example, if $(x_{old}, y_{old}) = (3.7, 5.2)$, it sits between pixels $(3, 5)$, $(4, 5)$, $(3, 6)$, and $(4, 6)$. The resampling filter decides how much each neighbor contributes.

### 2.3 Interpolation as a Weighted Sum

Most resampling can be written as:

$$
C_{new}(x, y) = \sum_{i, j} C_{old}(i, j) \cdot w(i, j, x, y)
$$

where:
- $C_{new}(x, y)$ is the new pixel color.
- $C_{old}(i, j)$ is an old pixel color.
- $w(i, j, x, y)$ is the **weight** of that old pixel at the target location.

The choice of $w$ defines the resampling method.

### 2.4 Separability

Most ilters are **separable**: they first filter horizontally, then vertically (or vice versa). This makes the math simpler and faster:

$$
C(x, y) = \sum_i \sum_j C(i, j) \cdot w_x(x - i) \cdot w_y(y - j)
$$

Pillow's filters are all separable.

### 2.5 Worked Examples

Below are concrete, hand-calculated examples so you can see the formulas in action.

#### Example 1: Scaling Factor

You have an image $100 \times 80$ and you want to double its size:

$$
W_{new} = 2 \cdot 100 = 200 \quad \text{pixels}
$$

$$
H_{new} = 2 \cdot 80 = 160 \quad \text{pixels}
$$

The output is $200 \times 160$.

#### Example 2: Preserving Aspect Ratio

You have an image $1200 \times 900$ and you want the new width to be $400$, maintaining aspect ratio:

$$
H_{new} = 400 \cdot \frac{900}{1200} = 400 \cdot 0.75 = 300
$$

The output is $400 \times 300$.

#### Example 3: Backward Mapping

You have an old image $W_{old}=8$, and you are resizing to $W_{new}=4$. Where in the old image does the new pixel $x_{new}=2$ come from?

$$
x_{old} = \frac{8}{4} \cdot 2 = 4
$$

New pixel 2 maps exactly to old pixel 4. No interpolation is needed.

Now ask the same question for $x_{new}=1$:

$$
x_{old} = \frac{8}{4} \cdot 1 = 2
$$

It also maps exactly. But for $W_{old}=8$ to $W_{new}=3$:

$$
x_{old} = \frac{8}{3} \cdot 1 \approx 2.67
$$

New pixel 1 comes from old position 2.67, which lies between old pixels 2 and 3. We must interpolate.

#### Example 4: BILINEAR Interpolation in 1D

You have two old pixel values:

- $f(2) = 100$
- $f(3) = 120$

You want the value at $x = 2.67$.

The fractional part is $\{x\} = 0.67$.

$$
f(2.67) = (1 - 0.67) \cdot 100 + 0.67 \cdot 120
$$

$$
f(2.67) = 0.33 \cdot 100 + 0.67 \cdot 120 = 33 + 80.4 = 113.4
$$

So the new pixel would be about **113** (rounded to an integer).

#### Example 5: Interpolation as a Weighted Sum

Imagine a tiny 2x2 image with these grayscale values:

```
10  20
30  40
```

You want the value at the exact center, which is equally distant from all four pixels. Each pixel contributes equally:

$$
C_{new} = \frac{10 + 20 + 30 + 40}{4} = \frac{100}{4} = 25
$$

This is the same idea that BOX filtering uses when downscaling.

#### Example 6: NEAREST

You have old pixels at integer positions $x=2$ (value 50) and $x=3$ (value 70). You want the value at $x = 2.4$.

Nearest neighbor rounds to the closest integer: $\text{round}(2.4) = 2$.

The new pixel gets the value of old pixel 2: **50**.

If the target had been $x = 2.6$, it would round to 3 and get **70**.

---

## 3. Pillow Resampling Filters

Pillow provides several resampling filters. They differ in:

- **Speed**: how many input pixels must be read.
- **Sharpness**: whether edges stay crisp or become soft.
- **Artifacts**: ringing, aliasing, blockiness, or blurring.
- **Purpose**: pixel art vs. photographs vs. general use.

### 3.1 NEAREST (Nearest Neighbor)

**Concept**: Pick the color of the single closest input pixel. No blending, no averaging.

Mathematically, for a target position $x$, it selects the input pixel whose center is closest:

$$
\text{nearest}(x) = \text{round}(x)
$$

**Use when**:
- Resizing **pixel art** or sprites.
- You want crisp, hard edges and no anti-aliasing.
- Upscaling small icons where blur is undesirable.

**Risks**:
- Produces jagged, blocky edges.
- Can create positional shifts because rounding always picks one side.
- Downscaling can drop detail because many input pixels are ignored.

---

### 3.2 BOX

**Concept**: Average all input pixels that fall inside the area covered by one output pixel. Imagine each output pixel as a box placed over the input image; take the average color inside that box.

For downscaling by factor $s < 1$, each output pixel covers approximately $1/s$ input pixels. BOX sums them and divides.

**Use when**:
- Downscaling images, especially by large factors.
- Creating thumbnails.
- You want a balance between speed and quality for reduction.

**Risks**:
- Slightly softer than higher-quality filters.
- Not ideal for upscaling.

---

### 3.3 BILINEAR (Linear Interpolation)

**Concept**: Fit a linear ramp between the four nearest pixels and sample along it. It blends the four nearest neighbors using weights based on distance.

In 1D, for a target $x$ between integer positions $i$ and $i+1$:

$$
f(x) = (1 - \{x\}) \cdot f(i) + \{x\} \cdot f(i+1)
$$

where $\{x\}$ is the fractional part of $x$.

**Use when**:
- General-purpose resizing.
- Slight downscaling or upscaling where speed matters more than ultimate quality.

**Risks**:
- Produces softer images than bicubic or lanczos.
- Can blur fine details.
- Better for photos than for graphics with sharp edges.

---

### 3.4 HAMMING

**Concept**: A windowed sinc approximation. It smooths the image while trying to preserve some sharpness. It applies a Hamming window to reduce ringing artifacts.

**Use when**:
- Downsizing images where you want less blur than bilinear but less ringing than sharper filters.

**Risks**:
- Less commonly used than LANCZOS or BICUBIC.
- Can still introduce mild smoothing.

---

### 3.5 BICUBIC

**Concept**: Use a cubic polynomial to interpolate between the 16 nearest pixels (a $4 \times 4$ neighborhood). It produces smoother results than bilinear.

The cubic kernel is steeper than linear, so it keeps edges sharper but can introduce **ringing** (halos) near strong edges.

**Use when**:
- General high-quality resizing, especially upscaling.
- Photographs and natural images.

**Risks**:
- **Ringing**: faint light/dark bands near sharp edges.
- Slower than bilinear.
- Not ideal for pixel art (makes edges fuzzy).

---

### 3.6 LANCZOS

**Concept**: Uses a **sinc function** windowed by a sinc function. It samples a larger neighborhood (a $6 \times 6$ or bigger area) and gives high weight to nearby pixels, tapering off smoothly.

The idealized kernel is:

$$
L(x) = \begin{cases}
\text{sinc}(x) \cdot \text{sinc}(x/a) & |x| < a \\
0 & \text{otherwise}
\end{cases}
$$

where $a$ is the window size (often 3 or 4, giving a $6 \times 6$ or $8 \times 8$ neighborhood in Pillow).

**Use when**:
- Highest-quality general resizing.
- Photographs where detail and smooth gradients matter.
- Downscaling where aliasing must be minimized.

**Risks**:
- **Ringing** near very high-contrast edges.
- Slower than bilinear or bicubic because it uses more pixels.
- Should not be used for pixel art (it anti-aliases and blurs crisp edges).

---

## 4. Quick Filter Summary

| Filter     | Neighborhood | Best For                         | Main Risk                       |
|------------|--------------|----------------------------------|----------------------------------|
| NEAREST    | 1 pixel      | Pixel art, sprites, icons        | Jagged edges, detail loss       |
| BOX        | Variable box | Thumbnails, downscaling          | Slightly soft                   |
| BILINEAR   | 4 pixels     | General use, speed               | Blur                            |
| HAMMING    | Windowed     | Downsizing                       | Mild smoothing                  |
| BICUBIC    | 16 pixels    | Photos, upscaling                | Ringing, halos                  |
| LANCZOS    | 36+ pixels   | High-quality photos, downscaling | Ringing, slower, not for pixel art |

---

## 5. Special Concerns for Animated GIFs

GIFs are not just single images. An animated GIF contains:

- Multiple frames.
- A **global color palette** (up to 256 colors).
- Optional local palettes per frame.
- Per-frame **duration** (how long the frame is shown).
- A **loop count**.
- **Disposal methods** for each frame.
- Optional **transparency** and **background color index**.

### 5.1 Frame Iteration

When Pillow opens an animated GIF, `ImageSequence.Iterator` yields each frame. Each frame may be:

- A full image.
- A partial update to the previous frame, relying on disposal and transparency to composite correctly.

If you process each frame independently, you must preserve the per-frame timing and disposal information.

### 5.2 Disposal Methods

Disposal tells the GIF player what to do with the current frame before drawing the next one.

- **0 (undefined / no disposal)**: No explicit instruction; the next frame is drawn over the current one.
- **1 (do not dispose)**: Leave the current frame visible. The next frame is drawn on top. This can create cumulative animations but may leave residuals if the next frame is transparent.
- **2 (restore to background)**: Clear the canvas to the **background color** before drawing the next frame. This prevents ghosting but requires the background color to be correct.
- **3 (restore to previous)**: Restore the canvas to the state before the current frame was drawn. Rarely used.

**When you see ghosting or residual images in transparent areas, the usual cause is using disposal 1 instead of 2, or failing to set a correct background/transparency.**

### 5.3 Transparency and Background

- **Transparency**: A palette index (0-255) that should be rendered as fully transparent. Stored in `image.info['transparency']`.
- **Background**: The palette index to clear the canvas to when disposal 2 is used. Stored in `image.info['background']`.

If you resize a frame but do not preserve the original image's `transparency` and `background`, transparent areas can become opaque or pick up wrong colors.

### 5.4 Resizing GIFs Correctly

A safe approach is:

1. Read the source GIF once and collect global metadata (`loop`, `transparency`, `background`).
2. Iterate frames.
3. For each frame, preserve its `duration`.
4. Resize the frame using an appropriate filter (often `NEAREST` for pixel-art GIFs, `LANCZOS` for photographic GIFs).
5. Before saving, attach the original global `transparency` and `background` to the first output frame (or pass them to `save()`).
6. Save with `save_all=True`, passing `duration`, `loop`, and `disposal`.
7. Use `disposal=2` for GIFs with transparent backgrounds to avoid residuals.

### 5.5 Why Resized GIFs Show Residuals

Common causes:

- **Lost transparency**: The original `image.info['transparency']` is not copied to the output. Transparent pixels become opaque, often picking up the background color.
- **Wrong disposal**: Using `disposal=1` with transparent frames causes the previous frame to remain visible behind transparent parts of the current frame.
- **Resampling transparent pixels**: Filters like LANCZOS can blend transparent edges with neighboring opaque colors, creating colored fringes.
- **Palette mismatch**: Each frame may have a different palette. If the global palette is recomputed incorrectly, colors shift.
- **Background color not matching transparency**: With `disposal=2`, the canvas is cleared to the background color. If that color is not the intended transparent color, the background shows through.

### 5.6 Frame Duration and Loop

- **Duration**: A list of milliseconds, one per frame. Tells the player how long each frame stays on screen.
- **Loop**: How many times the animation repeats. `0` means loop forever.

These must be passed to `save()` when writing the animated GIF, or the output will play at default speed (often 100 ms per frame) and may not loop.

---

## 6. Implementation Notes for This Project

- **Non-GIF images**: Use `LANCZOS` for highest quality. For thumbnails or downscaling, `BOX` or `BILINEAR` may be faster.
- **GIFs**:
  - Use `NEAREST` for pixel-art GIFs to preserve hard edges.
  - Use `LANCZOS` for photographic GIFs if edge softness is acceptable.
  - Always preserve `duration`, `loop`, `transparency`, `background`, and `disposal`.
  - Use `disposal=2` when transparency is involved.
  - Copy global `transparency` and `background` to the first output frame before calling `save()`.
- **Aspect ratio**: Always recalculate the missing dimension when `maintain_aspect_ratio=True`.
- **Metadata loss**: Resampling creates new pixels, so any per-frame `info` (especially transparency) must be manually carried over.

---

## 7. Decision Checklist

| Situation                          | Recommended Filter | Notes |
|------------------------------------|--------------------|-------|
| Pixel art / sprites                | NEAREST            | Keep edges crisp |
| Thumbnails / heavy downscale       | BOX or LANCZOS     | BOX is faster; LANCZOS is sharper |
| General photo resize               | LANCZOS            | Best overall quality |
| Photo upscaling                    | BICUBIC or LANCZOS | Watch for ringing |
| Real-time preview                  | BILINEAR           | Fast, acceptable quality |
| GIF with transparency              | NEAREST            | Avoid color fringes at transparent edges |

---

## 8. Glossary

- **Resampling**: Reconstructing a signal (image) at a different set of sample positions.
- **Interpolation**: Estimating unknown values from known neighbors.
- **Aliasing**: Visual artifacts (jaggies, moiré) caused by undersampling high-frequency detail.
- **Ringing**: Oscillating light/dark bands near sharp edges, common with sharp filters.
- **Disposal**: GIF playback instruction for clearing frames.
- **Palette**: A lookup table of up to 256 colors used by GIF frames.
