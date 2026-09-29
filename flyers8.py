import os
import re
from PIL import Image
from weasyprint import HTML

# Configuración del Directorio Raíz
DIRECTORIO_RAIZ = "./"

# 🛠️ RUTAS DE LOS LOGOS GENERALES (Convertidos a rutas absolutas del sistema)
RUTA_LOGO_EMPRESA = os.path.abspath("./logo_empresa.png")
RUTA_LOGO_ML = os.path.abspath("./logo_mercadolibre.svg")


def recortar_fondo_al_ras(ruta_imagen):
    """
    Abre una imagen, detecta los bordes reales del producto 
    (eliminando transparencias o fondos blancos) y la guarda recortada al ras.
    """
    if not os.path.exists(ruta_imagen):
        return
    
    try:
        img = Image.open(ruta_imagen)
        
        # Si la imagen está en modo indexado (P) o escala de grises, la pasamos a RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # 1. Detectar fondo transparente usando el canal Alfa
        caja_recorte = img.getbbox()
        
        # 2. Si no tiene transparencia (o el getbbox no achicó nada), probamos detectar fondo blanco
        if caja_recorte:
            # Creamos una máscara basada en el brillo para ignorar el blanco puro (R>245, G>245, B>245)
            # Esto ayuda si tus fotos tienen fondos casi blancos o blancos de catálogo
            datos = img.getdata()
            nuevos_datos = []
            for item in datos:
                # Si el píxel es muy cercano al blanco puro, lo hacemos transparente temporalmente
                if item[0] > 245 and item[1] > 245 and item[2] > 245:
                    nuevos_datos.append((0, 0, 0, 0))
                else:
                    nuevos_datos.append(item)
            
            img_temporal = Image.new("RGBA", img.size)
            img_temporal.putdata(nuevos_datos)
            caja_blanca = img_temporal.getbbox()
            
            # Si encontramos un recuadro más chico aislando el blanco, usamos ese
            if caja_blanca:
                caja_recorte = caja_blanca

        # 3. Si encontramos bordes reales, recortamos y guardamos reemplazando la original
        if caja_recorte:
            # Le agregamos un pequeño margen de 5 píxeles para que no quede asfixiado el producto
            ancho_orig, alto_orig = img.size
            x0 = max(0, caja_recorte[0] - 5)
            y0 = max(0, caja_recorte[1] - 5)
            x1 = min(ancho_orig, caja_recorte[2] + 5)
            y1 = min(alto_orig, caja_recorte[3] + 5)
            
            img_recortada = img.crop((x0, y0, x1, y1))
            img_recortada.save(ruta_imagen, "PNG")
            
    except Exception as e:
        print(f"  ⚠️ No se pudo recortar automáticamente {os.path.basename(ruta_imagen)}: {e}")


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

