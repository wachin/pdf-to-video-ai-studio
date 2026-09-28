# Git rama – Tutorial para estudiantes de informática

## Objetivo
Aprenderemos paso a paso cómo **crear, usar y unir ramas** en Git, con ejemplos de instrucciones, diagramas y emojis. 

---

## 📦 Estructura del proyecto

```
📁 pdf-to-video-ai-studio
 ├── docs/                    # documentación
 |   └── tutorials/           # <-- **este** archivo
 ├── src/                     # código del proyecto
 └── ...
```

> En esta guía **no** toucharemos el código del proyecto, solo el flujo de Git.

---

## 📡 Requisitos previos

1. Tener Git instalado (puedes usar `brew install git` o `sudo apt-get install git`).
2. Abrir una terminal y navegar hasta la raíz de tu repositorio:

```bash
cd /home/wachin/Dev/pdf-to-video-ai-studio
```

---

## 🔢 Comandos básicos de Git
| Comando | Descripción |
|---------|-------------|
| `git status` | Muestra qué archivos han sido modificados o añadidos.
| `git log` | Lista los commits recientes.
| `git branch` | Muestra las ramas locales.
| `git checkout <branch>` | Cambia de rama.
| `git push` | Sube tus cambios al remoto.
| `git merge <branch>` | Fusiona una rama en la rama en la que estás.
| `git diff` | Muestra la diferencia entre archivos.

---

## 🎯 Paso 1: Crear las 4 ramas de prueba

1️⃣ **Ir a la rama principal** (si no estás en ella):

```bash
git checkout main
```

2️⃣ **Crear y empujar** cada rama. Repite 4 veces con los nombres que quieras:

```bash
# Opción 1 – layout simple
git checkout -b option1-plain-layout
git push -u origin option1-plain-layout

# Opción 2 – ancho extendido
git checkout main
git checkout -b option2-extend-width
git push -u origin option2-extend-width

# Opción 3 – plantilla PDF
git checkout main
git checkout -b option3-pdf-template
git push -u origin option3-pdf-template

# Opción 4 – híbrido
git checkout main
git checkout -b option4-hybrid
git push -u origin option4-hybrid
```

🔍 *Tip:* `-u origin <branch>` crea el enlace remoto **para la primera vez**.

---

## 📖 **Explicación detallada de cada opción**

Esta tabla te dice **qué hace cada rama** y **qué verás en el video** al probarla:

| Rama | Qué cambia en el código | Qué verás en el video | Cuándo usarla |
|------|------------------------|----------------------|---------------|
| **option1-plain-layout** | Cambia `slides.py` para **centrar verticalmente** el texto, calcular altura real del bloque y usar toda la slide 1080×1920 | Texto centrado, ocupa toda la pantalla, sin espacios blancos arriba/abajo | ✅ **Ideal si quieres texto limpio y legible** |
| **option2-extend-width** | Cambia dimensiones a **1920×1080 (horizontal)**, ajusta fuentes y márgenes | Video horizontal (estilo YouTube clásico), texto más ancho | ✅ Si el destino es YouTube/Facebook feed |
| **option3-pdf-template** | Usa **página real del PDF como fondo** (renderiza con PyMuPDF), superpone narración encima | Se ve la página original del documento con el texto hablado encima | ✅ **La más profesional** - muestra el documento real |
| **option4-hybrid** | Combina: página PDF a la izquierda + **texto OCR limpio** a la derecha | Dos paneles: imagen original + texto extraído legible | ✅ Para documentos escaneados o con poca calidad |

### 🔬 Detalles técnicos por opción

#### 🎯 **Opción 1 – Layout Simple Centrado** (`option1-plain-layout`)
- **Archivo modificado**: `src/pdf_to_video_ai/slides.py`
- **Qué hace**: 
  1. Calcula la altura total del texto con `draw.textbbox()`
  2. Centra verticalmente: `y_start = (1920 - text_height) // 2`
  3. Ajusta `spacing` entre líneas para que quepa
- **Resultado**: Tu narración aparece centrada en la pantalla, fácil de leer
- **Ventaja**: Cambio mínimo, rápido, funciona con cualquier texto

#### 🎯 **Opción 2 – Ancho Extendido** (`option2-extend-width`)
- **Archivo modificado**: `src/pdf_to_video_ai/slides.py` + `video.py`
- **Qué hace**:
  1. Invierte dimensiones: `width=1920, height=1080`
  2. Aumenta tamaño de fuente (ej: 48pt título, 32pt cuerpo)
  3. Ajusta márgenes laterales
