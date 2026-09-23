import os
import glob
import shutil
from PIL import Image

# Ruta base donde están las carpetas originales de los productos
BASE_DIR = r"./"
# Carpeta principal de destino solicitada
DEST_DIR = "./FlayersCatalogo"

def extraer_y_agrupar_flyers():
    if not os.path.exists(BASE_DIR):
        print(f"No se encontró la ruta base: {BASE_DIR}. Por favor verifica la dirección.")
        return

    # Crear la carpeta de destino principal si no existe
    os.makedirs(DEST_DIR, exist_ok=True)

    # Buscar todas las subcarpetas (productos)
    productos_dirs = [os.path.join(BASE_DIR, d) for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d))]

    # Nombres base de los archivos que queremos buscar y extraer
    flyers_nombres = [
        "flyer_1_impacto",
        "flyer_2_caracteristicas",
        "flyer_3_tecnico"
    ]

    total_procesados = 0
    archivos_imagen = []
    
    for prod_dir in productos_dirs:
        nombre_producto = os.path.basename(prod_dir)
        dest_prod_dir = os.path.join(DEST_DIR, nombre_producto)
        
        encontrados = []
        
        # Buscar cada flyer individualmente con sus posibles extensiones
        for base_name in flyers_nombres:
            img_encontrada = None

            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                candidato = os.path.join(prod_dir, f"{base_name}{ext}")
                if os.path.exists(candidato):

                    # AGREGADO PARA GENERAR PDF
                    archivos_imagen.append(prod_dir + '/' + base_name + ext) 
                    
                    img_encontrada = (candidato, f"{base_name}{ext}")
                    break
            if img_encontrada:
                encontrados.append(img_encontrada)

    
        # Si se encontró al menos un flyer, crear la carpeta de destino y copiar los archivos
        if encontrados:
            os.makedirs(dest_prod_dir, exist_ok=True)
            for src_path, file_name in encontrados:
                dest_path = os.path.join(dest_prod_dir, file_name)
                shutil.copy2(src_path, dest_path)
                print(f"[{nombre_producto}] Copiado: {file_name}")
            total_procesados += 1
        else:
            print(f"Aviso: No se encontraron flyers en la carpeta del producto '{nombre_producto}'.")

    # GENERAR PDF
    # Abrir todas las imágenes y convertirlas en objetos de Pillow
    print(archivos_imagen)
    imagenes = [Image.open(img).convert("RGB") for img in archivos_imagen]
    # Definir la ruta del PDF resultante
    ruta_pdf = "./salida.pdf"
    # Guardar la primera imagen agregando el resto
    imagenes[0].save(
        ruta_pdf,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=imagenes[1:]
    )



    print(f"\n¡Proceso completado con éxito!")
    print(f"Se estructuraron {total_procesados} carpetas de productos en: {os.path.abspath(DEST_DIR)}")

if __name__ == "__main__":
    extraer_y_agrupar_flyers()