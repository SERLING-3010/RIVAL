import { describe, expect, jest, test } from '@jest/globals';
import { fireEvent, render, screen } from '@testing-library/react-native';

import type { MatchChatController } from '../src/controllers/useMatchChat';
import type { ChatMessage, ChatPage } from '../src/domain/chatModels';
import { MatchChatScreen } from '../src/ui/screens/MatchChatScreen';
import { idleAction } from './fixtures';

const msg = (id: number, over: Partial<ChatMessage> = {}): ChatMessage => ({
  id,
  author_id: 2,
  author_name: 'Luis',
  body: `Mensaje ${id}`,
  created_at: '2026-11-24T20:00:00Z',
  deleted: false,
  mine: false,
  ...over,
});

function controller(page: ChatPage, over: Partial<MatchChatController> = {}): MatchChatController {
  return {
    state: { kind: 'success', data: page },
    draft: 'Llego tarde',
    draftError: null,
    action: idleAction(),
    setDraft: jest.fn(),
    handleSend: jest.fn(async () => undefined),
    handleDelete: jest.fn(async () => undefined),
    handleReload: jest.fn(),
    ...over,
  };
}

describe('MatchChatScreen', () => {
  test('muestra mensajes, borra solo los propios y envía', async () => {
    const page: ChatPage = {
      contract_id: 7,
      writable: true,
      messages: [msg(1), msg(2, { mine: true, body: 'Mío' }), msg(3, { deleted: true, body: null })],
    };
    const c = controller(page);
    await render(<MatchChatScreen controller={c} onBack={jest.fn()} />);
    expect(screen.getByText('Mensaje 1')).toBeTruthy();
    expect(screen.getByText('Mensaje eliminado')).toBeTruthy();
    expect(screen.getAllByText('Borrar')).toHaveLength(1);
    await fireEvent.press(screen.getByText('Borrar'));
    expect(c.handleDelete).toHaveBeenCalledWith(2);
    await fireEvent.press(screen.getByText('Enviar'));
    expect(c.handleSend).toHaveBeenCalled();
  });

  test('si el chat se cerró, no deja escribir', async () => {
    const c = controller({ contract_id: 7, writable: false, messages: [] });
    await render(<MatchChatScreen controller={c} onBack={jest.fn()} />);
    expect(screen.getByText('Aún no hay mensajes.')).toBeTruthy();
    expect(screen.queryByText('Enviar')).toBeNull();
  });
});