def generar_html_bloque_producto(datos, nombre_producto):
    """Genera exclusivamente las 3 páginas HTML de un producto usando rutas locales de su carpeta."""
    
    html_caracteristicas = ""
    for tit, desc in datos['caracteristicas'][:5]:
        html_caracteristicas += f"""
        <div class="feature-item">
            <div class="feature-title">{tit}</div>
            {f'<div class="feature-desc">{desc}</div>' if desc else ''}
        </div>"""

    html_especificaciones = ""
    for etiqueta, valor in datos['especificaciones'][:8]:
        html_especificaciones += f"""
        <div class="spec-row">
            <span class="spec-label">{etiqueta}</span>
            <span class="spec-value">{valor}</span>
        </div>"""

    # Definimos las rutas relativas directas de la carpeta actual del producto
    img1_html = '<img src="./foto1.png" class="prod-img-half">' if os.path.exists(f"./{nombre_producto}/foto1.png") else ''
    img2_html = '<img src="./foto2.png" class="prod-img-half">' if os.path.exists(f"./{nombre_producto}/foto2.png") else ''
    
    # Alternativas para las páginas interiores si faltan imágenes específicas (Solución al SyntaxError)
    img3_src = "./foto3.png" if os.path.exists(f"./{nombre_producto}/foto3.png") else "./foto1.png"
    img3_nombre = img3_src.replace("./", "")
    img3_html = f'<img src="{img3_src}" class="side-img">' if os.path.exists(f"./{nombre_producto}/{img3_nombre}") else ''
    
    img4_src = "./foto4.png" if os.path.exists(f"./{nombre_producto}/foto4.png") else "./foto1.png"
    img4_nombre = img4_src.replace("./", "")
    img4_html = f'<img src="{img4_src}" class="side-img">' if os.path.exists(f"./{nombre_producto}/{img4_nombre}") else ''
    
    img5_src = "./foto5.png" if os.path.exists(f"./{nombre_producto}/foto5.png") else "./foto1.png"
    img5_nombre = img5_src.replace("./", "")
    img5_html = f'<img src="{img5_src}" class="tech-img">' if os.path.exists(f"./{nombre_producto}/{img5_nombre}") else ''


    # 1. Preparamos las rutas de los logos fuera de la f-string para evitar la barra invertida (\)
    ruta_logo_empresa_url = RUTA_LOGO_EMPRESA.replace("\\", "/")
    ruta_logo_ml_url = RUTA_LOGO_ML.replace("\\", "/")

    # 2. Ahora armamos el HTML usando las variables limpias de forma segura
    logo_empresa_html = f'<img src="file:///{ruta_logo_empresa_url}" class="logo-empresa">' if os.path.exists(RUTA_LOGO_EMPRESA) else ''
    logo_ml_html = f'<img src="file:///{ruta_logo_ml_url}" class="logo-ml">' if os.path.exists(RUTA_LOGO_ML) else ""


    # Retorna el fragmento de código de las 3 secciones (páginas) correspondientes a este producto
    return f"""
    <!-- PRODUCTO: {nombre_producto} -->
    <div class="flyer">
        {logo_empresa_html}
        <div class="header-tag">Producto Destacado</div>
        <h1 class="title">{datos['titulo']}</h1>
        
        <div class="gallery-container">
            {img1_html}
            {img2_html}
        </div>
        
        <div class="summary-banner">
            <div class="summary-title">RESUMEN:</div>
            <div class="summary-text">{datos['descripcion_breve']}</div>
        </div>
        {logo_ml_html}
    </div>

    <div class="flyer">
        {logo_empresa_html}
        <div class="header-tag">Ventajas Competitivas</div>
        <h1 class="title" style="font-size:24px;">Características Principales</h1>
        
        <div class="flex-container">
            <div class="left-column">
                {html_caracteristicas}
            </div>
            <div class="right-column">
                {img3_html}
                {img4_html}
            </div>
        </div>
        {logo_ml_html}
    </div>

    <div class="flyer">
        {logo_empresa_html}
        <div class="header-tag">Detalles Complementarios</div>
        <h1 class="title" style="font-size:24px;">Especificaciones Técnicas</h1>
        
        <div class="specs-container">
            {html_especificaciones}
        </div>
        
        <div class="footer-tech">
            <div class="apps-box">
                {f'<div class="apps-title">Usos recomendados:</div><div class="apps-text">{datos["aplicaciones"]}</div>' if datos['aplicaciones'] else ''}
            </div>
            {img5_html}
        </div>
        
        <div class="cta-banner">
            ENCUÉNTRANOS EN MERCADOLIBRE O NUESTRO SITIO WEB
        </div>
        {logo_ml_html}
    </div>
    """

def obtener_estilos_base_css():
    """Retorna los estilos de diseño unificados y optimizados para WeasyPrint."""
    return """
    @page {
        size: 800px 800px;
        margin: 0;
    }
    body {
        margin: 0;
        padding: 0;
        font-family: 'Montserrat', Arial, sans-serif;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .flyer {
        width: 800px;
        height: 800px;
        box-sizing: border-box;
        position: relative;
        page-break-after: always;
        background: linear-gradient(180deg, #0a1426 0%, #192337 100%);
        color: #ffffff;
        padding: 40px;
        overflow: hidden;
    }
    .header-tag {
        color: #00d2ff;
        font-size: 16px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .title {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.3;
        margin: 0 0 20px 0;
        max-width: 500px;
    }
    .logo-empresa {
        position: absolute;
        top: 30px;
        right: 40px;
        max-width: 250px;
        max-height: 70px;
        object-fit: contain;
    }
    .logo-ml {
        position: absolute;
        bottom: 0px;
        left: 0px;
        max-width: 50px;
        max-height: 250px;
        object-fit: contain;
    }
    .gallery-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        height: 430px;
        margin-top: 20px;
    }
    .prod-img-half {
        max-width: 49%;
        max-height: 90%;
        object-fit: contain;
    }
    .summary-banner {
        position: absolute;
        bottom: 40px;
        left: 40px;
        right: 40px;
        background: #ffa500;
        color: #0a1426;
        padding: 20px;
        border-radius: 4px;
        box-sizing: border-box;
    }
    .summary-title {
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .summary-text {
        font-size: 14px;
        line-height: 1.4;
    }
    .flex-container {
        display: flex;
        justify-content: space-between;
        margin-top: 30px;
        height: 560px;
    }
    .left-column {
        width: 55%;
    }
    .right-column {
        width: 40%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }
    .feature-item {
        margin-bottom: 20px;
    }
    .feature-title {
        color: #ffa500;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 4px;
    }
    .feature-desc {
        color: #dddddd;
        font-size: 14px;
        line-height: 1.4;
    }
    .side-img {
        max-width: 100%;
        max-height: 50%;
        object-fit: contain;
    }
    .right-column img:last-child {
        margin-top: -250px;
    }
    .specs-container {
        margin-top: 20px;
        width: 100%;
    }
    .spec-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #283246;
        font-size: 14px;
    }
    .spec-label {
        color: #b4b4b4;
        font-weight: 700;
        width: 40%;
    }
    .spec-value {
        color: #ffffff;
        width: 60%;
        text-align: right;
        }
    .footer-tech{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
        height: 150px;
    }
    .apps-box {
        width: 80%;
    }
    .apps-title {
        color: #ffa500;
        font-weight: 700;
        font-size: 16px;
        margin-bottom: 8px;
    }
    .apps-text {
        color: #cccccc;
        font-size: 14px;
        line-height: 1.4;
    }
    .tech-img {
        width: 85%;
        max-height: 100%;
        object-fit: contain;
    }
    .cta-banner {
        position: absolute;
        bottom: 40px;
        left: 40px;
        right: 40px;
        background: #00d2ff;
        color: #0a1426;
        text-align: center;
        padding: 15px;
        font-weight: 700;
        font-size: 16px;
        letter-spacing: 1px;
        border-radius: 4px;
    }
    """

