// frontend/app/types.ts

export interface Message {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  session_id: string;
  context_found: boolean;   // new field from the fixed backend
}