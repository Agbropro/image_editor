// All backend calls live in this file so the UI components stay easy to read.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const API_PREFIX = `${API_BASE_URL}/api/v1`;

export type ImageInfo = {
  image_id: string;
  filename: string;
  format: string;
  width: number;
  height: number;
  frames: number;
};

export type ResizeResult = {
  image_id: string;
  version: number;
  width: number;
  height: number;
  frames: number;
};

async function readError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return body.detail ?? "The server returned an error.";
  } catch {
    return `Request failed with status ${response.status}.`;
  }
}

export async function uploadImage(file: File): Promise<ImageInfo> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_PREFIX}/images`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export async function resizeImage(
  imageId: string,
  values: { width?: number; height?: number; scale?: number; maintain_aspect_ratio: boolean },
): Promise<ResizeResult> {
  const response = await fetch(`${API_PREFIX}/images/${imageId}/resize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export function imageViewUrl(imageId: string, version?: number): string {
  const cacheBuster = version === undefined ? "" : `?version=${version}`;
  return `${API_PREFIX}/images/${imageId}/view${cacheBuster}`;
}

export function imageDownloadUrl(imageId: string): string {
  return `${API_PREFIX}/images/${imageId}/download`;
}
