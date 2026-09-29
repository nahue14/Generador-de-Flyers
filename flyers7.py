import os
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Configuración del Directorio Raíz y Tamaño de salida (Diseño nativo a 2X)
DIRECTORIO_RAIZ = "./"
ANCHO_PROCESO, ALTO_PROCESO = 1600, 1600
ANCHO_FINAL, ALTO_FINAL = 800, 800

# 🛠️ RUTAS DE LOS LOGOS GENERALES
RUTA_LOGO_EMPRESA = "./logo_empresa.png"
RUTA_LOGO_ML = "./logo_mercadolibre.png"

def parsear_descripcion(ruta_txt):
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
            
        match_tit = re.search(r'📝 Título\s*\n(.*?)(?=\n[📋⭐📐🛠️]|$)', contenido, re.DOTALL)
        if match_tit:
            datos['titulo'] = match_tit.group(1).strip().replace('\n', ' ')
        else:
            match_box = re.search(r'📦 PRODUCTO \d+:\s*([^\n]+)', contenido)
            if match_box:
                datos['titulo'] = match_box.group(1).strip()

        match_desc = re.search(r'📋 Descripción breve\s*\n(.*?)(?=\n[⭐📐🛠️]|$)', contenido, re.DOTALL)
        if match_desc:
            datos['descripcion_breve'] = match_desc.group(1).strip().replace('\n', ' ')
            
        match_caract = re.search(r'⭐ Características destacadas\s*\n(.*?)(?=\n[📐🛠️📋]|$)', contenido, re.DOTALL)
        if match_caract:
            lineas = [l.strip() for l in match_caract.group(1).split('\n') if l.strip()]
            for linea in lineas:
                if ":" in linea:
                    clave, det = linea.split(":", 1)
                    datos['caracteristicas'].append((clave.strip(), det.strip()))
                else:
                    datos['caracteristicas'].append((linea, ""))

        match_espec = re.search(r'📐 Especificaciones técnicas\s*\n(.*?)(?=\n[🛠️⭐📋]|$)', contenido, re.DOTALL)
        if match_espec:
            lineas = [l.strip() for l in match_espec.group(1).split('\n') if l.strip()]
            for linea in lineas:
                if ":" in linea:
                    clave, valor = linea.split(":", 1)
                    if valor.strip():
                        datos['especificaciones'].append((clave.strip(), valor.strip()))

        match_apli = re.search(r'🛠️ Aplicaciones recomendadas\s*\n(.*?)(?=\n[📐⭐📋]|$)', contenido, re.DOTALL)
        if match_apli:
            datos['aplicaciones'] = match_apli.group(1).strip().replace('\n', ' ')
    except Exception as e:
        print(f"  ⚠️ Error procesando la estructura del archivo de texto: {e}")
    return datos

def ajustar_texto(texto, fuente, ancho_maximo):
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        prueba = f"{linea_actual} {palabra}".strip()
        ancho_linea = fuente.getbbox(prueba)[2]
        if ancho_linea <= ancho_maximo:
            linea_actual = prueba
        else:
            if linea_actual:
                lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas

def dibujar_parrafo_dinamico(draw, texto, x, y, fuente, color, ancho_max, interlineado=52):
    lineas = ajustar_texto(texto, fuente, ancho_max)
    for linea in lineas:
        draw.text((x, y), linea, fill=color, font=fuente)
        y += interlineado
    return y

def crear_fondo_tecnologico():
    # Creamos un degradado perfecto usando interpolación bilineal y desenfoque masivo para eliminar rayas
    base = Image.new("RGB", (4, 4))
    base.putpixel((0, 0), (10, 20, 38))
    base.putpixel((3, 0), (10, 20, 38))
    base.putpixel((0, 3), (25, 35, 55))
    base.putpixel((3, 3), (25, 35, 55))
    fondo = base.resize((ANCHO_PROCESO, ALTO_PROCESO), Image.Resampling.BILINEAR)
    return fondo.filter(ImageFilter.GaussianBlur(radius=5))

def dibujar_rectangulo_suave(imagen, coordenadas, color_relleno):
    # Dibuja figuras con bordes nítidos generando la forma sobre una capa separada
    capa_figura = Image.new("RGBA", imagen.size, (0, 0, 0, 0))
    draw_figura = ImageDraw.Draw(capa_figura)
    draw_figura.rectangle(coordenadas, fill=color_relleno)
    return Image.alpha_composite(imagen.convert("RGBA"), capa_figura)

