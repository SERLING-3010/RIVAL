# App de deportes — Sprint 0: estrategia, investigación y backlog

Nov 23, 2026 · @sergio

## 1. Resumen, misión y comité

La app conecta equipos amateur de cualquier deporte con rivales, árbitros y canchas cercanas por GPS, y deja que el director técnico (o el capitán, si no hay DT) negocie y cierre el partido con condiciones configurables. Es el Sprint 0: solo investigación, ideación y plan; no hay código y nada se construye hasta tu aprobación.

**Nombre:** RIVAL, confirmado por el dueño al crear el repositorio `github.com/SERLING-3010/RIVAL` (23/11/2026). Antes de publicar en tiendas hay que revisar disponibilidad de marca en la SIC \[POR VERIFICAR\].

**Clasificación de la tarea:** descubrimiento + investigación + arquitectura (sin implementación).

**Misión adaptada del prompt FIIN.** Se conserva el método (Plan → Test → Implement → Review → Verify, Scrum con 5 loops, etiquetas de evidencia, una sola pregunta, nada "terminado" sin prueba ejecutada). Cambia el dominio: de contabilidad y créditos a partidos, equipos y reservas.

**Comité adaptado** (revisores del Loop 4):

- Principal Software Architect y Desarrollador Full Stack móvil
- Senior UI/UX Product Designer (móvil, accesibilidad, mapas)
- Ingeniero de Datos/DBA con experiencia geoespacial (PostGIS)
- Ingeniero de IA (emparejamiento y nivel de equipos, moderación)
- Abogado de protección de datos y consumo (Ley 1581, menores, términos)
- Contador/Tributario solo si se cobran comisiones o reservas en la app
- CISO, QA/SRE y Gerente de Proyectos
- Asesor deportivo (reglamentos por deporte y arbitraje amateur)

**Ceremonia del Sprint 0**

- **Product Owner:** la meta es validar el núcleo "mi equipo encuentra rival cerca y el partido queda pactado". Todo lo demás (pagos, torneos, rankings) se prioriza detrás de ese flujo.
- **Scrum Master:** reglas innegociables heredadas — máximo 150 líneas por archivo, capas domain/services/controllers/ui, cero `any`, `import type`, español en docs e inglés en código, dinero en decimal exacto. Impedimento: no existe repositorio; se creará en el Sprint 1 con aprobación.
- **Developers:** investigaron competidores, normas y stack; proponen arquitectura móvil-primero, tres conceptos de interfaz y el backlog del MVP.

## 2. Loop 1 — Investigación y descubrimiento

El mercado está lleno de apps de fútbol para "armar el partido entre amigos", pero casi ninguna reúne en un solo flujo equipo con roles, rival por GPS, árbitro y cancha. Ese es el hueco que RIVAL puede ocupar.

### 2.1 Inventario real

- **Código:** no existe repositorio de esta app \[VERIFICADO EN ENTORNO 23/11/2026: no hay carpeta conectada ni proyecto previo\]. Es un proyecto nuevo; el stack se propone en ADR (sección 5).
- **Lo que sí existe:** tu experiencia con FastAPI, React + TypeScript y la metodología FIIN, que se reutilizan.
- **No puedo inspeccionar aún:** dispositivos reales, cuentas de Google Play/App Store, ni cotizaciones de mapas o pagos con tu NIT.

### 2.2 Benchmark (consultado 23/11/2026)

