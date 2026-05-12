export async function uploadDocument(file: File): Promise<{
  document_id: string;
  file_name: string;
  chunk_count: number;
  status: string;
}> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("/api/rag/upload", {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}