def aplicar_branding_marcas(imagen_flyer):
    if os.path.exists(RUTA_LOGO_EMPRESA):
        try:
            logo_emp = Image.open(RUTA_LOGO_EMPRESA).convert('RGBA')
            logo_emp.thumbnail((480, 180), Image.Resampling.LANCZOS)
            imagen_flyer.paste(logo_emp, (ANCHO_PROCESO - logo_emp.width - 100, 60), mask=logo_emp)
        except Exception as e:
            print(f"  ⚠️ No se pudo pegar el logo de la empresa: {e}")

    if os.path.exists(RUTA_LOGO_ML):
        try:
            logo_ml = Image.open(RUTA_LOGO_ML).convert('RGBA')
            logo_ml.thumbnail((440, 140), Image.Resampling.LANCZOS)
            imagen_flyer.paste(logo_ml, (0, ALTO_PROCESO - logo_ml.height), mask=logo_ml)
        except Exception as e:
            print(f"  ⚠️ No se pudo pegar el logo de Mercado Libre: {e}")

def cargar_fuentes():
    try:
        font_titulo = ImageFont.truetype("Montserrat-Bold.ttf", 56)
        font_sub = ImageFont.truetype("Montserrat-Bold.ttf", 40)
        font_cuerpo = ImageFont.truetype("Montserrat-Regular.ttf", 34)
        font_destaque = ImageFont.truetype("Montserrat-Bold.ttf", 34)
    except:
        font_titulo = font_sub = font_cuerpo = font_destaque = ImageFont.load_default()
    return font_titulo, font_sub, font_cuerpo, font_destaque

def limpiar_emojis(texto):
    return "".join(c for c in texto if ord(c) <= 65535)

