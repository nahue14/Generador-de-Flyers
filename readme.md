# 🚀 Generador Automatizado de Campañas y Catálogos Digitales

Herramienta interna basada en **Python y Pillow (PIL)** diseñada para automatizar la maquetación de flyers publicitarios profesionales en formato carrusel (redes sociales, Mercado Libre y WhatsApp). A partir de carpetas de productos con imágenes estandarizadas y una descripción en texto plano, la herramienta genera un paquete de **3 flyers inteligentes y adaptativos** con la identidad corporativa integrada.

---

## 🎨 Estructura Visual de la Campaña (Carrusel de 3 Flyers)

El sistema procesa la información y la segmenta estratégicamente para respetar el embudo de ventas digital:
1. **Flyer 1 (Impacto):** Gran foco visual en el producto, título optimizado anti-colisión con logos y un banner destacado con el resumen comercial.
2. **Flyer 2 (Características):** Presentación de ventajas competitivas en formato de viñetas con descripciones técnicas multilínea e imagen de apoyo derecha.
3. **Flyer 3 (Ficha Técnica):** Cuadrícula ordenada con especificaciones limpias, imagen de detalles complementarios, sección de usos recomendados y llamado a la acción comercial (CTA).

---

## 📁 Estructura del Proyecto y Archivos

Para que la herramienta funcione de forma correcta, se debe respetar la siguiente arquitectura de directorios en la carpeta raíz del script:

```text
📁 Catalogo/
│
├── 📄 flyers.py                  # Script principal automatizado
├── 🖼️ logo_empresa.png          # Logotipo institucional (Formato sugerido: PNG transparente)
├── 🖼️ logo_mercadolibre.png     # Logotipo de Mercado Libre para sello de confianza
│
├── 📁 Producto_Modelo_A/         # Carpeta por cada producto (Nombre libre)
│   ├── 📄 descripcion.txt       # Texto estructurado con la información técnica
│   ├── 🖼️ foto1.png              # Imagen principal del producto (F1, F2 y F3 fallback)
│   ├── 🖼️ foto2.png              # Imagen secundaria / Detalle de componentes (F2)
│   └── 🖼️ foto3.png              # Imagen técnica / Accesorios (F3)
│
└── 📁 Producto_Modelo_B/         # Siguientes carpetas de productos...
    ├── 📄 descripcion.txt
    └── 🖼️ foto1.png
```

### 🖼️ Requerimientos Estandarizados de Imágenes

*   **`logo_empresa.png` y `logo_mercadolibre.png`:** Deben ubicarse en la **raíz del proyecto**. El script aplica un escalado inteligente (`.thumbnail()`) para no deformar las marcas corporativas, ubicándolas arriba a la derecha y abajo a la derecha respectivamente de forma simétrica.
*   **`foto1.png` (Obligatoria):** Es la imagen base del producto. Se utiliza de manera central en el Flyer 1 y sirve como respaldo (*fallback*) automático en los flyers 2 y 3 si no se proveen imágenes secundarias.
*   **`foto2.png` (Opcional):** Se renderiza en el lateral derecho del Flyer 2.
*   **`foto3.png` (Opcional):** Se renderiza en el cuadrante inferior derecho del Flyer 3.

> **💡 Nota de Diseño:** Se recomienda que todas las imágenes de los productos tengan fondo transparente (`.png`) o colores sólidos coincidentes para lograr una fusión premium sobre el fondo tecnológico degradado generado por código.

---

## 📝 Formato Obligatorio del Archivo `descripcion.txt`

El motor de procesamiento de texto utiliza **Expresiones Regulares** para capturar los datos basándose en encabezados estandarizados con emojis funcionales. El archivo dentro de cada producto debe seguir este formato exacto:

```text
📦 PRODUCTO 1: Nombre Corto Alternativo (Opcional)
📝 Título
Escribe aquí el título completo del producto. Puede ocupar múltiples líneas si es necesario, el sistema las unificará de forma limpia.

📋 Descripción breve
Escribe el resumen comercial del producto. Se usará para el banner naranja inferior del Flyer 1.

⭐ Características destacadas
Título Característica 1: Detalle extendido de la ventaja comercial.
Título Característica 2: Detalle extendido de la ventaja comercial.
Título Característica 3: Detalle extendido de la ventaja comercial.

📐 Especificaciones técnicas
Capacidad: Datos...
Medidas Externas: Datos...
Material y acabado: Datos...
Peso: (Si se deja vacío, la fila no se dibuja en el flyer)

🛠️ Aplicaciones recomendadas
Alojamiento de switches de red, patch panels, centrales telefónicas y sistemas de alarma.
```

---

## ⚙️ Funcionamiento Interno de la Herramienta

El script opera de manera 100% automatizada bajo la siguiente lógica algorítmica al ejecutarse:

```python
# Para iniciar la generación del catálogo masivo:
python flyers.py
```

### 🧠 Características Avanzadas de Ingeniería Visual:
1. **Bucle de Aislamiento:** El script recorre la raíz, detecta carpetas de productos e ignora de forma inteligente entornos virtuales (`env`, `venv`) o archivos del sistema para evitar corrupciones.
2. **Eje Y Dinámico y Text Wrap:** Pillow no cuenta nativamente con salto de línea. El script incorpora la función `dibujar_parrafo_dinamico` que mide en píxeles (`getbbox`) el ancho del texto. Si supera el margen asignado, efectúa el quiebre y devuelve la posición `Y` exacta de finalización para que el siguiente elemento del layout se dibuje abajo sin solapamientos.
3. **Control Anti-Colisión:** El título del Flyer 1 tiene configurado un `ancho_max=480` píxeles. Esto fuerza el salto de línea prematuro y bloquea el texto para que jamás llegue a encimarse con el logotipo de la empresa ubicado a la derecha.
4. **Escalado Proporcional Sin Distorsión:** Se eliminaron todos los métodos `.resize()` forzados. El script implementa `.thumbnail()` combinado con cálculos de centrado dinámico, garantizando que los productos se escalen de manera simétrica según su relación de aspecto original.

---

## 🛠️ Mantenimiento y Modificaciones Frecuentes

### 1. Cambiar el Tamaño de los Banners de Texto
Si el texto de la descripción o el llamado a la acción se expanden y requieres darles más altura interna, localiza los métodos `.rectangle` de cada sección:
*   **Flyer 1 (Banner Naranja):** `d1.rectangle([(50, 675), (750, 765)])`. Reduce el segundo valor (`675`) para subir el techo del rectángulo.
*   **Flyer 3 (Banner Celeste):** `d3.rectangle([(50, 680), (750, 755)])`. Reduce el segundo valor (`680`) para ensanchar la caja verticalmente hacia arriba.

### 2. Actualizar Colores de la Marca (Paleta Corporativa)
El fondo degradado y los acentos se administran mediante tuplas de color RGB:
*   **Fondo General:** Modifica la función `crear_fondo_tecnologico()` variando los rangos matemáticos de las variables `r, g, b` para alterar las tonalidades del degradado.
*   **Acentos y Destacados:** Cambia los parámetros `fill=(255, 165, 0)` (Naranja) o `fill=(0, 210, 255)` (Celeste Cyan) por los valores RGB de tu manual de marca institucional.

### 3. Reemplazo de Tipografías
El sistema busca por defecto las fuentes de sistema `arial.ttf` y `arialbd.ttf` (Arial Bold). Si deseas utilizar una tipografía corporativa personalizada (ej. *Montserrat*), coloca el archivo `.ttf` en la raíz y actualiza las rutas dentro de la función `cargar_fuentes()`.