- **Resultado**: Video 1920×1080 horizontal, texto más grande
- **Ventaja**: Formato estándar YouTube, mejor en desktop

#### 🎯 **Opción 3 – Plantilla PDF** (`option3-pdf-template`) ⭐ **RECOMENDADA**
- **Archivos nuevos/modificados**: 
  - `src/pdf_to_video_ai/slides.py` (nueva función `render_slide_with_pdf_bg`)
  - `src/pdf_to_video_ai/extractor_canonical.py` (extrae imágenes de páginas)
  - `src/pdf_to_video_ai/pipeline.py` (usa la nueva función)
- **Qué hace**:
  1. Renderiza cada página del PDF a PNG (300 DPI) con `PyMuPDF`
  2. Guarda en `outputs/pages/page_001.png`, etc.
  3. Al crear slide: usa la imagen como fondo + superpone texto narrado
  4. Texto con semi-transparencia o caja de fondo para legibilidad
- **Resultado**: **Se ve la página real del PDF** (tablas, firmas, logos) con tu narración encima
- **Ventaja**: Video muestra exactamente el documento original, 100% fiel

#### 🎯 **Opción 4 – Híbrido** (`option4-hybrid`)
- **Archivos**: Combina opción 3 + OCR
- **Qué hace**:
  1. Detecta páginas con poca calidad (scanned, fotos)
  2. Para esas: corre OCR (PaddleOCR) y extrae texto limpio
  3. Crea slide: **izquierda** = imagen PDF original, **derecha** = texto OCR limpio
  4. Para páginas nativas: usa opción 3 normal
- **Resultado**: Lo mejor de los dos mundos
- **Ventaja**: Documentos escaneados se leen perfecto + se ve la página

---

## 🧪 Paso 2: Seguir cada rama y probar

### 1️⃣ Cambiar de rama

```bash
git checkout option4-hybrid
```

⚠️ Si la rama no existe localmente, Git la descarga del remoto automáticamente.

### 2️⃣ Ejecutar el comando que quieres probar

```bash
python -m pdf_to_video_ai.cli generar "third-party/.../2026-0435/" --salida outputs/
```

### 3️⃣ Revisar el resultado

```bash
ls outputs/
```

---

## 🔄 Paso 3: Serán `conflictos` o no? 

Cuando fusionas una rama en `main`, Git intenta **unir** los cambios. Si ambos branches alteraron las **misma líneas** iguales, se marcará un *conflicto*. Se verá algo así: 

```
<<<<<<< HEAD
Cambios en main
=======
Cambios en option4-hybrid
>>>>>>> option1-plain-layout
```

En ese caso, abre el archivo, elige la versión que deseas conservar, elimina los delimitadores (`<<<<<<<`, etc.) y guarda.

---

## ✅ Paso 4: Fusionar la rama elegida con `main`

1️⃣ Cambia a `main`:

```bash
git checkout main
```

2️⃣ Merge de la rama que te gustó (ejemplo: `option1-plain-layout`):

```bash
git merge option1-plain-layout
```

3️⃣ Revisa si hay conflictos y resuélvelos.

4️⃣ Haz el commit final si hubo cambios: 

```bash
git commit -m "Agregar opci.n 4 . h.bri"
```

5️⃣ Sube a GitHub:

```bash
git push origin main
```

---

## 📌 Resumen rápido en mermaid

```mermaid
gitgraph
  commit id: main
  branch option1-plain-layout
  commit "Plain layout changes"
  merge option1-plain-layout
  commit id: main

  branch option2-extend-width
  commit "Extend width changes"
  merge option2-extend-width
  commit id: main

  branch option3-pdf-template
  commit "PDF template changes"
  merge option3-pdf-template
  commit id: main

  branch option4-hybrid
  commit "Hybrid changes"
  merge option4-hybrid
  commit id: main
```

---

## 📌 Glosario rápido
| Término | Definición |
|---------|------------|
| **rama** | Copia de la historia que permite trabajar en paralelo. |
| **merge** | Operación que combina dos ramas en una sola. |
| **conflicto** | Cuando dos ramas cambian la misma línea y Git no sabe cuál usar. |
| **commit** | Punto “fijo” en el historial con un mensaje y un hash. |
| **remote** | Instancia del repositorio en un servidor (por ej. GitHub). |

---

## 🎉 ¡Listo! Ahora puedes crear, probar y fusionar ramas con confianza.

### Próximos pasos
1. Prueba cada una de las ramas y elige la que prefieras.
2. Integra esa rama en `main` siguiendo los pasos 4.
3. Usa la nueva rama de producción.

¡Éxitos en tu curso de informatica! 🚀
