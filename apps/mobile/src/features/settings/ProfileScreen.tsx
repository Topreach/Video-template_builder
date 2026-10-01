import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Body, Eyebrow, Page, Title } from '../../shared/Components';
import { palette } from '../../shared/theme';

type Props = { onSignIn: () => void };
export function ProfileScreen({ onSignIn }: Props) {
  return <Page><Eyebrow>YOUR SPACE</Eyebrow><Title>Make it yours.</Title><Body>Set up your creative defaults. An account is optional.</Body>
    <View style={styles.profileCard}><View style={styles.avatar}><Text style={styles.avatarText}>A</Text></View><View style={styles.profileCopy}><Text style={styles.profileTitle}>Creator profile</Text><Text style={styles.profileMeta}>Optional · no account yet</Text></View><Text style={styles.action}>Set up</Text></View>
    <SettingsGroup title="YOUR APP">
      <Setting icon="▣" title="Creation defaults" detail="Format, captions, export quality" onPress={() => {}} />
      <Setting icon="♧" title="Notifications" detail="Off until you choose" onPress={() => {}} />
      <Setting icon="◇" title="Privacy & media" detail="No server upload in this UI spike" onPress={() => {}} />
      <Setting icon="◉" title="Accessibility" detail="Text size, motion, captions" onPress={() => {}} />
    </SettingsGroup>
    <SettingsGroup title="ACCOUNT">
      <Setting icon="＋" title="Sign in or create account" detail="Optional · for cloud backup" onPress={onSignIn} />
      <Setting icon="○" title="Plan & billing" detail="No subscription at launch" onPress={() => {}} />
    </SettingsGroup>
    <Text style={styles.buildNote}>MOBILE UI SPIKE · SETTINGS ARE SAMPLE CONTENT</Text>
  </Page>;
}

function SettingsGroup({ title, children }: React.PropsWithChildren<{ title: string }>) {
  return <View style={styles.group}><Text style={styles.groupTitle}>{title}</Text>{children}</View>;
}
function Setting({ icon, title, detail, onPress }: { icon: string; title: string; detail: string; onPress: () => void }) {
  return <Pressable onPress={onPress} style={styles.row} accessibilityRole="button"><View style={styles.settingIcon}><Text style={styles.settingGlyph}>{icon}</Text></View><View style={styles.rowCopy}><Text style={styles.rowTitle}>{title}</Text><Text style={styles.rowDetail}>{detail}</Text></View><Text style={styles.chevron}>›</Text></Pressable>;
}

const styles = StyleSheet.create({
  profileCard: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: 12, backgroundColor: '#FFF', borderColor: palette.line, borderWidth: 1, borderRadius: 12, marginTop: 19 },
  avatar: { width: 39, height: 39, borderRadius: 20, backgroundColor: '#E2DEFF', alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#5146B7', fontSize: 15, fontWeight: '700' },
  profileCopy: { flex: 1 },
  profileTitle: { color: palette.ink, fontSize: 11, fontWeight: '700' },
  profileMeta: { color: '#8A8894', fontSize: 9, marginTop: 3 },
  action: { color: palette.accent, fontSize: 9, fontWeight: '700' },
  group: { marginTop: 22 },
  groupTitle: { color: '#92909D', fontSize: 8, letterSpacing: 1.2, fontWeight: '700', marginLeft: 3, marginBottom: 6 },
  row: { minHeight: 54, flexDirection: 'row', alignItems: 'center', gap: 10, borderBottomWidth: 1, borderBottomColor: '#EEEDEF', paddingHorizontal: 3 },
  settingIcon: { width: 29, height: 29, borderRadius: 9, backgroundColor: palette.accentSoft, alignItems: 'center', justifyContent: 'center' },
  settingGlyph: { color: palette.accent, fontSize: 14 },
  rowCopy: { flex: 1, gap: 3 },
  rowTitle: { color: palette.ink, fontSize: 10, fontWeight: '700' },
  rowDetail: { color: '#898793', fontSize: 8 },
  chevron: { color: '#A09EAA', fontSize: 18 },
  buildNote: { textAlign: 'center', fontSize: 7, letterSpacing: 1, color: '#A09EAA', fontWeight: '700', marginTop: 25 },
});