| Producto | Fortaleza observada | Limitación / oportunidad para RIVAL |
| --- | --- | --- |
| [Playtomic](https://playtomic.com/es) | Red de clubes, reserva de pista, partidos abiertos y sistema de niveles | Centrado en raqueta; de fútbol por equipos con DT no hay evidencia \[INFERENCIA\] |
| [Timpik](https://apps.apple.com/es/app/timpik-jugar-padel-y-futbol/id433422542) | Reserva de pistas, buscar jugadores de tu nivel, rankings, torneos | Orientado a jugadores sueltos, no a equipos que retan a equipos |
| [TeamSnap](https://apps.apple.com/mx/app/teamsnap/id393048976) | Gestión de equipo para entrenadores y padres; plan pago | Gestiona tu equipo, no busca rival por cercanía |
| [Spond](https://www.spond.com/en-us/news-and-blog/5-best-sports-team-management-apps/) | Equipos, agenda y pagos; gratis | Igual: sin emparejamiento de rivales ni árbitros |
| [TorneAR](https://ar.linkedin.com/in/agustin-saladino) (Argentina) | Ranking de equipos amateur, buscar rivales y jugadores | Solo fútbol y una ciudad; sin árbitros ni canchas |
| [FútbolYa](https://www.iproup.com/startups/68586-chau-grupos-de-whatsapp-crean-una-app-para-organizar-partidos-de-futbol) (Argentina) | Publica el partido y reserva cancha; el jugador paga su cupo | Partidos por cupo individual, no equipo contra equipo |
| [Micrapp](https://apps.apple.com/ly/app/micrapp/id6502481302) (Colombia, microfútbol) | Partidos cercanos y buscar al jugador que falta | Un solo deporte; sin reseñas suficientes para medir tracción |
| [easycancha](https://www.portafolio.co/emprendimiento/la-plataforma-para-encontrar-y-reservar-canchas-deportivas-en-colombia-617649) (Colombia) | Reserva de escenarios y gestión para dueños de canchas | Lado establecimiento; posible aliado o competidor |
| [Vive IDRD](https://idrd.gov.co/noticias/el-idrd-impulsa-la-transformacion-digital-con-un-registro-mas-rapido-en-el-portal) (Bogotá) | Reserva de canchas públicas desde el celular | Solo escenarios públicos de Bogotá; no conecta equipos |

**Hallazgo clave:** existe demanda real — los partidos amateur se caen por falta de jugadores y se coordinan por grupos de WhatsApp, según los fundadores de FútbolYa. Ningún producto revisado combina los cuatro actores (equipo, rival, árbitro, cancha) en un solo contrato de partido \[INFERENCIA sobre la muestra revisada, no sobre todo el mercado\].

### 2.3 Matriz normativa inicial

| Norma / fuente | Aplica a | Implicación técnica | Estado |
| --- | --- | --- | --- |
| [Ley 1581 de 2012](https://www.unidadvictimas.gov.co/wp-content/uploads/Documentos/ley/Ley_1581_2012.pdf) | Todos los datos personales | Autorización previa, política de tratamiento, derechos del titular. Dato personal es cualquier información asociable a una persona determinable | \[VERIFICADO EN FUENTE\] |
| Ley 1581 art. 7 + [Decreto 1377 de 2013](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646) | Jugadores menores de 18 | El artículo 7 prohíbe en principio tratar datos de menores; la Corte (C-748/2011) lo permite si responde a su interés superior y con autorización del representante legal ([PwC](https://www.pwc.com/co/es/assets/document/brochure_proteccion_de_datos_s.pdf)) | \[VERIFICADO EN FUENTE\]; flujo exacto \[POR VERIFICAR\] con abogado |
| Ubicación GPS | Usuarios y equipos | Es dato personal; revela hábitos ([Dialnet](https://dialnet.unirioja.es/descarga/articulo/7497926.pdf)). Minimizar precisión y retención | \[INFERENCIA\] |
| [Política de Google Play: ubicación en segundo plano](https://support.google.com/googleplay/android-developer/answer/9799150?hl=es) | App Android | Solo se aprueba si es función principal; preferir ubicación en primer plano | \[VERIFICADO EN FUENTE\] |
| Fotos de jugadores | Perfiles | Una imagen identificable es dato personal; con menores se recomienda no usarla ([Uniandes](https://derecho.uniandes.edu.co/wp-content/uploads/2025/09/datos-personales-v3.pdf)) | \[VERIFICADO EN FUENTE\] |
| Estatuto del Consumidor (Ley 1480 de 2011) | Reservas y pagos | Derecho de retracto, información de precios, reclamos | \[POR VERIFICAR\] |
| Facturación electrónica DIAN | Solo si la app cobra comisión | Facturar la comisión de la plataforma | \[POR VERIFICAR\] con contador |
| Lineamientos SIC sobre IA ([Circular 002 de 2024](https://sedeelectronica.sic.gov.co/sites/default/files/normativa/Circular%20Externa%20No.%20002%20del%2021%20de%20agosto%20de%202024.pdf)) | Emparejamiento con IA | Transparencia sobre decisiones automatizadas | \[VERIFICADO EN FUENTE\] existencia; alcance \[POR VERIFICAR\] |

### 2.4 Lista POR VERIFICAR

- Flujo legal exacto para registrar menores (quién autoriza, cómo se verifica la edad).
- Si cobrar comisión por reservas o árbitros convierte a la app en intermediario con deberes de consumo o tributarios.
- Tarifas vigentes de Google Maps Platform, Mapbox y pasarelas (Wompi, Mercado Pago, PayU) para tu volumen.
- Si las ligas o federaciones exigen requisitos a árbitros "certificados" (o solo se publica la declaración del árbitro).

## 3. Cómo se adapta el prompt FIIN a esta app

Se adopta todo el método y se reemplaza lo que era propio de contabilidad y escritorio. Esta tabla es el registro de conflictos resueltos (equivalente a la sección 21 de FIIN).

| Regla FIIN | Decisión en RIVAL | Motivo |
| --- | --- | --- |
| Scrum, 5 loops, PO/SM/Devs, Plan-First, etiquetas de evidencia | Se adopta igual | Es el método, no el dominio |
| Máx. 150 líneas, capas domain/services/controllers/ui, cero `any` | Se adopta igual | Aplica a cualquier código |
| App de escritorio Windows, shell MDI, barra de estado | Se descarta: móvil primero (Android + iOS) y panel web para canchas y administración | El GPS y "buscar rival cerca" viven en el teléfono |
| Offline-first con BD local cifrada | Parcial: caché local y cola de acciones, pero el emparejamiento requiere red | Buscar rivales es por definición en línea |
| Acceso universal a módulos con controles por operación | Se adopta: todos navegan todo; las acciones se controlan por rol dentro del equipo (DT, capitán, jugador) en el backend | Mismo principio: ocultar un botón no es seguridad |
| Aprobación 4 ojos (initiated\_by ≠ approved\_by) | Se adopta para: aceptar un reto, cambiar condiciones pactadas, registrar resultado (ambos equipos confirman) y transferir la administración | Evita resultados o acuerdos falsos |
| Trazabilidad nominal y auditoría encadenada con SHA-256 | Se adopta para el contrato del partido, resultados, sanciones y pagos | Disputas entre equipos son el riesgo principal |
| Decimal exacto, nunca float, para dinero | No hay dinero dentro de la app (pagos fuera, decisión del dueño). Las monedas RIVAL son enteros virtuales sin valor real; las tarifas de referencia se guardan en Decimal; la app no maneja dinero apostado entre equipos (juego de suerte y azar, Coljuegos \[POR VERIFICAR\]); las coordenadas sí usan double/geography | Las coordenadas no son dinero |
| Contabilidad NIIF, DIAN, usura, libranzas, papelería B/N, POS | Se descarta salvo que se cobre comisión (entonces facturación electrónica) | No es el dominio |
| Marca blanca por empresa (5.7) | Se reemplaza por perfiles de establecimiento con datos propios | Las canchas son los "clientes empresa" de la app |
| IA local y supervisada | Se adopta el principio: la IA sugiere rivales y detecta abuso; no sanciona ni expulsa sin una persona | Igual que FIIN: la IA recomienda, no decide |
| Script PowerShell del Loop 5 | Se adopta desde el Sprint 1 (Sprint 0 no genera código) | No hay archivos que escribir aún |
| Centro de salud del sistema | Se adopta con invariantes propias (sección 7) | Misma idea, otras reglas |

## 4. Alcance funcional por módulo

El corazón del producto es el **contrato de partido**: un documento vivo que dos equipos negocian (deporte, modalidad, fecha, cancha, árbitro, reglas, costos) y que ambos administradores firman. Todo lo demás alimenta o ejecuta ese contrato.

### 4.1 Registro por rol (primer ingreso)

Decisión del dueño (23/11/2026): al entrar por primera vez la persona elige cómo se registra, y cada rol arranca con su propio menú de inicio. Todos indican **para qué deporte(s)** se registran.

| Rol al registrarse | Datos mínimos | Primeras opciones |
| --- | --- | --- |
| Jugador | Nombre visible, fecha de nacimiento (≥ 18), deportes, posición, barrio y ciudad | Buscar equipo · Crear equipo · Marcarse como agente libre |
| Director técnico | Igual que jugador + experiencia opcional | Crear equipo · Buscar equipo que necesite DT |
| Árbitro | Deportes, ciudad y barrios de cobertura, disponibilidad, certificados opcionales | Buscar liga · Aparecer en el directorio de árbitros |
| Establecimiento deportivo | Nombre o razón social, NIT o cédula, dirección, barrio y ciudad, deportes, canchas, horarios y tarifas de referencia | Registrar canchas · Publicar disponibilidad |

Reglas:

- Una persona, una cuenta. Después puede **agregar otro rol** desde su perfil (un jugador que también arbitra) sin crear otra cuenta.
- Jugador y DT, una vez tienen equipo: **Buscar liga · Crear liga**.
- Cada jugador ve siempre **Mi equipo** como pestaña principal: plantilla, próximos partidos, convocatorias y resultados.
- Solo mayores de 18 por ahora (decisión del dueño): la fecha de nacimiento se valida al registrarse.

### 4.2 Equipos y roles

- Crear equipo por deporte y modalidad (fútbol 5/7/8/11, microfútbol, baloncesto 3x3/5x5, béisbol/softbol, voleibol y los que se agreguen por configuración, no por código).
- Plantilla: invitar jugadores por enlace, QR o usuario; aceptar o rechazar; dorsal, posición, estado (activo, lesionado, inactivo).
- **Administrador del equipo:** el DT si existe; si no, el capitán. Regla del dominio: siempre hay exactamente un administrador activo. Si el DT sale, la administración pasa al capitán automáticamente y queda en auditoría. Se puede nombrar un **subadministrador** para cuando el titular no responde.
- Permisos del administrador: proponer y aceptar retos, editar condiciones, reservar cancha, contratar árbitro, convocar jugadores, registrar resultado. Los jugadores ven todo y confirman su asistencia.

### 4.2.1 Ligas

Propuesta para tu duda de quién administra la liga: la administra quien la crea, como **organizador**, y puede nombrar coorganizadores. Así nadie depende de un "dueño oficial" y la regla es la misma que con el DT y el capitán.

- **Quién crea:** cualquier jugador o DT con equipo, o un árbitro. Al crearla queda como organizador (administrador único hasta que nombre a otros).
- **Qué tiene una liga:** deporte, modalidad, ciudad y barrios, temporada, equipos inscritos, **cuerpo arbitral**, canchas sede (establecimientos aliados), calendario y tabla de posiciones.
- **Inscripción de equipos:** el DT o capitán solicita entrar; el organizador aprueba o rechaza.
- **Cuerpo arbitral:** un árbitro busca la liga y solicita unirse; el organizador lo aprueba. La liga puede tener muchos árbitros. El organizador puede nombrar a uno como **coordinador arbitral**, que asigna árbitros a los partidos de la liga según su disponibilidad.
- **Decisiones sensibles con dos personas** cuando la liga tiene dos o más organizadores: expulsar un equipo, cambiar reglas a mitad de temporada o corregir un resultado ya cerrado.
- **Si el organizador abandona:** pasa a un coorganizador; si no hay, la liga queda "sin organizador" y los equipos pueden votar uno nuevo \[SUPUESTO, ajustable\].

### 4.2.2 Modo manager: "un juego de lo real"

Tu idea: que manejar el equipo se sienta como Football Manager, pero con partidos y personas reales. Propuesta:

- **Plantilla con fichas de jugador:** foto opcional, posición, dorsal y estadísticas **reales** sacadas de los partidos confirmados (partidos, goles o puntos, asistencias, tarjetas, asistencia a convocatorias). Nada de atributos inventados.
- **Valoración:** media de las notas que ponen el DT y los compañeros después de cada partido, más el resultado del equipo. Se muestra el número de votos para que se vea qué tan confiable es.
- **Monedas RIVAL (virtuales):** cada equipo tiene un presupuesto que gana jugando, ganando y con juego limpio. **No se compran con dinero real ni se cambian por dinero.** Si algún día se vendieran, habría que revisar la parte legal antes (juegos de suerte y azar y consumo) \[POR VERIFICAR\].
- **Mercado de fichajes:** el DT marca jugadores como transferibles; otro DT hace una oferta en monedas; el DT dueño acepta o contraoferta. **El jugador siempre debe aceptar** el traspaso: es una persona real, no se le cambia de equipo sin su consentimiento.
- **Agentes libres:** jugadores sin equipo, buscables por deporte, posición y cercanía; el DT les envía una propuesta.
- **Préstamos para un partido:** pedir prestado "el que falta" a otro equipo por un solo partido, con aceptación del jugador y de su DT.
- **Ventanas de traspasos** por liga y temporada, para que los equipos no cambien de plantilla en mitad de una fase final.
- **Alineación y convocatoria:** formación visual según el deporte y la modalidad; el jugador confirma si va.

### 4.3 Buscar rival por cercanía, barrio o ciudad

Decisión del dueño (23/11/2026): la búsqueda **no muestra la ubicación exacta** de nadie. Los resultados se presentan por cercanía, barrio o ciudad.

- El buscador tiene tres alcances: **Cerca de mí**, **Mi barrio** y **Mi ciudad**.
- Cada equipo, árbitro y establecimiento tiene un **barrio y una ciudad** elegidos de una lista. Para calcular distancias se usa el punto central del barrio, nunca el de una persona.
- "Cerca de mí" usa el GPS solo en ese momento para saber en qué barrio estás; la posición no se guarda. Si no das permiso de ubicación, eliges el barrio a mano y todo funciona igual.
- Las distancias se muestran por rangos ("menos de 2 km", "2 a 5 km", "más de 5 km") junto al nombre del barrio, no como un punto en el mapa.
- Los establecimientos sí muestran su dirección, porque es un negocio que quiere ser encontrado.
- El administrador publica una **solicitud de partido** (deporte, modalidad, fecha y hora, alcance, nivel y condiciones) o hace un **reto directo**. Los equipos cercanos envían ofertas y contraofertas, como en InDriver.
- Resultados ordenados por cercanía, nivel parecido, reputación y disponibilidad.

### 4.4 Condiciones configurables del partido

- Modalidad, duración y tiempos, número de cambios, uniformes (colores para evitar choque), balón, superficie.
- Reparto de costos: cancha 50/50, la paga el retador, cada uno lo suyo; árbitro igual.
- Reglas especiales por deporte (ej. innings en béisbol, cuartos en baloncesto), desde plantillas editables.
- Política de cancelación y de inasistencia (W.O.) pactada antes de firmar.
- Cada cambio después de firmar requiere aceptación del otro administrador (versión nueva del contrato, con antes y después).

### 4.4.1 Partido informal: sin árbitro y en cancha libre

Decisión del dueño (23/11/2026): los equipos pueden jugar **sin árbitro** y en un **lugar informal** (parque público, cancha del barrio, cancha propia), no solo en un establecimiento registrado.

- En el contrato, el árbitro es una condición más: **Con árbitro** (se invita uno) o **Sin árbitro, arbitraje entre los equipos**. Si es sin árbitro, se puede pactar quién cobra las faltas dudosas (por ejemplo, el capitán del equipo que defiende).
- El lugar tiene dos tipos: **Establecimiento registrado** (con confirmación de franja) o **Lugar informal**: nombre ("Parque de X, cancha de arena"), barrio, ciudad y una referencia opcional. No necesita confirmación de nadie.
- Los lugares informales que se usan seguido se guardan como **lugares frecuentes** del equipo para elegirlos con un toque. Los que usan varios equipos pueden proponerse al catálogo como "cancha pública".
- La app avisa que en un lugar informal nadie garantiza disponibilidad: si el parque está ocupado, los equipos lo resuelven entre ellos.
- Sin árbitro, el resultado vale cuando **ambos administradores lo confirman**. Si no coinciden, el partido pasa a disputa y no suma a estadísticas ni a la tabla de una liga hasta que se resuelva.
- Una liga puede exigir árbitro en sus partidos oficiales; los amistosos pueden ser informales.

### 4.5 Árbitros

- Perfil con deportes, ciudad y barrios de cobertura, disponibilidad y certificados declarados (documento adjunto, verificación manual).
- Se unen al **cuerpo arbitral de una o varias ligas** (sección 4.2.1) y aparecen en el directorio general por cercanía, barrio o ciudad.
- Un DT o el coordinador arbitral de la liga los invita al contrato del partido; el árbitro acepta o rechaza.
- **La tarifa y el pago se arreglan fuera de la app** (decisión del dueño). La app solo muestra la tarifa de referencia que el árbitro declara y quién la asume según el contrato.
- Después del partido el árbitro registra el resultado y las incidencias (tarjetas, expulsiones); ambos equipos lo califican.

### 4.6 Establecimientos deportivos independientes

- Perfil del establecimiento: nombre, dirección, barrio y ciudad, deportes, canchas, superficie, fotos, horarios y tarifas de referencia.
- Calendario de franjas: el dueño marca disponible u ocupada. Un DT solicita una franja ligada al contrato del partido y el establecimiento la confirma o rechaza; la base de datos impide dos confirmaciones para la misma franja.
- **El pago de la cancha se hace fuera de la app** (decisión del dueño): en efectivo, transferencia o como lo acuerden.
- Puede aliarse con ligas como **cancha sede**.
- Los escenarios públicos pueden aparecer como "cancha pública" con enlace al sistema oficial de reserva.

### 4.7 Día del partido y después

- Convocatoria, recordatorios, check-in en la cancha, chat del partido (solo participantes).
- Resultado confirmado por ambos administradores o por el árbitro; si no coinciden, pasa a disputa.
- Estadísticas, historial, reputación y nivel del equipo (rating tipo Glicko-2, sección 5).

### 4.8 Moderación y confianza

- Reportes por agresión, inasistencia o perfiles falsos; bloqueo; sanciones aplicadas por una persona con motivo y apelación.

## 5. Arquitectura y stack comparado

Recomendación: app móvil con React Native + Expo y TypeScript, backend FastAPI + PostgreSQL/PostGIS, y un panel web React + Vite para establecimientos y administración. Reutiliza lo que ya dominas de FIIN y comparte tipos y reglas entre móvil y web.

### 5.1 Cliente móvil

| Opción | A favor | En contra | Decisión |
| --- | --- | --- | --- |
| React Native + Expo | TypeScript y React que ya usas; Expo SDK 58 con RN 0.88 es la versión estable de octubre de 2026 ([MobiLoud](https://www.mobiloud.com/blog/flutter-vs-expo)); EAS Build y actualizaciones OTA | Algunas librerías nativas requieren "dev build" | **Recomendada** |
| Flutter | Rendimiento de dibujo muy consistente | Dart: lenguaje nuevo para ti; no comparte código con el panel web React | Descartada por costo de aprendizaje |
| PWA (solo web) | Una sola base, sin tiendas | Ubicación y notificaciones más limitadas en iOS \[POR VERIFICAR\] | Solo para el panel de canchas |

### 5.2 Backend, datos y tiempo real

- **FastAPI + Python 3.12 + SQLAlchemy**, mismas convenciones de FIIN (Decimal para dinero, contratos tipados, idempotencia).
- **PostgreSQL + PostGIS:** columnas `geography(Point,4326)` con índice GiST y búsquedas por radio con `ST_DWithin`, que usa el índice y es más rápida que `ST_Distance` ([PostGIS](https://postgis.net/documentation/tips/st-dwithin)). Row Level Security como segunda barrera.
- **Tiempo real:** WebSockets en FastAPI para ofertas y chat; Redis para pub/sub y límites de peticiones.
- **Notificaciones push:** Expo Notifications (FCM/APNs).
- **Mapas:** comparar Google Maps Platform, Mapbox y OpenStreetMap (MapLibre) por costo y términos \[POR VERIFICAR precios vigentes\].
- **Pagos:** fuera del alcance por decisión del dueño (23/11/2026): árbitros y canchas se pagan por fuera. Si más adelante se quiere cobrar, se evaluarían pasarelas con split. Wompi (Grupo Bancolombia) y Mercado Pago (Split de Pagos 1:1, disponible en Colombia) son candidatos ([Mercado Pago](https://www.mercadopago.com.co/developers/es/docs/split-payments/split-1-1/overview)); comisiones y requisitos \[POR VERIFICAR\].

### 5.3 Emparejamiento y nivel

- Fase 1, reglas deterministas: distancia, deporte, modalidad, franja horaria, diferencia de nivel máxima.
- Fase 2, rating por equipo con **Glicko-2**, que además del nivel mide la incertidumbre (RD) y la volatilidad; un equipo nuevo tiene RD alta y el sistema lo sabe ([Wikipedia](https://www.wikipedia.com/wiki/Mark_Glickman)). Glicko-2 ya se ha aplicado a ligas de fútbol ([arXiv 2310.11459](https://arxiv.org/pdf/2310.11459)).
- IA (P2): sugerencias explicables ("te sugerimos a X porque está a 2,3 km, juega los sábados y su nivel es parecido"), nunca sanciones automáticas.

### 5.4 ADR propuestos (para aprobar)

- **ADR-001:** móvil con React Native + Expo; panel web React + Vite.
- **ADR-002:** monolito modular FastAPI (no microservicios) con módulos `identity`, `teams`, `matchmaking`, `match_contract`, `referees`, `venues`, `bookings`, `payments`, `audit`, `health`.
- **ADR-003:** PostgreSQL + PostGIS como única fuente de verdad; Redis solo para caché y colas.
- **ADR-004:** ubicación solo en primer plano en el MVP (sin rastreo en segundo plano), alineado con la política de Google Play.
- **ADR-005:** rating Glicko-2 por equipo y modalidad, desde la Fase 2.

## 6. Modelo de datos y reglas de dominio

El contrato de partido es una máquina de estados: cada transición la hace un actor identificado y queda en auditoría, y ningún estado posterior a "firmado" se alcanza sin la aceptación de ambos administradores.

&#91;embedded content: estados del contrato de partido · 8 pasos, 2 salidas\]

La cancelación también puede ocurrir en Negociando o Firmado; se dibuja solo desde Listo para no cruzar líneas. Un cambio de condiciones después de firmar crea una versión nueva y vuelve a Negociando. "Listo para jugar" solo exige el lugar acordado: el árbitro es opcional y el lugar puede ser informal (sección 4.4.1).

### 6.1 Entidades principales (borrador del ERD)

| Entidad | Campos clave | Regla |
| --- | --- | --- |
| `user_account` | id, nombre visible, fecha de nacimiento, verificado | Una persona, una cuenta; ≥ 18 años |
| `user_role` | user\_id, rol (PLAYER, COACH, REFEREE, VENUE\_OWNER), deportes | Varios roles por cuenta |
| `neighborhood` | id, nombre, ciudad, centro (`geography`) | Catálogo; las distancias salen de aquí, no de personas |
| `team` | id, deporte, modalidad, barrio, presupuesto de monedas | Exactamente un administrador activo |
| `team_membership` | team\_id, user\_id, rol (DT, capitán, jugador, subadmin), dorsal, estado | Permisos validados en el backend |
| `league` | id, deporte, modalidad, ciudad, temporada, estado | El creador es organizador |
| `league_staff` | league\_id, user\_id, rol (organizador, coorganizador, coordinador arbitral) | Siempre al menos un organizador |
| `league_team` / `league_referee` | league\_id, team\_id o user\_id, estado de solicitud | Aprobación del organizador |
| `match_request` / `match_offer` | equipo, ventana horaria, alcance (cerca, barrio, ciudad), condiciones | Versionadas; nunca se editan |
| `match_contract` | equipos, liga opcional, lugar (establecimiento o informal), modo de arbitraje (con o sin árbitro), estado, versión, condiciones (JSON validado), firmas | Firmado ⇒ inmutable salvo nueva versión aceptada |
| `venue` / `court` / `slot` | establecimiento, cancha, barrio, franja, tarifa de referencia (`Decimal`) | Una franja, una confirmación |
| `match_result` | contract\_id, marcador, confirmaciones, árbitro | Válido con ambas confirmaciones o la del árbitro |
| `transfer_offer` (P1) | jugador, equipo origen y destino, monedas, aceptaciones | Requiere aceptación del DT dueño y del jugador |
| `coin_ledger` (P1) | team\_id, movimiento (entero), motivo, referencia | Solo asientos de suma y resta; saldo nunca negativo |
| `audit_event` | initiated\_by, approved\_by, actor\_type, antes/después, hash | Encadenado; nadie lo edita desde la app |

## 7. Seguridad, privacidad, menores y centro de salud

El mayor riesgo legal de RIVAL no es el dinero sino la combinación de ubicación + menores de edad. Por eso el MVP propone **solo mayores de 18** y deja las categorías juveniles para cuando un abogado valide el flujo.

### 7.1 Ubicación

- La app **nunca muestra la ubicación exacta** de una persona ni de un equipo: solo barrio, ciudad y rango de distancia (sección 4.3).
- Lo que se guarda es el barrio y la ciudad elegidos de una lista; las distancias se calculan desde el centro del barrio.
- El GPS es opcional y solo "mientras se usa la app": sirve para sugerir tu barrio y se descarta. Nunca en segundo plano.
- Los rangos de distancia y el límite de búsquedas impiden adivinar dónde vive alguien haciendo muchas búsquedas desde puntos distintos.
- El check-in en la cancha (P1) compara la distancia al establecimiento y guarda solo "llegó / no llegó".

### 7.2 Menores de edad

Decisión del dueño (23/11/2026): **solo mayores de 18 por ahora**. El registro valida la fecha de nacimiento y rechaza a menores con un mensaje claro. Las categorías juveniles quedan fuera del producto hasta una revisión legal (Ley 1581 art. 7 y Decreto 1377 de 2013).

### 7.3 Ley 1581 en la app

- Política de tratamiento y aviso de privacidad versionados; cada autorización queda registrada.
- Derechos del titular desde la app (conocer, actualizar, revocar, suprimir) con radicado y plazo.
- Inventario de terceros que reciben datos (mapas, push, pasarela de pago), visible para el usuario.
- Transparencia de IA: cada sugerencia indica que la generó un algoritmo y con qué datos.

### 7.4 Seguridad de la aplicación (checklist heredado de FIIN 9.3)

- Contraseñas con Argon2id según OWASP, o inicio de sesión con Google/Apple; verificación por SMS o correo.
- Tokens en almacenamiento seguro del sistema (Keychain / Keystore), nunca en AsyncStorage plano.
- Anti-IDOR: toda consulta filtra por equipo y rol en el servidor; pruebas que cambian IDs.
- Rate limiting en login, búsquedas por radio (evita triangular la ubicación de alguien) y ofertas.
- Fotos y documentos: validar tipo por contenido, tamaño máximo, quitar metadatos EXIF (incluida la ubicación).

### 7.5 Auditoría

Evento nominal con `initiated_by`, `approved_by`, `actor_type`, antes/después y hash encadenado para: contrato de partido y sus versiones, resultados, transferencias de administración, sanciones, reservas, traspasos y movimientos de monedas.

### 7.6 Centro de salud del sistema — invariantes deterministas

- Un equipo sin administrador activo, o con dos (S1).
- Doble reserva de la misma cancha y franja (S0).
- Partido "jugado" sin resultado confirmado tras 48 h (S3).
- Contrato firmado modificado sin aceptación del rival (S0).
- Traspaso de jugador aplicado sin su aceptación, o presupuesto de monedas negativo (S0).
- Picos de búsquedas por radio desde una cuenta (posible rastreo, S1).

## 8. UX: tres conceptos de interfaz

Propongo el concepto B como base y tomar del A el mapa como vista secundaria. Los tres son ideas, no pantallas construidas; el prototipo navegable llega en el Sprint 1.

| Concepto | Idea central | A favor | En contra |
| --- | --- | --- | --- |
| **A. Radar** | Pantalla principal = mapa de barrios con el número de equipos, árbitros y canchas en cada uno (sin pines de personas); deslizas una tarjeta desde abajo para retar | Se entiende al instante el "cerca de mí" | Mapas llenos son lentos y exponen zonas; difícil con muchas solicitudes |
| **B. Mesa de negociación** | Pantalla principal = "Mis partidos" como tarjetas de contrato con estado (buscando rival, oferta recibida, falta árbitro, falta cancha, confirmado). Cada tarjeta muestra qué falta y el siguiente paso | Lleva al usuario a cerrar el partido; encaja con el contrato de 4 firmas | Menos "vistoso" que un mapa en la primera impresión |
| **C. Feed de retos** | Muro de solicitudes abiertas cercanas, como un tablero de anuncios, con ofertas en tiempo real estilo InDriver | Genera actividad y descubrimiento | Ruido; favorece a quien publica más, no al mejor emparejamiento |

**Reglas de interfaz heredadas de FIIN (adaptadas a móvil):**

- Los 7 estados en cada vista que lee o cambia datos: cargando (skeleton), vacío, error con reintento, éxito, sin conexión (qué quedó en cola), conflicto (el rival cambió las condiciones mientras editábamos) y **pendiente de aprobación** ("esperando que el DT rival acepte").
- Una acción primaria por pantalla; acciones destructivas (cancelar partido, expulsar jugador) separadas y con confirmación.
- Accesibilidad WCAG AA: contraste ≥ 4.5:1, objetivos táctiles ≥ 44 pt, lector de pantalla, nada solo por color (estado con icono + texto).
- Color de acento único; verde = confirmado, ámbar = pendiente, rojo = cancelado o en disputa.
- Cifras de dinero en formato colombiano ($ 120.000) y distancias en km con un decimal.
- Nunca bloquear el hilo de la interfaz: búsquedas, mapas e imágenes en segundo plano con progreso.

## 9. Brechas, riesgos, MVP y Sprint Backlog

El MVP (P0) es un día real de uso: cada persona se registra con su rol, un DT arma su equipo, encuentra rival por cercanía o barrio, pactan condiciones, acuerdan el lugar (cancha de un establecimiento o un parque) y, si quieren, un árbitro (pagado por fuera), juegan y confirman el resultado, sin WhatsApp.

### 9.1 Brechas y riesgos

| Módulo | Estado actual | Brecha | Prioridad | Riesgo |
| --- | --- | --- | --- | --- |
| Repositorio | Creado en GitHub por el dueño; esta sesión aún no tiene acceso \[VERIFICADO EN ENTORNO\] | Dar acceso y crear la estructura base | Crítica | Trabajar sin poder inspeccionar el repo |
| Registro por rol | Sin implementar | Onboarding de 4 roles con deportes | Crítica | Cuentas falsas de árbitros o establecimientos |
| Búsqueda por cercanía/barrio/ciudad | Sin implementar | Catálogo de barrios y búsqueda por radio desde su centro | Crítica | Adivinar la ubicación de alguien con muchas búsquedas |
| Contrato de partido | Sin implementar | Máquina de estados + versiones + aprobación de ambos | Crítica | Disputas por condiciones cambiadas |
| Ligas y cuerpo arbitral | Sin implementar | Crear, buscar, inscribir equipos y árbitros, organizador | Alta | Ligas abandonadas sin organizador |
| Establecimientos | Sin implementar | Perfil + calendario sin doble confirmación | Alta | Pocos establecimientos al inicio |
| Modo manager | Sin implementar | Fichas, estadísticas, monedas, fichajes | Media (P1) | Traspasos sin consentimiento; monedas vendidas por fuera |
| Acceso universal | Por diseñar | Todos navegan; el backend controla acciones por rol | Alta | Un jugador aceptando retos en nombre del equipo |
| Pagos | Fuera del alcance (decisión del dueño) | Ninguna | No aplica | Que alguien espere que la app garantice el pago: aclararlo en la interfaz |

### 9.2 MVP propuesto

- **P0 (imprescindible):** registro por rol (jugador, DT, árbitro, establecimiento) con deportes; Mi equipo; crear y buscar equipo, solicitudes de unión y agentes libres; DT o capitán como administrador con traspaso automático; búsqueda de rival por cercanía, barrio o ciudad; reto directo y solicitud abierta con ofertas; contrato de partido con condiciones y firmas; directorio de árbitros y establecimientos con invitación y confirmación de franja; ligas básicas (crear, buscar, inscribir equipos y árbitros, organizador); resultado confirmado por ambos; auditoría y centro de salud básico. Sin dinero dentro de la app.
- **P1 (importante):** modo manager completo (fichas con estadísticas reales, valoraciones, monedas RIVAL, mercado de fichajes, préstamos, ventanas de traspasos), calendario y tabla de liga, coordinador arbitral, rating Glicko-2, reputación y reportes, chat del partido, check-in.
- **P2 (futuro):** torneos eliminatorios, alineaciones tácticas avanzadas, sugerencias con IA, logros e insignias, categorías juveniles (solo tras revisión legal), otros países.

### 9.3 Sprint Backlog inicial

| ID | Historia de usuario | Criterio de aceptación verificable | Prioridad |
| --- | --- | --- | --- |
| RIV-001 | Como persona, quiero registrarme como jugador, DT, árbitro o establecimiento y elegir mis deportes | Rol y deportes obligatorios; menores de 18 rechazados; prueba pytest + tsc | P0 |
| RIV-002 | Como usuario, quiero agregar otro rol a mi cuenta | Una sola cuenta con varios roles; sin duplicar persona | P0 |
| RIV-003 | Como jugador, quiero buscar un equipo o crearlo | Al crearlo queda como administrador; al buscar, solicita unirse y el administrador aprueba | P0 |
| RIV-004 | Como jugador, quiero ver Mi equipo | Plantilla, próximos partidos y resultados en la pestaña principal | P0 |
| RIV-005 | Como equipo sin DT, quiero que el capitán administre | Si el DT sale, el capitán pasa a administrador con evento de auditoría | P0 |
| RIV-006 | Como jugador sin equipo, quiero aparecer como agente libre | Buscable por deporte, posición y barrio; el DT envía propuesta y el jugador acepta | P0 |
| RIV-007 | Como DT, quiero buscar rivales por cercanía, barrio o ciudad | Nunca se devuelve ubicación exacta; distancias por rangos; prueba que lo verifica | P0 |
| RIV-008 | Como DT, quiero retar o publicar una solicitud abierta y recibir ofertas | Solo administradores aceptan (control en backend); ofertas versionadas | P0 |
| RIV-009 | Como DT, quiero pactar condiciones y que ambos firmemos | Contrato firmado inmutable; cambios = nueva versión aceptada por el rival | P0 |
| RIV-010 | Como árbitro, quiero buscar ligas y unirme a su cuerpo arbitral | Solicitud aprobada por el organizador; el árbitro aparece en la liga | P0 |
| RIV-011 | Como DT, quiero crear o buscar una liga e inscribir mi equipo | El creador es organizador; inscripción aprobada por el organizador | P0 |
| RIV-012 | Como establecimiento, quiero registrar canchas y franjas | Ninguna franja con dos confirmaciones (restricción en BD + prueba de concurrencia) | P0 |
| RIV-013 | Como equipos, queremos confirmar el resultado | Válido con ambas confirmaciones o la del árbitro; si no, disputa | P0 |
| RIV-014 | Como usuario, quiero ver quién hizo cada cambio | Central de actividad por partido, equipo y liga con antes/después | P0 |
| RIV-015 | Como DT, quiero fichar jugadores con monedas virtuales | Oferta → acepta DT dueño → **acepta el jugador**; nunca dinero real | P1 |
| RIV-016 | Como jugador, quiero ver mis estadísticas reales | Calculadas solo de partidos con resultado confirmado | P1 |

## 10. Roadmap, verificación y gate de aprobación

El Sprint 0 termina aquí: no se escribe código hasta que apruebes este documento y respondas la pregunta del punto 10.4.

### 10.1 Roadmap de Sprints

&#91;embedded content: roadmap · 6 fases, 5 gates\]

La duración de cada Sprint se fija al aprobar el Sprint 1, con tu disponibilidad real de horas; no se ponen fechas sin ese dato.

### 10.2 Loop 4 — Verificación y QA del Sprint 0

| Verificación | Resultado |
| --- | --- |
| Conteo de líneas por archivo | NO APLICA: no hay código |
| `npm run build` / `tsc -b` | NO EJECUTADO: no existe proyecto |
| `pytest` | NO EJECUTADO: no existe backend |
| Fuentes citadas con enlace y fecha | Hecho: consultadas el 23/11/2026 |
| Revisión independiente legal (menores, ubicación, consumo) | PENDIENTE: requiere abogado humano |
| Revisión de afirmaciones | Ninguna afirmación de "cumplimiento legal garantizado"; lo no confirmado queda \[POR VERIFICAR\] |

### 10.3 Loop 5 — Review y retrospectiva

- No hay script de PowerShell en este Sprint porque no hay archivos que escribir. El repositorio ya existe en GitHub (`SERLING-3010/RIVAL`); el Sprint 1 creará en él `backend/`, `mobile/` y `web_admin/`. Si trabajas en Windows, el script del Loop 5 clonará o actualizará el repo local, guardará copias `.bak` antes de reemplazar, no usará `Remove-Item -Recurse` y terminará con el build.
- Retrospectiva: tus decisiones quitaron los dos riesgos legales más grandes (menores y pagos). El nuevo riesgo es el **tamaño** del producto con ligas y modo manager; por eso el mercado de fichajes y las monedas quedan en P1.

### 10.4 Decisiones del dueño y supuestos

**Decidido por el dueño (23/11/2026):**

1. Búsqueda por cercanía, barrio o ciudad, sin ubicación exacta.
2. Registro por rol (jugador, DT, árbitro, establecimiento) con deportes; ligas; modo manager tipo Football Manager.
3. Repositorio público en GitHub: `SERLING-3010/RIVAL` (solo tiene un README; un commit inicial).
4. Sin modelo de ingresos por ahora: la app es gratuita.
5. Pagos a árbitros y establecimientos fuera de la app.
6. Solo mayores de 18.
7. Partidos informales: árbitro opcional y lugar informal (parque público, cancha de barrio) además de establecimientos.

**Supuestos que quedan (reversibles):** ciudad piloto Barranquilla; Android y iOS; la liga la administra quien la crea, con coorganizadores; las monedas RIVAL son virtuales y no se compran ni se venden.

**Pregunta abierta:** ninguna que cambie la arquitectura. Para empezar el Sprint 1 solo faltan tu aprobación y que esta sesión pueda ver el repositorio.

### 10.5 Fuentes consultadas (23/11/2026)

Playtomic, Timpik, TeamSnap, Spond, TorneAR, FútbolYa, Micrapp, easycancha, Vive IDRD, Ley 1581 de 2012, Decreto 1377 de 2013, guía de PwC, Uniandes, Dialnet, Circular SIC 002 de 2024, política de ubicación de Google Play, PostGIS, MobiLoud (Expo vs Flutter), Mercado Pago Split, arXiv 2310.11459 y Glicko-2. Cada enlace está en la tabla o párrafo donde se usa.
