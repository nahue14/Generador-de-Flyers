import os
import re
import cairosvg
import io
from PIL import Image, ImageDraw, ImageFont

# Configuración del Directorio Raíz y Tamaño de salida
DIRECTORIO_RAIZ = "./"
ANCHO, ALTO = 800, 800

# 🛠️ RUTAS DE LOS LOGOS GENERALES
RUTA_LOGO_EMPRESA = "./logo_empresa.png"
RUTA_LOGO_ML = "./logo_mercadolibre.svg"

def parsear_descripcion(ruta_txt):
    """
    Lee el archivo txt usando expresiones regulares para aislar e identificar
    dinámicamente las secciones, soportando múltiples líneas por campo.
    """
    datos = {
        'titulo': "Producto Destacado",
        'descripcion_breve': "Sin descripción disponible.",
        'caracteristicas': [],
        'especificaciones': [],
        'aplicaciones': ""
    }
    
    if not os.path.exists(ruta_txt):
        return datos

    try:
        with open(ruta_txt, "r", encoding="utf-8") as f:
            contenido = f.read()
            
        # 1. Extraer Título (Multilínea)
        match_tit = re.search(r'📝 Título\s*\n(.*?)(?=\n[📋⭐📐🛠️]|$)', contenido, re.DOTALL)
        if match_tit:
            datos['titulo'] = match_tit.group(1).strip().replace('\n', ' ')
        else:
            match_box = re.search(r'📦 PRODUCTO \d+:\s*([^\n]+)', contenido)
            if match_box:
                datos['titulo'] = match_box.group(1).strip()

        # 2. Extraer Descripción breve (Multilínea)
        match_desc = re.search(r'📋 Descripción breve\s*\n(.*?)(?=\n[⭐📐🛠️]|$)', contenido, re.DOTALL)
        if match_desc:
            datos['descripcion_breve'] = match_desc.group(1).strip().replace('\n', ' ')
            
        # 3. Extraer Características Destacadas
        match_caract = re.search(r'⭐ Características destacadas\s*\n(.*?)(?=\n[📐🛠️📋]|$)', contenido, re.DOTALL)
        if match_caract:
            lineas = [l.strip() for l in match_caract.group(1).split('\n') if l.strip()]
            for linea in lineas:
                if ":" in linea:
                    clave, det = linea.split(":", 1)
                    datos['caracteristicas'].append((clave.strip(), det.strip()))
                else:
                    datos['caracteristicas'].append((linea, ""))

        # 4. Extraer Especificaciones Técnicas
        match_espec = re.search(r'📐 Especificaciones técnicas\s*\n(.*?)(?=\n[🛠️⭐📋]|$)', contenido, re.DOTALL)
        if match_espec:
            lineas = [l.strip() for l in match_espec.group(1).split('\n') if l.strip()]
            for linea in lineas:
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    if valor.strip():
                        datos['especificaciones'].append((clave.strip(), valor.strip()))

        # 5. Extraer Aplicaciones recomendadas (Multilínea)
        match_apli = re.search(r'🛠️ Aplicaciones recomendadas\s*\n(.*?)(?=\n[📐⭐📋]|$)', contenido, re.DOTALL)
        if match_apli:
            datos['aplicaciones'] = match_apli.group(1).strip().replace('\n', ' ')
            
    except Exception as e:
        print(f"  ⚠️ Error procesando la estructura del archivo de texto: {e}")
        
    return datos

def ajustar_texto(texto, fuente, ancho_maximo):
    """Divide un texto largo en múltiples líneas según el ancho en píxeles."""
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    
    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()
        ancho_linea = fuente.getbbox(prueba)[2] # Índice 2 es el ancho final
        
        if ancho_linea <= ancho_maximo:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas

def dibujar_parrafo_dinamico(draw, texto, x, y, fuente, color, ancho_max, interlineado=25):
    """Dibuja un texto usando wrap automático y devuelve la nueva posición Y final."""
    lineas = ajustar_texto(texto, fuente, ancho_max)
    for linea in lineas:
        draw.text((x, y), linea, fill=color, font=fuente)
        y += interlineado
    return y

