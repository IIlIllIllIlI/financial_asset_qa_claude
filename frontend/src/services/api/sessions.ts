import { apiGet, apiPost, apiPatch, apiDelete } from "./client";
import type { Session, SessionDetail } from "@/types/session";

export async function fetchSessions(): Promise<Session[]> {
  return apiGet("/api/sessions");
}

export async function createSession(): Promise<Session> {
  return apiPost("/api/sessions");
}

export async function fetchSession(id: string): Promise<SessionDetail> {
  return apiGet(`/api/sessions/${id}`);
}

export async function updateSessionTitle(
  id: string,
  title: string
): Promise<Session> {
  return apiPatch(`/api/sessions/${id}/title`, { title });
}

export async function deleteSession(id: string): Promise<void> {
  return apiDelete(`/api/sessions/${id}`);
}
