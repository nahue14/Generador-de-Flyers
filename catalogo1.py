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
    
    tabs_nav_html = ""
    tabs_content_html = ""

    # Configuración de los nombres de los flyers exactos y sus etiquetas visuales
    flyers_config = [
        ("flyer_1_impacto", "Impacto"),
        ("flyer_2_caracteristicas", "Características"),
        ("flyer_3_tecnico", "Técnico")
    ]

    for index, prod_dir in enumerate(productos_dirs):
        nombre_producto = os.path.basename(prod_dir).replace("_", " ")
        prod_id = f"producto-{index}"
        is_active = "active" if index == 0 else ""

        # Leer archivo de texto (descripcion)
        txt_files = glob.glob(os.path.join(prod_dir, "*.txt"))
        descripcion = "Sin descripción disponible."
        if txt_files:
            try:
                with open(txt_files[0], "r", encoding="utf-8") as f:
                    descripcion = f.read().strip().replace("\n", "<br>")
            except Exception as e:
                descripcion = f"Error al leer descripción: {e}"

        # Buscar específicamente los flyers de la configuración
        galeria_html = ""
        for base_name, etiqueta in flyers_config:
            img_encontrada = None
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidato = os.path.join(prod_dir, f"{base_name}{ext}")
                if os.path.exists(candidato):
                    img_encontrada = candidato
                    break
            
            if img_encontrada:
                img_rel_path = os.path.relpath(img_encontrada, BASE_DIR)
                galeria_html += f'<div class="gallery-item"><img src="{img_rel_path}" alt="{nombre_producto} - {etiqueta}" loading="lazy"><span>{etiqueta}</span></div>'
            else:
                galeria_html += f'<div class="gallery-item placeholder"><span>Falta {base_name}.jpg</span></div>'

        # Botón de pestaña (Navigation Tab)
        tabs_nav_html += f'<button class="tab-btn {is_active}" onclick="openTab(event, \'{prod_id}\')">{nombre_producto}</button>\n'

        # Contenido de la pestaña (Tab Content)
        tabs_content_html += f"""
        <div id="{prod_id}" class="tab-content {is_active}">
            <div class="product-detail-container">
                <div class="product-info">
                    <h2>{nombre_producto}</h2>
                    <p>{descripcion}</p>
                </div>
                <div class="product-gallery">
                    {galeria_html}
                </div>
            </div>
        </div>
        """

    # Plantilla HTML completa con estilos para Pestañas (Tabs)
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
                padding: 30px 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            header h1 {{
                margin: 0;
                font-size: 2.3em;
                letter-spacing: 1px;
            }}
            header p {{
                margin: 10px 0 0 0;
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .container {{
                max-width: 1100px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            /* Estilos de las Pestañas (Tabs) */
            .tabs-nav {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                border-bottom: 2px solid #ddd;
                margin-bottom: 20px;
                padding-bottom: 10px;
            }}
            .tab-btn {{
                background-color: #e0e0e0;
                border: none;
                padding: 12px 20px;
                cursor: pointer;
                font-size: 1em;
                font-weight: 600;
                border-radius: 8px 8px 0 0;
                transition: background 0.3s, color 0.3s;
                color: #555;
            }}
            .tab-btn:hover {{
                background-color: var(--light-green);
                color: white;
            }}
            .tab-btn.active {{
                background-color: #1b4d3e;
                color: white;
            }}
            .tab-content {{
                display: none;
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.08);
                padding: 30px;
                animation: fadeIn 0.4s ease-in-out;
            }}
            .tab-content.active {{
                display: block;
            }}
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(5px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            .product-detail-container {{
                display: flex;
                flex-direction: column;
                gap: 25px;
            }}
            .product-info h2 {{
                margin-top: 0;
                color: #1b4d3e;
                font-size: 1.8em;
                border-bottom: 2px solid var(--light-green);
                padding-bottom: 8px;
            }}
            .product-info p {{
                line-height: 1.6;
                color: #555;
                font-size: 1.05em;
            }}
            .product-gallery {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}
            .gallery-item {{
                background: #fafafa;
                border: 1px solid #eee;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
            }}
            .gallery-item img {{
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 6px;
            }}
            .gallery-item span {{
                display: block;
                margin-top: 8px;
                font-size: 0.9em;
                color: #666;
                font-weight: bold;
            }}
            .gallery-item.placeholder {{
                display: flex;
                align-items: center;
                justify-content: center;
                height: 200px;
                background: #eee;
                color: #999;
                font-style: italic;
            }}
            footer {{
                text-align: center;
                padding: 25px;
                background: #2c3e50;
                color: white;
                margin-top: 60px;
                font-size: 0.9em;
            }}
        </style>
        <script>
            function openTab(evt, tabId) {{
                const contents = document.getElementsByClassName("tab-content");
                for (let i = 0; i < contents.length; i++) {{
                    contents[i].classList.remove("active");
                }}
                const buttons = document.getElementsByClassName("tab-btn");
                for (let i = 0; i < buttons.length; i++) {{
                    buttons[i].classList.remove("active");
                }}
                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
            }}
        </script>
    </head>
    <body>
        <header>
            <h1>EXSEI S.A.</h1>
            <p>Catálogo Oficial de Productos - Sistema de Pestañas Interactivas</p>
        </header>

        <div class="container">
            <!-- Botones de Navegación por Pestañas -->
            <div class="tabs-nav">
                {tabs_nav_html}
            </div>

            <!-- Contenido de las Pestañas -->
            {tabs_content_html}
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
    
    print(f"¡Catálogo con pestañas generado con éxito! Guárdalo y ábrelo desde: {output_path}")

if __name__ == "__main__":
    generar_catalogo()