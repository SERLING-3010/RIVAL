// Términos de uso de RIVAL (Sprint 27). BORRADOR: debe revisarlo un abogado antes del piloto.
// La versión debe coincidir con la del backend (legal_rules.TERMS_VERSION).

export const TERMS_VERSION = '2026-11-25.2';

export interface LegalSection {
  title: string;
  body: string;
}

export const TERMS: LegalSection[] = [
  {
    title: 'Qué es RIVAL',
    body:
      'RIVAL ayuda a armar partidos entre equipos aficionados, organizar ligas y llevar el historial ' +
      'de cada equipo y jugador. Es un borrador de términos para el piloto y puede cambiar.',
  },
  {
    title: 'Solo mayores de 18',
    body:
      'Para usar RIVAL debes tener 18 años o más. Al registrarte declaras que tu fecha de nacimiento es ' +
      'real. Si descubrimos que una cuenta es de un menor, la cerramos.',
  },
  {
    title: 'Sin dinero dentro de la app',
    body:
      'RIVAL no cobra, no recibe pagos y no maneja dinero de nadie. Los árbitros y las canchas se pagan ' +
      'por fuera, como lo acuerden los equipos. Las monedas RIVAL son virtuales: se ganan jugando y no se ' +
      'compran, no se venden ni se cambian por dinero.',
  },
  {
    title: 'Contratos de partido',
    body:
      'Un contrato de partido es un acuerdo entre equipos aficionados para jugar. RIVAL guarda quién ' +
      'propuso, firmó y reportó cada cosa, con un registro que no se puede alterar, para resolver dudas.',
  },
  {
    title: 'Convivencia',
    body:
      'No se permiten insultos, acoso, discriminación ni suplantación. Puedes reportar a una persona o un ' +
      'mensaje; el equipo de moderación puede advertir, suspender o cerrar cuentas.',
  },
  {
    title: 'Tu ubicación',
    body:
      'RIVAL nunca muestra dónde estás. Los equipos se encuentran por barrio y ciudad. El check-in en la ' +
      'cancha usa tu ubicación una sola vez para comprobar que llegaste, y no la guarda.',
  },
  {
    title: 'Tu cuenta',
    body:
      'Puedes descargar tus datos o eliminar tu cuenta desde «Mis datos». Al eliminarla, borramos lo que ' +
      'te identifica y tus partidos quedan como de un «Jugador eliminado».',
  },
];
