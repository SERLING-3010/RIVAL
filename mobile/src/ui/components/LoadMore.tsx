import { StyleSheet, Text } from 'react-native';

import { colors, font } from '../theme';
import { PrimaryButton } from './PrimaryButton';

interface Props {
  hasMore: boolean;
  loading: boolean;
  error: string | null;
  onPress: () => void;
}

export function LoadMore({ hasMore, loading, error, onPress }: Props) {
  return (
    <>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {hasMore ? (
        <PrimaryButton label="Cargar más" variant="secondary" loading={loading} onPress={onPress} />
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  error: { color: colors.danger, fontSize: font.small },
});
