# ZeroLimit Compressor 🚀

ZeroLimit Compressor es una herramienta web de compresión de video avanzada y sin límites de tamaño. A diferencia de soluciones que procesan todo en una sola petición HTTP (lo que produce errores por falta de memoria o timeouts en videos pesados), ZeroLimit escala usando un sistema de carga por fragmentos (Chunked Uploading), y procesamiento en tareas en segundo plano.

Todo diseñado con una estética Súper Senior (Glassmorfismo, Bento Grid y Tipografías Modernas).

## ✨ Características Principales

- **Compresión Sin Límites de Peso:** Sube videos de +5GB. El frontend divide el archivo en fragmentos (Chunks) de 5MB y los reensambla automáticamente en el servidor para esquivar restricciones de Nginx/Apache/Proxies.
- **Background Processing en Django:** Usa `Django-Q2` acoplado al ORM de SQLite para gestionar las tareas pesadamente intensivas sin trabar el servidor web principal. No requiere instalar Redis ni RabbitMQ.
- **FFmpeg Incorporado:** Utiliza `imageio-ffmpeg` el cual descarga un binario portátil nativo para tu sistema operativo de forma transparente. ¡No necesitas instalar/configurar variables de entorno con FFmpeg!
- **Feedback Dinámico en Vivo:** El sistema lee el output del motor renderizador (`stderr` de ffmpeg) y dibuja una barra de carga precisa vía una API Polling (milisegundos) en el Frontend.
- **Diseño Impactante:** Un UI construido con HTML/CSS puro enfocado en accesibilidad, alto contraste y animaciones que cautivan.

## ⚙️ Arquitectura

- **Frontend:** Vanilla JS (`File.slice()` API), CSS Variables, Google Fonts (`Outfit`, `Space Grotesk`).
- **Backend API:** Django 5.x, Django REST Framework (DRF).
- **Colas / Worker:** Django-Q2.
- **Motor Compresión:** FFmpeg portable (H.264/H.265).

---

## 🛠 Instalación y Configuración (Entorno Local)

### 1. Clonar el Repositorio

Primero clona este repositorio desde GitHub:

```bash
git clone https://github.com/Eghost1/zero-limit-compressor.git
cd zero-limit-compressor
```

*(Nota: Asegúrate de estar dentro de la carpeta `django_compressor` donde vive el archivo `manage.py`)*

### 2. Crear y Activar Entorno Virtual

Se recomienda fuertemente aislar las dependencias en un entorno de Python.

- **En Windows:**

  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **En Mac/Linux:**

  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar Dependencias

Asegúrate de tener el entorno virtual activo e instala los paquetes necesarios (`Django`, `DRF`, `django-q2`, `imageio-ffmpeg`):

```bash
pip install django djangorestframework django-cors-headers django-q2 imageio-ffmpeg
```

*(Nota: Opcionalmente puedes usar `pip install -r requirements.txt` si existe el archivo).*

### 4. Migrar la Base de Datos

Esto creará el SQLite local y las tablas del esquema (incluyendo las tablas que administran la cola de procesos de `Django-Q2` y nuestra tabla de historiales de `VideoTask`):

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Puesta en Marcha (Levantar Servidores)

El proyecto consta de **DOS** componentes sincronizados. Para el correcto funcionamiento necesitas levantar ambos (idealmente en dos terminales/consolas independientes teniendo en ambas el entorno virtual activo).

### Terminal 1 (Servidor Web)

Ejecuta la interfaz del usuario y los endpoints REST de Django:

```bash
python manage.py runserver
```

### Terminal 2 (Clúster de Tareas Asíncronas)

Este Worker escucha lo que entra a la base de datos y prende el motor FFmpeg. Es el "músculo" del sistema:

```bash
python manage.py qcluster
```

*(Asegúrate de activar antes el entorno con `.\venv\Scripts\activate` en esa terminal también).*

### Listo para Usar 🎉

Navega en tu explorador hacia: **[http://localhost:8000](http://localhost:8000)**

---

## 💻 Opciones de la Interfaz

Al arrastrar un video aparecerá el panel de "**Ajustes de Motor**":

1. **Alta Calidad (Poca compresión):** Genera archivos `.mp4` más grandes usando un Constant Rate Factor (CRF) de 23. Mantiene visualmente la identidad del archivo matriz de origen casi inalterable.
2. **Óptimo (Web & Móvil):** CRF 28. Reduce drásticamente el peso (ideal para enviar por WhatsApp o adjuntar en mails), con un daño perceptible menor que no afecta el visionado del humano en pantallas medianas o celulares.
3. **Extremo (Máxima reducción):** CRF 32. Comprime de una tasa sumamente destructiva si la meta crítica es ahorrar servidores cloud. El archivo quedará minúsculo, introduciendo ligeros artefactos estilo bloque (Macroblocking) lógicos de re-compresión en zonas turbulentas del video.
