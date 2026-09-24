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

## 🧪 Paso 2: Seguir cada rama y probar

### 1️⃣ Cambiar de rama

```bash
git checkout option2-extend-width
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
Cambios en option2-extend-width
>>>>>>> option2-extend-width
```

En ese caso, abre el archivo, elige la versión que deseas conservar, elimina los delimitadores (`<<<<<<<`, etc.) y guarda.

---

## ✅ Paso 4: Fusionar la rama elegida con `main`

1️⃣ Cambia a `main`:

```bash
git checkout main
```

2️⃣ Merge de la rama que te gustó (ejemplo: `option2-extend-width`):

```bash
git merge option2-extend-width
```

3️⃣ Revisa si hay conflictos y resuélvelos.

4️⃣ Haz el commit final si hubo cambios: 

```bash
git commit -m "Agregar opción 2 – ancho extendido 1920x1080"
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
