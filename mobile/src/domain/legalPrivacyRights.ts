// Derechos, consultas y reclamos (Ley 1581 de 2012, arts. 8, 14, 15 y 16). Parte de la política (BORRADOR).

import type { LegalSection } from './legalTerms.ts';

export const PRIVACY_RIGHTS: LegalSection[] = [
  {
    title: 'Tus derechos',
    body:
      'Puedes conocer, actualizar y rectificar tus datos; pedir prueba de la autorización que diste; saber ' +
      'para qué se han usado; revocar la autorización o pedir que los suprimamos (salvo lo que debamos ' +
      'conservar por ley o por un contrato vigente); acceder a ellos gratis; y quejarte ante la ' +
      'Superintendencia de Industria y Comercio (SIC).',
  },
  {
    title: 'Cómo ejercerlos',
    body:
      'Desde la app, en «Mi cuenta», puedes descargar tus datos y eliminar tu cuenta. Para lo demás ' +
      '(corregir, preguntar, revocar o reclamar), escribe al correo del responsable con tu nombre, el ' +
      'correo de tu cuenta, lo que pides y, si es un reclamo, los hechos y los documentos que quieras ' +
      'aportar. Atiende estas solicitudes: [POR DEFINIR: persona o área].',
  },
  {
    title: 'Plazos',
    body:
      'Consultas: respondemos en máximo 10 días hábiles; si no alcanzamos, te avisamos y respondemos en ' +
      'máximo 5 días hábiles más. Reclamos: respondemos en máximo 15 días hábiles, prorrogables 8 más con ' +
      'aviso. Si a tu reclamo le falta información, te la pedimos dentro de los 5 días hábiles siguientes; ' +
      'si pasan 2 meses sin que la envíes, entenderemos que desististe.',
  },
  {
    title: 'Queja ante la SIC',
    body:
      'Antes de quejarte ante la Superintendencia de Industria y Comercio debes haber hecho la consulta o ' +
      'el reclamo ante nosotros.',
  },
  {
    title: 'Si eliminas tu cuenta',
    body:
      'Borramos tu correo, nombre, fecha de nacimiento, barrio, posición, sesiones, teléfonos y el texto ' +
      'de tus mensajes. Tus partidos y resultados quedan como de un «Jugador eliminado», porque también son ' +
      'el historial de otros equipos. El registro de auditoría se conserva por seguridad.',
  },
  {
    title: 'Vigencia',
    body:
      'Esta política rige desde [POR DEFINIR: fecha de inicio del piloto]. Guardamos tus datos mientras ' +
      'tengas tu cuenta y, después de eliminarla, solo lo anonimizado. Si cambiamos esta política, te lo ' +
      'mostraremos en la app y te pediremos aceptarla de nuevo.',
  },
];
