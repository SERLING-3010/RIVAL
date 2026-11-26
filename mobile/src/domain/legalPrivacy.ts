// Política de tratamiento de datos de RIVAL (Sprint 27, Ley 1581 de 2012 y Decreto 1377 de 2013, art. 13).
// BORRADOR: falta completar los datos del responsable y que alguien con formación jurídica lo revise.

import type { LegalSection } from './legalTerms.ts';
import { PRIVACY_RIGHTS } from './legalPrivacyRights.ts';

const PRIVACY_DATA: LegalSection[] = [
  {
    title: 'Responsable del tratamiento',
    body:
      'Nombre: [POR DEFINIR]. Cédula o NIT: [POR DEFINIR]. Domicilio y dirección: [POR DEFINIR]. ' +
      'Correo: [POR DEFINIR]. Teléfono: [POR DEFINIR].',
  },
  {
    title: 'Qué datos guardamos',
    body:
      'Correo, nombre visible, fecha de nacimiento, ciudad, barrio, posición, deportes y roles. También ' +
      'tus equipos, partidos, goles, valoraciones que recibes (sin decir quién las dio), mensajes del chat ' +
      'de cada partido y la hora de tus check-ins. Nunca guardamos tu ubicación exacta. No pedimos datos ' +
      'sensibles (salud, origen, creencias, biometría) ni datos de menores de edad.',
  },
  {
    title: 'Para qué los usamos (finalidades)',
    body:
      'Crear y proteger tu cuenta; armar partidos, ligas y copas; mostrar tu carta, tu historial y el de ' +
      'tu equipo; avisarte de pendientes; mantener la convivencia y atender reportes; y llevar un registro ' +
      'de quién firmó, reportó o aceptó cada cosa para resolver dudas. No vendemos tus datos ni los usamos ' +
      'para publicidad.',
  },
  {
    title: 'Cómo los tratamos',
    body:
      'Los recogemos cuando te registras y mientras usas la app; los guardamos, consultamos, actualizamos ' +
      'y, si lo pides, los suprimimos. Solo acceden las personas que operan RIVAL, con contraseña, y los ' +
      'datos viajan cifrados (HTTPS).',
  },
  {
    title: 'Quién ve qué',
    body:
      'Tu ficha (nombre, posición, carta y estadísticas) la ven otros usuarios. Tu correo y tu fecha de ' +
      'nacimiento no se muestran a nadie. La alineación de tu equipo solo la ve tu equipo.',
  },
  {
    title: 'Encargados y transmisión al exterior',
    body:
      'Para funcionar usamos proveedores que tratan datos por nuestra cuenta: el servidor donde vive la ' +
      'base de datos [POR DEFINIR] y, si aceptas notificaciones, Expo y Apple o Google, que pueden estar ' +
      'fuera de Colombia. A ellos solo les llega lo necesario: los avisos no llevan nombres, equipos, ' +
      'marcadores, horarios ni lugares.',
  },
];

export const PRIVACY: LegalSection[] = [...PRIVACY_DATA, ...PRIVACY_RIGHTS];