def crear_fondo_tecnologico():
    fondo = Image.new("RGB", (ANCHO, ALTO), color=(10, 20, 38))
    draw = ImageDraw.Draw(fondo)
    for y in range(ALTO):
        r = int(10 + (25 - 10) * (y / ALTO))
        g = int(20 + (35 - 20) * (y / ALTO))
        b = int(38 + (55 - 38) * (y / ALTO))
        draw.line([(0, y), (ANCHO, y)], fill=(r, g, b))
    return fondo

def aplicar_branding_marcas(imagen_flyer):
    """🛠️ NUEVA FUNCIÓN: Inserta de forma limpia los logos corporativos si existen."""
    # 1. Logo de la Empresa (Arriba a la Derecha, equilibrando la categoría izquierda)
    if os.path.exists(RUTA_LOGO_EMPRESA):
        try:
            logo_emp = Image.open(RUTA_LOGO_EMPRESA).convert('RGBA')
            logo_emp.thumbnail((240, 90))  # Redimensionar manteniendo proporción max 120x45
            imagen_flyer.paste(logo_emp, (ANCHO - logo_emp.width - 50, 30), mask=logo_emp)
        except Exception as e:
            print(f"  ⚠️ No se pudo pegar el logo de la empresa: {e}")

    # 2. Logo de Mercado Libre (Abajo a la derecha, arriba o al lado del CTA)
    if os.path.exists(RUTA_LOGO_ML):
        try:
            png_bytes = cairosvg.svg2png(url=RUTA_LOGO_ML, output_height=140)
            logo_ml = Image.open(io.BytesIO(png_bytes)).convert('RGBA')
            
            logo_ml.thumbnail((220, 70))  # Redimensionar de forma discreta institucional
            imagen_flyer.paste(logo_ml, (0, 800-logo_ml.height), mask=logo_ml)
        except Exception as e:
            print(f"  ⚠️ No se pudo pegar el logo de Mercado Libre: {e}")

def cargar_fuentes():
    try:
        font_titulo = ImageFont.truetype("arialbd.ttf", 28)
        font_sub = ImageFont.truetype("arialbd.ttf", 20)
        font_cuerpo = ImageFont.truetype("arial.ttf", 17)
        font_destaque = ImageFont.truetype("arialbd.ttf", 17)
    except:
        font_titulo = font_sub = font_cuerpo = font_destaque = ImageFont.load_default()
    return font_titulo, font_sub, font_cuerpo, font_destaque

