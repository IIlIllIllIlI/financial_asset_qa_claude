export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail || res.statusText, body);
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function apiGet(url: string) {
  const res = await fetch(url);
  return handleResponse(res);
}

export async function apiPost(url: string, body?: unknown) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handleResponse(res);
}

export async function apiPatch(url: string, body: unknown) {
  const res = await fetch(url, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiDelete(url: string) {
  const res = await fetch(url, { method: "DELETE" });
  return handleResponse(res);
}
