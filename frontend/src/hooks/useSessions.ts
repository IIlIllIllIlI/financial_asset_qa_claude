import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchSessions,
  createSession,
  fetchSession,
  deleteSession,
} from "@/services/api/sessions";

export function useSessions() {
  return useQuery({
    queryKey: ["sessions"],
    queryFn: fetchSessions,
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}

export function useSessionDetail(sessionId: string | null) {
  return useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => fetchSession(sessionId!),
    enabled: !!sessionId,
  });
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}
