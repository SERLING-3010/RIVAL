// Chat del partido: solo lo ven quienes juegan o pitan este partido.

import { StyleSheet, Text, View } from 'react-native';

import type { MatchChatController } from '../../controllers/useMatchChat';
import { messageText } from '../../domain/chatModels';
import { formatLocal } from '../../domain/dateTime';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { TextField } from '../components/TextField';
import { colors, font, radius, space } from '../theme';

interface Props {
  controller: MatchChatController;
  onBack: () => void;
}

export function MatchChatScreen({ controller, onBack }: Props) {
  const busy = controller.action.busy;
  return (
    <Screen title="Chat del partido" onBack={onBack}>
      <Text style={styles.meta}>
        Solo lo ven los dos equipos y el árbitro. No compartas tu ubicación exacta ni datos personales.
      </Text>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(page) => (
          <>
            {page.messages.length === 0 ? <Text style={styles.meta}>Aún no hay mensajes.</Text> : null}
            {page.messages.map((m) => (
              <View key={m.id} style={[styles.bubble, m.mine ? styles.mine : null]}>
                <Text style={styles.author}>
                  {m.mine ? 'Tú' : m.author_name} · {formatLocal(m.created_at)}
                </Text>
                <Text style={m.deleted ? styles.deleted : styles.body}>{messageText(m)}</Text>
                {m.mine && !m.deleted ? (
                  <PrimaryButton
                    label="Borrar"
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleDelete(m.id)}
                  />
                ) : null}
              </View>
            ))}
            {page.writable ? (
              <>
                <TextField
                  label="Mensaje"
                  value={controller.draft}
                  onChangeText={controller.setDraft}
                  error={controller.draftError ?? undefined}
                />
                <PrimaryButton label="Enviar" disabled={busy} onPress={() => void controller.handleSend()} />
              </>
            ) : (
              <Text style={styles.meta}>
                El chat es de solo lectura: el partido se canceló o ya pasaron 48 horas.
              </Text>
            )}
          </>
        )}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.meta} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  bubble: {
    padding: space.sm,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    marginBottom: space.xs,
  },
  mine: { borderLeftWidth: 4, borderLeftColor: colors.accent },
  author: { color: colors.textMuted, fontSize: font.small },
  body: { color: colors.text, fontSize: font.body },
  deleted: { color: colors.textMuted, fontSize: font.body, fontStyle: 'italic' },
  meta: { color: colors.textMuted, fontSize: font.small },
});