def procesar_catalogos():
    font_titulo, font_sub, font_cuerpo, font_destaque = cargar_fuentes()

    for nombre_producto in os.listdir(DIRECTORIO_RAIZ):
        ruta_producto = os.path.join(DIRECTORIO_RAIZ, nombre_producto)
        
        if not os.path.isdir(ruta_producto) or nombre_producto.startswith('.') or nombre_producto in ['env', 'venv']:
            continue
            
        ruta_txt = os.path.join(ruta_producto, "descripcion.txt")
        if not os.path.exists(ruta_txt):
            continue
            
        print(f"\n🚀 Procesando campaña premium corporativa para: '{nombre_producto}'")
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
        
        d1.text((100, 70), "PRODUCTO DESTACADO", fill=(0, 210, 255), font=font_cuerpo)
        texto_limpio = limpiar_emojis(datos['titulo'])
        y_actual = dibujar_parrafo_dinamico(d1, texto_limpio, 100, 130, font_titulo, (255, 255, 255), ancho_max=800, interlineado=70)

        alto_disponible = max(500, 1200 - y_actual)

        # Pegar Foto 1 de manera directa y limpia
        if os.path.exists(img_f1):
            img = Image.open(img_f1).convert('RGBA')
            caja_delimitadora = img.getbbox()
            if caja_delimitadora:
                img = img.crop(caja_delimitadora)
            img.thumbnail((700, alto_disponible), Image.Resampling.LANCZOS) 
            x_centro = int((ANCHO_PROCESO / 2 - img.width) / 2) + 50
            y_centro = int(y_actual + 30 + (alto_disponible - img.height) / 2)
            f1.paste(img, (x_centro, y_centro), mask=img)

        # Pegar Foto 2 de manera directa y limpia
        if os.path.exists(img_f2):
            img = Image.open(img_f2).convert('RGBA')
            caja_delimitadora = img.getbbox()
            if caja_delimitadora:
                img = img.crop(caja_delimitadora)
            img.thumbnail((700, alto_disponible), Image.Resampling.LANCZOS) 
            x_centro = int(ANCHO_PROCESO / 2 + (ANCHO_PROCESO / 2 - img.width) / 2) - 50
            y_centro = int(y_actual + 30 + (alto_disponible - img.height) / 2)
            f1.paste(img, (x_centro, y_centro), mask=img)
        
        # Dibujar banner inferior suave
        f1 = dibujar_rectangulo_suave(f1, [(100, 1330), (1500, 1530)], (255, 165, 0, 255))
        d1 = ImageDraw.Draw(f1) # Re-vincular draw tras fusión de capas
        
        d1.text((140, 1350), "RESUMEN:", fill=(10, 20, 38), font=font_destaque)
        texto_limpio = limpiar_emojis(datos['descripcion_breve'])
        dibujar_parrafo_dinamico(d1, texto_limpio, 140, 1400, font_cuerpo, (10, 20, 38), ancho_max=1320, interlineado=44)
        
        aplicar_branding_marcas(f1)
        flyer_final = f1.resize((ANCHO_FINAL, ALTO_FINAL), Image.Resampling.LANCZOS)
        # Guardamos en PNG para máxima fidelidad estructural
        flyer_final.save(os.path.join(ruta_producto, "flyer_1_impacto.png"), "PNG")

        # =========================================================================
        # 🖼️ FLYER 2: CARACTERÍSTICAS
        # =========================================================================
        f2 = crear_fondo_tecnologico()
        d2 = ImageDraw.Draw(f2)
        d2.text((100, 70), "VENTAJAS COMPETITIVAS", fill=(0, 210, 255), font=font_cuerpo)
        d2.text((100, 130), "Características Principales", fill=(255, 255, 255), font=font_titulo)

        origen_f2_1 = img_f3 if os.path.exists(img_f3) else img_f1
        if os.path.exists(origen_f2_1):
            img = Image.open(origen_f2_1).convert('RGBA')
            caja_delimitadora = img.getbbox()
            if caja_delimitadora:
                img = img.crop(caja_delimitadora)
            img.thumbnail((620, 580), Image.Resampling.LANCZOS)
            y_centro_f2 = int(280 + (580 - img.height) / 2)
            f2.paste(img, (880, y_centro_f2), mask=img)
            origen_f2_2 = img_f4 if os.path.exists(img_f4) else img_f1
        if os.path.exists(origen_f2_2):
            img = Image.open(origen_f2_2).convert('RGBA')
            caja_delimitadora = img.getbbox()
            if caja_delimitadora:
                img = img.crop(caja_delimitadora)
            img.thumbnail((620, 580), Image.Resampling.LANCZOS)
            y_centro_f2 = int(880 + (580 - img.height) / 2)
            f2.paste(img, (880, y_centro_f2), mask=img)
        y_pos = 280
        for item_tit, item_desc in datos['caracteristicas'][:5]:
            texto_limpio = limpiar_emojis(item_tit)
            d2.text((100, y_pos), f"{texto_limpio}", fill=(255, 165, 0), font=font_destaque)
            y_pos += 46
            if item_desc:
                texto_limpio = limpiar_emojis(item_desc)
                y_pos = dibujar_parrafo_dinamico(d2, texto_limpio, 100, y_pos, font_cuerpo, (220, 220, 220), ancho_max=740, interlineado=46)
            y_pos += 35
        aplicar_branding_marcas(f2)
        flyer_final = f2.resize((ANCHO_FINAL, ALTO_FINAL), Image.Resampling.LANCZOS)
        flyer_final.save(os.path.join(ruta_producto, "flyer_2_caracteristicas.png"), "PNG")
        # =========================================================================
        # # 🖼️ FLYER 3: FICHA TÉCNICA
        # # =========================================================================
        f3 = crear_fondo_tecnologico()
        d3 = ImageDraw.Draw(f3)
        d3.text((100, 70), "DETALLES COMPLEMENTARIOS", fill=(0, 210, 255), font=font_cuerpo)
        d3.text((100, 130), "Especificaciones Técnicas", fill=(255, 255, 255), font=font_titulo)
        y_pos = 280
        for etiqueta, valor in datos['especificaciones'][:8]:
            texto_limpio = limpiar_emojis(etiqueta)
            d3.text((100, y_pos), f"{texto_limpio}", fill=(180, 180, 180), font=font_destaque)
            texto_limpio = limpiar_emojis(valor)
            y_pos_final_valor = dibujar_parrafo_dinamico(d3, texto_limpio, 500, y_pos, font_cuerpo, (255, 255, 255), ancho_max=1000, interlineado=46)
            d3.line([(100, y_pos_final_valor + 12), (1500, y_pos_final_valor + 12)], fill=(40, 50, 70), width=2)
            y_pos = y_pos_final_valor + 35
        origen_f3 = img_f5 if os.path.exists(img_f5) else img_f1
        if os.path.exists(origen_f3):
            img_tecnica = Image.open(origen_f3).convert('RGBA')
            caja_delimitadora = img_tecnica.getbbox()
            if caja_delimitadora:
                img_tecnica = img_tecnica.crop(caja_delimitadora)
            img_tecnica.thumbnail((500, 400), Image.Resampling.LANCZOS)
            y_centro_f3 = int(y_pos + (300 - img_tecnica.height) / 2)
            f3.paste(img_tecnica, (1000, y_centro_f3), mask=img_tecnica)
        
        if datos['aplicaciones']:
            d3.text((100, y_pos + 20), "Usos recomendados:", fill=(255, 165, 0), font=font_destaque)
        texto_limpio = limpiar_emojis(datos['aplicaciones'])
        dibujar_parrafo_dinamico(d3, texto_limpio, 100, y_pos + 75, font_cuerpo, (200, 200, 200), ancho_max=850, interlineado=46)
        f3 = dibujar_rectangulo_suave(f3, [(100, 1350), (1500, 1500)], (0, 210, 255, 255))
        d3 = ImageDraw.Draw(f3)
       
        d3.text((160, 1395), "ENCUÉNTRANOS EN MERCADOLIBRE O NUESTRO SITIO WEB", fill=(10, 20, 38), font=font_sub)
        aplicar_branding_marcas(f3)
       
        flyer_final = f3.resize((ANCHO_FINAL, ALTO_FINAL), Image.Resampling.LANCZOS)
       
        flyer_final.save(os.path.join(ruta_producto, "flyer_3_tecnico.png"), "PNG")
        print("  ✅ Los 3 flyers premium finales fueron generados sin pérdida.")
procesar_catalogos()