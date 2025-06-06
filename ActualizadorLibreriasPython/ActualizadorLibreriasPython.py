import subprocess
import sys

def fActualizarLibrerias():
   """Actualiza todas las librerías de Python instaladas usando pip."""
   try:
      print("Obteniendo la lista de librerías instaladas...")
      resultado = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], capture_output=True, text=True, check=True)
      lineas = resultado.stdout.strip().split('\n')
      if len(lineas) > 2:  # Ignorar la cabecera
         print("Se encontraron las siguientes librerías desactualizadas:")
         librerias_actualizar = []
         for linea in lineas[2:]:
            partes = linea.split()
            libreria = partes[0]
            version_actual = partes[1]
            version_nueva = partes[2]
            print(f"- {libreria} (Versión actual: {version_actual}, Nueva versión disponible: {version_nueva})")
            librerias_actualizar.append(libreria)

         if librerias_actualizar:
            print("\nIniciando la actualización de las librerías...")
            for libreria in librerias_actualizar:
               print(f"Actualizando {libreria}...")
               try:
                  subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', libreria], check=True)
                  print(f"  {libreria} se actualizó correctamente.")
               except subprocess.CalledProcessError as e:
                  print(f"  Error al actualizar {libreria}: {e}")
            print("\nProceso de actualización completado.")
         else:
            print("\nNo se encontraron librerías desactualizadas.")
      else:
         print("\nNo se encontraron librerías desactualizadas.")

   except subprocess.CalledProcessError as e:
      print(f"Error al obtener la lista de librerías desactualizadas: {e}")
   except FileNotFoundError:
      print("Error: 'pip' no se encontró. Asegúrate de que pip esté instalado y en tu PATH.")
   except Exception as e:
      print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
   fActualizarLibrerias()