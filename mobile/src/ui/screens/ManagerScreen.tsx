// Modo manager del equipo: presupuesto en monedas RIVAL, plantilla con fichas y ofertas de traspaso.

import { StyleSheet, Text } from 'react-native';

import type { ManagerController } from '../../controllers/useManager';
import { TEAM_ROLE_LABEL } from '../../domain/labels';
import { canBeListed, coinReason, formatCoins, TRANSFER_STATUS_LABEL } from '../../domain/managerRules';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';
import { Screen } from '../components/Screen';
import { StateView } from '../components/StateView';
import { colors, font } from '../theme';

interface Props {
  controller: ManagerController;
  onOpenCard: (userId: number) => void;
  onMarket: (balance: number) => void;
  onBack: () => void;
}

export function ManagerScreen({ controller, onOpenCard, onMarket, onBack }: Props) {
  const busy = controller.action.busy;
  return (
    <Screen title="Modo manager" onBack={onBack}>
      <StateView state={controller.state} onRetry={controller.handleReload}>
        {(m) => (
          <>
            <Card
              title={`Presupuesto: ${formatCoins(m.balance)}`}
              subtitle="Monedas virtuales: no se compran ni se venden"
            >
              {m.history.slice(0, 5).map((e, i) => (
                <Text key={`${e.created_at}-${i}`} style={styles.line}>
                  {formatCoins(e.amount)} · {coinReason(e.reason)}
                </Text>
              ))}
            </Card>
            {m.is_admin ? (
              <PrimaryButton label="Ir al mercado de fichajes" onPress={() => onMarket(m.balance)} />
            ) : null}
            <Text style={styles.section} accessibilityRole="header">
              Plantilla
            </Text>
            {m.squad.map((p) => (
              <Card
                key={p.user_id}
                title={p.display_name}
                subtitle={`${TEAM_ROLE_LABEL[p.role]}${p.position ? ` · ${p.position}` : ''} · ${p.matches} PJ · ${p.goals} goles`}
                badge={p.listed ? 'Transferible' : undefined}
                onPress={() => onOpenCard(p.user_id)}
              >
                {m.is_admin && canBeListed(p) ? (
                  <PrimaryButton
                    label={p.listed ? 'Quitar del mercado' : 'Poner en el mercado'}
                    variant="secondary"
                    disabled={busy}
                    onPress={() => void controller.handleListed(p.user_id, !p.listed)}
                  />
                ) : null}
              </Card>
            ))}
            {m.offers_received.map((o) => (
              <Card
                key={`r${o.id}`}
                title={`${o.to_team.name} ofrece ${formatCoins(o.amount)} por ${o.player_name}`}
                badge={TRANSFER_STATUS_LABEL[o.status]}
              >
                {o.status === 'PENDING_OWNER' ? (
                  <>
                    <PrimaryButton
                      label="Aceptar oferta"
                      disabled={busy}
                      onPress={() => void controller.handleDecide(o.id, 'owner-accept')}
                    />
                    <PrimaryButton
                      label="Rechazar"
                      variant="secondary"
                      disabled={busy}
                      onPress={() => void controller.handleDecide(o.id, 'owner-reject')}
                    />
                  </>
                ) : null}
              </Card>
            ))}
            {m.offers_sent.map((o) => (
              <Card
                key={`s${o.id}`}
                title={`Ofreciste ${formatCoins(o.amount)} por ${o.player_name}`}
                subtitle={o.from_team.name}
                badge={TRANSFER_STATUS_LABEL[o.status]}
              >
                <PrimaryButton
                  label="Retirar oferta"
                  variant="secondary"
                  disabled={busy}
                  onPress={() => void controller.handleDecide(o.id, 'withdraw')}
                />
              </Card>
            ))}
          </>
        )}
      </StateView>
      {controller.action.message ? (
        <Text style={styles.line} accessibilityLiveRegion="polite">
          {controller.action.message}
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  section: { color: colors.text, fontSize: font.heading, fontWeight: '700' },
  line: { color: colors.text, fontSize: font.small },
});
