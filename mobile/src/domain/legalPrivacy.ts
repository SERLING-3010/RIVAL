// Política de tratamiento de datos de RIVAL (Sprint 27, Ley 1581 de 2012).
// BORRADOR: debe revisarlo un abogado antes del piloto (responsable, contacto y plazos legales).

import type { LegalSection } from './legalTerms.ts';

export const PRIVACY: LegalSection[] = [
  {
    title: 'Qué datos guardamos',
    body:
      'Correo, nombre visible, fecha de nacimiento, ciudad, barrio, posición, deportes y roles. También ' +
      'tus equipos, partidos, goles, valoraciones que recibes (sin decir quién las dio), mensajes del chat ' +
      'de cada partido y la hora de tus check-ins. Nunca guardamos tu ubicación exacta.',
  },
  {
    title: 'Para qué los usamos',
    body:
      'Para armar partidos y ligas, mostrar tu carta y tu historial, avisarte de pendientes y mantener la ' +
      'convivencia. No vendemos tus datos ni los usamos para publicidad.',
  },
  {
    title: 'Avisos en tu teléfono',
    body:
      'Si aceptas notificaciones, el aviso pasa por Expo y por Apple o Google. Por eso solo dice qué tipo ' +
      'de cosa te espera, sin nombres, equipos, marcadores, horarios ni lugares.',
  },
  {
    title: 'Quién ve qué',
    body:
      'Tu ficha (nombre, posición, carta y estadísticas) la ven otros usuarios. Tu correo y tu fecha de ' +
      'nacimiento no se muestran a nadie. La alineación de tu equipo solo la ve tu equipo.',
  },
  {
    title: 'Tus derechos',
    body:
      'Puedes conocer, actualizar, rectificar y suprimir tus datos, y revocar esta autorización. Desde ' +
      '«Mis datos» puedes descargarlos o eliminar tu cuenta.',
  },
  {
    title: 'Si eliminas tu cuenta',
    body:
      'Borramos tu correo, nombre, fecha de nacimiento, barrio, posición, sesiones, teléfonos y el texto ' +
      'de tus mensajes. Tus partidos y resultados quedan como de un «Jugador eliminado», porque también son ' +
      'el historial de otros equipos. El registro de auditoría se conserva por seguridad.',
  },
  {
    title: 'Responsable',
    body:
      'Responsable del tratamiento: [POR DEFINIR antes del piloto: nombre, cédula o NIT, dirección y correo de ' +
      'contacto para ejercer tus derechos].',
  },
];
