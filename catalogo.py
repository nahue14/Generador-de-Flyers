import os
import glob

# Ruta base donde están las carpetas de los productos
BASE_DIR = r"./"

def generar_catalogo():
    if not os.path.exists(BASE_DIR):
        print(f"No se encontró la ruta: {BASE_DIR}. Por favor verifica la dirección.")
        return

    # Buscar todas las subcarpetas (productos)
    productos_dirs = [os.path.join(BASE_DIR, d) for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]
    
    productos_html = ""

    for prod_dir in productos_dirs:
        nombre_producto = os.path.basename(prod_dir).replace("_", " ")
        
        # Leer archivo de texto (descripcion)
        txt_files = glob.glob(os.path.join(prod_dir, "*.txt"))
        descripcion = "Sin descripción disponible."
        if txt_files:
            try:
                with open(txt_files[0], "r", encoding="utf-8") as f:
                    descripcion = f.read().strip().replace("\n", "<br>")
            except Exception as e:
                descripcion = f"Error al leer descripción: {e}"

        # Buscar imágenes (jpg, jpeg, png, webp)
        imagenes = []
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            imagenes.extend(glob.glob(os.path.join(prod_dir, ext)))
        
        # Generar HTML para las imágenes del producto
        galeria_html = ""
        for img_path in imagenes:
            # Ruta relativa para el HTML
            img_rel_path = os.path.relpath(img_path, BASE_DIR)
            galeria_html += f'<img src="{img_rel_path}" alt="{nombre_producto}" loading="lazy">'

        if not galeria_html:
            galeria_html = '<p class="sin-imagen">Sin imágenes disponibles</p>'

        # Estructura HTML de la tarjeta de producto
        productos_html += f"""
        <div class="product-card">
            <div class="product-images">
                {galeria_html}
            </div>
            <div class="product-info">
                <h2>{nombre_producto}</h2>
                <p>{descripcion}</p>
            </div>
        </div>
        """

    # Plantilla HTML completa con los estilos y colores corporativos de EXSEI
    html_template = f"""<!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Productos - EXSEI S.A.</title>
        <style>
            :root {{
                --primary-green: #27ae60;
                --light-green: #2ecc71;
                --dark-bg: #1a1a1a;
                --card-bg: #ffffff;
                --text-color: #333333;
                --gray-bg: #f4f6f7;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--gray-bg);
                color: var(--text-color);
                margin: 0;
                padding: 0;
            }}
            header {{
                background: linear-gradient(135deg, #1b4d3e, var(--primary-green));
                color: white;
                text-align: center;
                padding: 40px 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            header h1 {{
                margin: 0;
                font-size: 2.5em;
                letter-spacing: 1px;
            }}
            header p {{
                margin: 10px 0 0 0;
                font-size: 1.2em;
                opacity: 0.9;
            }}
            .container {{
                max-width: 1200px;
                margin: 40px auto;
                padding: 0 20px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 30px;
            }}
            .product-card {{
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.08);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                transition: transform 0.3s ease;
            }}
            .product-card:hover {{
                transform: translateY(-5px);
            }}
            .product-images {{
                display: flex;
                overflow-x: auto;
                gap: 10px;
                padding: 15px;
                background: #fafafa;
                border-bottom: 1px solid #eee;
                scroll-snap-type: x mandatory;
            }}
            .product-images img {{
                width: 100%;
                height: 220px;
                object-fit: cover;
                border-radius: 8px;
                flex-shrink: 0;
                scroll-snap-align: center;
            }}
            .product-info {{
                padding: 20px;
                flex-grow: 1;
                display: flex;
                flex-direction: column;
            }}
            .product-info h2 {{
                margin-top: 0;
                color: #1b4d3e;
                font-size: 1.4em;
                border-bottom: 2px solid var(--light-green);
                padding-bottom: 8px;
            }}
            .product-info p {{
                line-height: 1.6;
                color: #555;
                font-size: 0.95em;
                flex-grow: 1;
            }}
            .sin-imagen {{
                color: #88f;
                font-style: italic;
                text-align: center;
                padding: 40px;
            }}
            footer {{
                text-align: center;
                padding: 30px;
                background: #2c3e50;
                color: white;
                margin-top: 60px;
                font-size: 0.9em;
            }}
            @media print {{
                body {{ background: white; }}
                .product-card {{ break-inside: avoid; box-shadow: none; border: 1px solid #ccc; }}
                .product-images {{ overflow: visible; }}
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>EXSEI S.A.</h1>
            <p>Catálogo Oficial de Productos - Nuestro nombre nos define</p>
        </header>

        <div class="container">
            {productos_html}
        </div>

        <footer>
            <p>EXSEI S.A. | Contacto: comercial@exsei.com.ar | www.exsei.com.ar</p>
        </footer>
    </body>
    </html>
    """

    output_path = os.path.join(BASE_DIR, "catalogo.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"¡Catálogo generado con éxito! Guárdalo y ábrelo desde: {output_path}")

if __name__ == "__main__":
    generar_catalogo()