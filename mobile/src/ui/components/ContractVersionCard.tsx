import { StyleSheet, Text } from 'react-native';

import type { Contract, ContractVersion } from '../../domain/contractModels';
import { describeTerms } from '../../domain/contractRules';
import { formatLocal } from '../../domain/dateTime';
import { PLACE_LABEL, REFEREE_LABEL } from '../../domain/matchLabels';
import { colors, font } from '../theme';
import { Card } from './Card';

interface Props {
  contract: Contract;
  version: ContractVersion;
  title: string;
}

const sideName = (c: Contract, side: string) => (side === 'HOST' ? c.host.name : c.guest.name);

export function ContractVersionCard({ contract, version, title }: Props) {
  const t = version.terms;
  const signatures = version.signed_by.map((s) => sideName(contract, s)).join(' y ') || 'nadie';
  return (
    <Card title={`${title} · v${version.version}`} subtitle={formatLocal(t.kickoff_at)}>
      <Text style={styles.line}>
        {REFEREE_LABEL[t.referee_mode]} · {PLACE_LABEL[t.place_kind]}
      </Text>
      {t.place_note ? <Text style={styles.line}>Lugar: {t.place_note}</Text> : null}
      {describeTerms(t, contract.host.name, contract.guest.name).map((line) => (
        <Text key={line} style={styles.line}>
          {line}
        </Text>
      ))}
      {version.note ? <Text style={styles.meta}>“{version.note}”</Text> : null}
      <Text style={styles.meta}>Firmada por: {signatures}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  line: { color: colors.text, fontSize: font.small },
  meta: { color: colors.textMuted, fontSize: font.small },
});
