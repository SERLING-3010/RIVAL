import type { ChatMessage, ChatPage } from '../domain/chatModels';
import { request } from './httpClient';

export const chatApi = {
  read: (token: string, contractId: number, afterId: number) =>
    request<ChatPage>('GET', `/api/v1/contracts/${contractId}/chat`, {
      token,
      query: { after_id: String(afterId) },
    }),

  send: (token: string, contractId: number, text: string) =>
    request<ChatMessage>('POST', `/api/v1/contracts/${contractId}/chat`, { token, body: { text } }),

  remove: (token: string, messageId: number) =>
    request<{ id: number }>('POST', `/api/v1/chat/${messageId}/delete`, { token }),
};
