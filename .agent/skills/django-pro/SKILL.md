---
name: django-pro
description: Habilidad avanzada para el manejo exhaustivo de Django 5.x a nivel súper senior. Instruye al agente sobre patrones arquitectónicos avanzados, vistas asíncronas, Django REST Framework (DRF), Celery, optimización de ORM y seguridad.
---

# Django Pro (Nivel Súper Senior)

Esta habilidad capacita al agente para desarrollar, refactorizar y arquitectar aplicaciones web y APIs utilizando Django 5.x y su ecosistema (DRF, Celery, Redis, PostgreSQL) siguiendo las mejores prácticas de la industria a nivel súper senior.

## Cuándo usar esta habilidad

- Al iniciar, estructurar o rediseñar proyectos complejos en Django de manera escalable.
- Cuando se soliciten optimizaciones de rendimiento y eficiencia en la base de datos (con el ORM de Django).
- Al diseñar o refactorizar APIs RESTful utilizando Django REST Framework (DRF).
- Para la implementación de tareas en segundo plano pesadas utilizando Celery.
- Cuando se implementen características modernas como vistas asíncronas (async views) de Django 5.x.

## Principios y Mejores Prácticas Arquitectónicas

### 1. Estructura y Lógica de Negocio
- **Capa de Servicios**: Evita el patrón de vistas o modelos sobrecargados de lógica ("Fat Models, Fat Views"). Extrae la lógica de negocio compleja a una capa de servicios, separando al máximo posible el framework de las reglas del negocio.
- **Consultas Optimizadas**: Todo agente que consuma esta habilidad debe utilizar sistemáticamente `select_related()` para relaciones de tipo Foreign Key / One-to-One y `prefetch_related()` para relaciones Many-to-Many / Reverse Foreign Key, evitando siempre y sin excepciones el problema de consultas N+1.
- **Custom Managers y QuerySets**: Encapsula las consultas complejas y los filtros comunes en métodos dentro de un `QuerySet` personalizado y asígnalo como `Manager` del modelo.

### 2. Django REST Framework (DRF)
- Utiliza ViewSets y Routers para mantener una arquitectura de API clara y consistente.
- Mantén los Views limpios: si la lógica de creación o actualización sobrepasa la validación básica, muévela a un servicio o al método `perform_create` / `perform_update`.
- Evita realizar consultas complejas a la base de datos dentro de `SerializerMethodField`. Optimiza estas operaciones reescribiendo o usando decoradores en el método `get_queryset` del ViewSet.
- Implementa paginación obligatoria en todos los endpoints que devuelvan listas o colecciones.

### 3. Celery y Tareas Asíncronas
- Nunca bloquees el hilo principal en una respuesta HTTP mediante tareas de duración impredecible (envío de emails, redimensionado de imágenes, Webhooks).
- Usa Celery acoplado con Redis o RabbitMQ para la orquestación.
- **Idempotencia y Serialización**: Las tareas de Celery deben ser idempotentes (poder ejecutarse múltiples veces de forma segura). Nunca pases objetos complejos del ORM a las tareas; envíales siempre sus llaves primarias (IDs) para minimizar riesgos de cambios de estado en concurrencia.

### 4. Características Asíncronas (Django 5.x)
- Para las vistas que involucran un intensivo requerimiento de I/O (por ejemplo, invocaciones concurrentes a microservicios externos), utiliza vistas asíncronas introducidas en las iteraciones de Django 4.x/5.x.
- Mantén el cuidado de las transacciones con ORM en contextos asíncronos y envuelve las sentencias apropiadamente bajo un `sync_to_async` cuando corresponda.

### 5. Configuración y Testing
- Refuerza la separación de configuraciones (ej: `settings/base.py`, `settings/local.py`, `settings/production.py`) y la carga estricta a través de variables de entorno usando `django-environ`.
- Generación de Test Unitarios: Asume el uso de `pytest` combinado con `pytest-django` y utilidades modernas de testeo como `factory_boy`. Evita depender excesivamente de los `fixtures` estáticos de Django.

## Directrices de Ejecución (Para el Agente)

1. Siempre analiza los modelos y querysets en busca de optimizaciones antes de entregar el código al usuario.
2. Si vas a escribir un nuevo View o Serializer, valida inmediatamente cómo manejará grandes volúmenes de datos.
3. Si la operación a codificar es propensa a fallar en la red, sugiere desde un inicio implementar tareas mediante Celery.
