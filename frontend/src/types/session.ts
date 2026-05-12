export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail {
  session: Session;
  messages: ChatMessageItem[];
}

export interface ChatMessageItem {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}