def procesar_catalogos():
    font_titulo, font_sub, font_cuerpo, font_destaque = cargar_fuentes()

    for nombre_producto in os.listdir(DIRECTORIO_RAIZ):
        ruta_producto = os.path.join(DIRECTORIO_RAIZ, nombre_producto)
        
        if not os.path.isdir(ruta_producto) or nombre_producto.startswith('.') or nombre_producto in ['env', 'venv']:
            continue
            
        ruta_txt = os.path.join(ruta_producto, "Descripcion.txt")
        if not os.path.exists(ruta_txt):
            ruta_txt = os.path.join(ruta_producto, "descripcion.txt")
            if not os.path.exists(ruta_txt):
                continue
            
        print(f"\n🚀 Procesando campaña adaptativa corporativa para: '{nombre_producto}'")
        datos = parsear_descripcion(ruta_txt)
        
        img_f1 = os.path.join(ruta_producto, "foto1.png")
        img_f2 = os.path.join(ruta_producto, "foto2.png")
        img_f3 = os.path.join(ruta_producto, "foto3.png")
        img_f4 = os.path.join(ruta_producto, "foto4.png")
        img_f5 = os.path.join(ruta_producto, "foto5.png")

        # =========================================================================
        # 🖼️ FLYER 1: IMPACTO 
        # =========================================================================
        f1 = crear_fondo_tecnologico()
        d1 = ImageDraw.Draw(f1)
        
        d1.text((50, 35), "PRODUCTO DESTACADO", fill=(0, 210, 255), font=font_cuerpo)
        
        y_actual = dibujar_parrafo_dinamico(d1, datos['titulo'], 50, 65, font_titulo, (255, 255, 255), ancho_max=400, interlineado=35)

        # Pegar Foto 1 manteniendo proporciones
        if os.path.exists(img_f1):
            img = Image.open(img_f1).convert('RGBA')
            caja_delimitadora = img.getbbox()

            if caja_delimitadora:
                # Recortar la imagen eliminando el fondo vacío
                imagen_recortada = img.crop(caja_delimitadora)
                img = imagen_recortada
                # Definir el nuevo tamaño para maximizar el objeto
                # Ejemplo: Definir un ancho fijo de 1920px manteniendo la proporción
                ancho_objetivo = 350
                proporcion = ancho_objetivo / float(img.width)
                alto_objetivo = int(float(img.height) * proporcion)
                
                # 4. Redimensionar con máxima calidad
                img = img.resize(
                    (ancho_objetivo, alto_objetivo), 
                    Image.Resampling.LANCZOS
                )

            # 1. Calculamos el espacio vertical real que dejó el título
            alto_disponible = max(250, 600 - y_actual)
            
            # 2. Achicamos la foto al recuadro máximo permitido sin deformarla
            img.thumbnail((550, alto_disponible)) 
            
            # 3. La centramos milimétricamente en el espacio libre del lienzo
            x_centro = int((ANCHO/2-img.width-10))
            y_centro = int(y_actual + 15 + (alto_disponible - img.height) / 2)
            
            f1.paste(img, (x_centro, y_centro), mask=img)

        # Pegar Foto 1 manteniendo proporciones
        if os.path.exists(img_f2):
            img = Image.open(img_f2).convert('RGBA')
            caja_delimitadora = img.getbbox()

            if caja_delimitadora:
                # Recortar la imagen eliminando el fondo vacío
                imagen_recortada = img.crop(caja_delimitadora)
                img = imagen_recortada
                # Definir el nuevo tamaño para maximizar el objeto
                # Ejemplo: Definir un ancho fijo de 1920px manteniendo la proporción
                ancho_objetivo = 350
                proporcion = ancho_objetivo / float(img.width)
                alto_objetivo = int(float(img.height) * proporcion)
                
                # 4. Redimensionar con máxima calidad
                img = img.resize(
                    (ancho_objetivo, alto_objetivo), 
                    Image.Resampling.LANCZOS
                )
                
            # 1. Calculamos el espacio vertical real que dejó el título
            alto_disponible = max(250, 600 - y_actual)
            
            # 2. Achicamos la foto al recuadro máximo permitido sin deformarla
            img.thumbnail((550, alto_disponible)) 
            
            # 3. La centramos milimétricamente en el espacio libre del lienzo
            x_centro = int(ANCHO/2+10)
            y_centro = int(y_actual + 15 + (alto_disponible - img.height) / 2)
            
            f1.paste(img, (x_centro, y_centro), mask=img)
        
            
        d1.rectangle([(50, 675), (750, 775)], fill=(255, 165, 0)) # Se bajó un poco el banner para dar espacio al logo de ML
        d1.text((90, 685), "📝 RESUMEN:", fill=(10, 20, 38), font=font_destaque)
        dibujar_parrafo_dinamico(d1, datos['descripcion_breve'], 90, 710, font_cuerpo, (10, 20, 38), ancho_max=660, interlineado=22)
        
        aplicar_branding_marcas(f1) # 🛠️ Aplicación de logos
        f1.save(os.path.join(ruta_producto, "flyer_1_impacto.jpg"), "JPEG", quality=95)

        # =========================================================================
        # 🖼️ FLYER 2: CARACTERÍSTICAS
        # =========================================================================
        f2 = crear_fondo_tecnologico()
        d2 = ImageDraw.Draw(f2)
        d2.text((50, 35), "VENTAJAS COMPETITIVAS", fill=(0, 210, 255), font=font_cuerpo)
        d2.text((50, 65), "Características Principales", fill=(255, 255, 255), font=font_titulo)


        origen_f2 = img_f3 if os.path.exists(img_f3) else img_f1
        if os.path.exists(origen_f2):
            img = Image.open(origen_f2).convert('RGBA')
            caja_delimitadora = img.getbbox()

            if caja_delimitadora:
                # Recortar la imagen eliminando el fondo vacío
                imagen_recortada = img.crop(caja_delimitadora)
                img = imagen_recortada
            
            # Recuadro máximo lateral (Ancho max: 340, Alto max: 320)
            img.thumbnail((340, 320))
            
            # La alineamos a la derecha (X=430) y centramos verticalmente en su bloque
            y_centro_f2 = int(195 + (320/2 - img.height) / 2)
            f2.paste(img, (430, y_centro_f2), mask=img)

        origen_f2 = img_f4 if os.path.exists(img_f4) else img_f1
        if os.path.exists(origen_f2):
            img = Image.open(origen_f2).convert('RGBA')
            caja_delimitadora = img.getbbox()

            if caja_delimitadora:
                # Recortar la imagen eliminando el fondo vacío
                imagen_recortada = img.crop(caja_delimitadora)
                img = imagen_recortada
            
            # Recuadro máximo lateral (Ancho max: 340, Alto max: 320)
            img.thumbnail((340, 320))
            
            # La alineamos a la derecha (X=430) y centramos verticalmente en su bloque
            y_centro_f2 = int(180 + 320 - (img.height) / 5)
            f2.paste(img, (430, y_centro_f2), mask=img)


            
        y_pos = 140
        for item_tit, item_desc in datos['caracteristicas'][:5]:
            d2.text((50, y_pos), f"🔹 {item_tit}", fill=(255, 165, 0), font=font_destaque)
            y_pos += 22
            if item_desc:
                y_pos = dibujar_parrafo_dinamico(d2, item_desc, 50, y_pos, font_cuerpo, (220, 220, 220), ancho_max=360, interlineado=22)
            y_pos += 15

        aplicar_branding_marcas(f2) # 🛠️ Aplicación de logos
        f2.save(os.path.join(ruta_producto, "flyer_2_caracteristicas.jpg"), "JPEG", quality=95)

        # =========================================================================
        # 🖼️ FLYER 3: FICHA TÉCNICA
        # =========================================================================
        f3 = crear_fondo_tecnologico()
        d3 = ImageDraw.Draw(f3)
        d3.text((50, 35), "DETALLES COMPLEMENTARIOS", fill=(0, 210, 255), font=font_cuerpo)
        d3.text((50, 65), "Especificaciones Técnicas", fill=(255, 255, 255), font=font_titulo)
        
        y_pos = 140


        for etiqueta, valor in datos['especificaciones'][:8]:
            d3.text((50, y_pos), f"{etiqueta}", fill=(180, 180, 180), font=font_destaque)
            y_pos_final_valor = dibujar_parrafo_dinamico(d3, valor, 240, y_pos, font_cuerpo, (255, 255, 255), ancho_max=510, interlineado=22)

            d3.line([(50, y_pos_final_valor + 5), (750, y_pos_final_valor + 5)], fill=(40, 50, 70), width=1)
            y_pos = y_pos_final_valor + 15

        origen_f3 = img_f5 if os.path.exists(img_f5) else img_f1
        if os.path.exists(origen_f3):
            img_tecnica = Image.open(origen_f3).convert('RGBA')
            caja_delimitadora = img.getbbox()

            if caja_delimitadora:
                # Recortar la imagen eliminando el fondo vacío
                imagen_recortada = img.crop(caja_delimitadora)
                img = imagen_recortada
            
            # Recuadro máximo inferior (Ancho max: 240, Alto max: 180)
            img_tecnica.thumbnail((240, 180))
            
            # Centramos la imagen en el espacio derecho junto a los usos recomendados
            y_centro_f3 = int((y_pos + 10) + (180 - img_tecnica.height) / 2)
            f3.paste(img_tecnica, (510, y_centro_f3), mask=img_tecnica)


        
        if datos['aplicaciones']:
            d3.text((50, y_pos + 10), "⚙️ Usos recomendados:", fill=(255, 165, 0), font=font_destaque)

        dibujar_parrafo_dinamico(d3, datos['aplicaciones'], 50, y_pos + 35, font_cuerpo, (200, 200, 200), ancho_max=440, interlineado=22)
        d3.rectangle([(50, 680), (750, 755)], fill=(0, 210, 255))

        d3.text((80, 705), "💼 ENCUÉNTRANOS EN MERCADOLIBRE O NUESTRO SITIO WEB", fill=(10, 20, 38), font=font_sub)
        aplicar_branding_marcas(f3) 

        # 🛠️ Aplicación de logos
        f3.save(os.path.join(ruta_producto, "flyer_3_tecnico.jpg"), "JPEG", quality=95)
        print("  ✅ Los 3 flyers corporativos finales fueron generados.")

procesar_catalogos()
