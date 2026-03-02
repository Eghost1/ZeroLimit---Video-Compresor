# Django Pro (Nivel Súper Senior)

> **Firma de autoría**: Creado por Diego Bravo (<https://github.com/Eghost1>).

## Índice de Contenidos

1. [Descripción y Propósito](#descripción-y-propósito)
2. [Funcionalidades Principales](#funcionalidades-principales)
3. [Casos de Uso](#casos-de-uso)
4. [Requisitos o Directrices Operativas](#requisitos-o-directrices-operativas)

---

## Descripción y Propósito

La habilidad **Django Pro** capacita al agente para actuar como un desarrollador súper senior en entornos basados en Django 5.x. Su propósito es asegurar que toda solución implementada escale adecuadamente mediante la aplicación de patrones arquitectónicos avanzados (capas de servicio, managers custom), integraciones potentes (Celery, Redis) y características actuales de Django como las vistas asíncronas. Evita el código frágil común en implementaciones *junior* y garantiza rendimiento a gran escala.

## Funcionalidades Principales

- **Arquitectura de Software Impecable**: Fomento del patrón de Servicios para evitar "Fat Models" y "Fat Views".
- **Optimización de ORM**: Prevención radical de consultas "N+1" forzando el uso de `select_related()` y `prefetch_related()`.
- **Ecosistema DRF Avanzado**: Organización limpia mediante ViewSets, Routers y Serializadores con metodologías estrictas de paginación.
- **Asincronía y Celery**: Enrutamiento de tareas pesadas (I/O, envío de correos, integraciones) a *workers* en segundo plano evitando bloqueos HTTP. Implementación de vistas asíncronas en Django 5.x.
- **Pruebas y Entornos**: Configuración de `pytest` y gestión de configuraciones segregadas por entornos mediante variables de entorno (`django-environ`).

## Casos de Uso

### Caso 1: Refactorización de endpoints pesados

* **Contexto**: Un endpoint en DRF está tardando varios segundos en devolver una lista de objetos porque incluye relaciones y métricas calculadas.
- **Acción**: El agente reescribe el método `get_queryset` usando `select_related()` y `prefetch_related()`. Adicionalmente asila los cálculos complejos fuera de `SerializerMethodField` transfiriéndolos a una anotación (`QuerySet.annotate()`).

### Caso 2: Sistema de Notificaciones Asíncrono

* **Contexto**: El usuario necesita integraciones que procesen cientos de notificaciones al confirmar un pago.
- **Acción**: En vez de procesar el pago y las notificaciones en el mismo request, el agente diseña una solución con Django 5.x y Celery, enviando un `task_id` idempotente para que los *workers* despachen en segundo plano y el sistema retorne respuesta inmediata.

### Caso 3: Arquitectura Base de Nuevo Proyecto

* **Contexto**: Iniciar el esqueleto de un SaaS grande con Django.
- **Acción**: El agente sugiere utilizar una estructura de carpetas dividida por configuraciones separadas (base, local, production), configura `django-environ` y abstrae la lógica de creación de usuarios hacia una Capa de Servicios.

## Requisitos o Directrices Operativas

- Considerar siempre cómo afectará la carga y los tiempos de latencia antes de programar una "View".
- Prohibir estrictamente el envío de un email u operación de red dentro del ciclo síncrono Request/Response HTTP.
- Toda consulta que involucre Modelos relacionados DEBE ser analizada en busca del problema "N+1".
- Usar identificadores (IDs/PKs) en la comunicación con Celery; nunca instancias pasadas directamente como argumento.
