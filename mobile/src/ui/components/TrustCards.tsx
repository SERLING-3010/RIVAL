// Tarjetas de confianza en el inicio: suspensión vigente, mis sanciones y cola de moderación.

import type { ModerationMe } from '../../domain/moderationModels';
import { activeSuspension } from '../../domain/moderationModels';
import { formatLocal } from '../../domain/dateTime';
import { Card } from './Card';

interface Props {
  me: ModerationMe | null;
  onMySanctions: () => void;
  onModeration: () => void;
}

export function TrustCards({ me, onMySanctions, onModeration }: Props) {
  if (me === null) return null;
  const suspension = activeSuspension(me, new Date());
  return (
    <>
      {suspension ? (
        <Card
          title="Tu cuenta está suspendida"
          subtitle={`${suspension.ends_at ? `Hasta ${formatLocal(suspension.ends_at)}. ` : ''}Puedes ver la app y apelar.`}
          badge="Suspendida"
          onPress={onMySanctions}
        />
      ) : null}
      {!suspension && me.sanctions.length > 0 ? (
        <Card
          title="Mis sanciones"
          subtitle="Advertencias y suspensiones, con su apelación"
          onPress={onMySanctions}
        />
      ) : null}
      {me.is_moderator ? (
        <Card title="Moderación" subtitle="Reportes y apelaciones por revisar" onPress={onModeration} />
      ) : null}
    </>
  );
}
