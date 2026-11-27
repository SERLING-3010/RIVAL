// Chat del partido (Sprint 14): solo participantes; la app consulta cada pocos segundos.

export const CHAT_MAX_LENGTH = 500;
export const CHAT_POLL_MS = 10_000;

export interface ChatMessage {
  id: number;
  author_id: number;
  author_name: string;
  body: string | null; // null si su autor lo borró
  created_at: string;
  deleted: boolean;
  mine: boolean;
}

export interface ChatPage {
  contract_id: number;
  writable: boolean;
  messages: ChatMessage[];
}

/** Une mensajes ya vistos con los nuevos, sin repetir y en orden de llegada. */
export function mergeMessages(current: ChatMessage[], incoming: ChatMessage[]): ChatMessage[] {
  const byId = new Map(current.map((m) => [m.id, m]));
  for (const m of incoming) byId.set(m.id, m);
  return [...byId.values()].sort((a, b) => a.id - b.id);
}

export function lastId(messages: ChatMessage[]): number {
  return messages.length === 0 ? 0 : Math.max(...messages.map((m) => m.id));
}

export function messageText(m: ChatMessage): string {
  return m.deleted || m.body === null ? 'Mensaje eliminado' : m.body;
}

/** Error del borrador antes de enviarlo, o null si se puede enviar. */
export function draftError(text: string): string | null {
  const clean = text.trim();
  if (clean.length === 0) return 'Escribe un mensaje.';
  if (clean.length > CHAT_MAX_LENGTH) return `Máximo ${CHAT_MAX_LENGTH} caracteres.`;
  return null;
}