def procesar_catalogos():
    # 🛠️ Solución para Windows (Asignación de DLLs del entorno GTK)
    ruta_dlls = r"C:\Program Files\GTK2-Runtime-Win64\bin"
    if os.path.exists(ruta_dlls):
        os.environ["WEASYPRINT_DLL_DIRECTORIES"] = ruta_dlls

    estilos_css = obtener_estilos_base_css()
    html_bloques_unificados = []
    
    print("🔍 Buscando productos y armando código estructurado...")
    
    for nombre_producto in os.listdir(DIRECTORIO_RAIZ):
        ruta_producto = os.path.join(DIRECTORIO_RAIZ, nombre_producto)
        if not os.path.isdir(ruta_producto) or nombre_producto.startswith('.') or nombre_producto in ['env', 'venv']:
            continue
            
        ruta_txt = os.path.join(ruta_producto, "descripcion.txt")
        if not os.path.exists(ruta_txt):
            continue
            
        print(f"📦 Procesando datos y estructurando HTML de: '{nombre_producto}'")
        datos = parsear_descripcion(ruta_txt)
        
        # Recortamos los fondos de las fotos antes de armar el HTML
        print(f"  ✂️ Minimizando fondos de imágenes para maximizar tamaño...")
        for f in ["foto1.png", "foto2.png", "foto3.png", "foto4.png", "foto5.png"]:
            p = os.path.join(ruta_producto, f)
            if os.path.exists(p):
                recortar_fondo_al_ras(p)

        # 1. Generamos el contenido estructural de este producto específico
        bloque_producto = generar_html_bloque_producto(datos, nombre_producto)
        
        # 2. Creamos y guardamos el archivo HTML completo e independiente dentro de su propia carpeta
        html_independiente = f"""<!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="utf-8">
                                <link href="https://googleapis.com" rel="stylesheet">
                                <style>{estilos_css}</style>
                            </head>
                            <body>
                                {bloque_producto}
                            </body>
                            </html>"""

        ruta_archivo_html = os.path.join(ruta_producto, "flyers_producto.html")
        with open(ruta_archivo_html, "w", encoding="utf-8") as f_html:
            f_html.write(html_independiente)
        print(f"  ↳ 📄 Archivo HTML local guardado en: {ruta_archivo_html}")
        
        # 3. Guardamos una copia adaptando las rutas para el gran PDF unificado en la raíz
        bloque_adaptado_raiz = bloque_producto.replace('src="./', f'src="./{nombre_producto}/')
        html_bloques_unificados.append(bloque_adaptado_raiz)

    # =========================================================================
    # RENDERIZADO DEL CATÁLOGO ÚNICO EN LA RAÍZ (Fuera del bucle for)
    # =========================================================================
    if html_bloques_unificados:
        print("\n🚀 Compilando el catálogo maestro consolidado...")
        
        html_maestro_string = f"""<!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="utf-8">
                                <link href="https://googleapis.com" rel="stylesheet">
                                <style>{estilos_css}</style>
                            </head>
                            <body>
                                {"".join(html_bloques_unificados)}
                            </body>
                            </html>"""

        ruta_pdf_final = os.path.join(DIRECTORIO_RAIZ, "catalogo_completo.pdf")
        try:
            # Forzamos la base_url en la raíz '.' para mapear correctamente las subcarpetas
            HTML(string=html_maestro_string, base_url=".").write_pdf(ruta_pdf_final)
            print(f"\n✨ ¡ÉXITO TOTAL! Catálogo unificado generado en: {os.path.abspath(ruta_pdf_final)}")
        except Exception as e:
            print(f"\n⚠️ Error crítico al compilar el PDF consolidado: {e}")
    else:
        print("\n❌ No se encontraron productos válidos para procesar.")


if __name__ == "__main__":
    procesar_catalogos()
