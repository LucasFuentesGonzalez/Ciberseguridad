import os
import psutil
from dotenv import load_dotenv
from datetime import datetime

# Constants for better readability
MB_DIVISOR = 1024 ** 2  # Divisor to convert bytes to MB
GB_DIVISOR = 1024 ** 3  # Divisor to convert bytes to GB

def fGuardarResultado(strNombreArchivo, strContenido):
   """
   Guarda los resultados del análisis en un archivo de texto.
   
   Args:
      strNombreArchivo (str): Nombre del archivo donde se guardarán los datos
      strContenido (str): Contenido a guardar en el archivo
   
   Returns:
      None
   """
   # Cargar el archivo .env
   load_dotenv()
   # Obtener la ruta desde el archivo .env
   # Ruta donde se guardarán los archivos de resultados
   sRUTA_DIRECTORIO = os.getenv('RUTA_DIRECTORIO')
   
   # Crear la carpeta si no existe
   os.makedirs(sRUTA_DIRECTORIO, exist_ok=True)
   
   # Construir la ruta completa del archivo
   strRutaArchivoTxt = os.path.join(sRUTA_DIRECTORIO, strNombreArchivo + ".txt")

   # Guardar como archivo de texto con codificación UTF-8
   with open(strRutaArchivoTxt, 'w', encoding='utf-8') as objArchivoTxt:
      objArchivoTxt.write(strContenido)
   
   print(f"INFO    - Resultado guardado en: {strRutaArchivoTxt}")


def fObtenerMemoriaSistema():
   """
   Obtiene información detallada sobre el uso de memoria del sistema y memoria swap.
   
   Returns:
      str: Cadena con la información formateada sobre el uso de memoria
   """
   # Obtener objetos con información de memoria
   objMem = psutil.virtual_memory()
   objSwap = psutil.swap_memory()

   # Construir el informe de memoria
   strContenido = "===== INFORMACIÓN DE MEMORIA DEL SISTEMA =====\n"
   strContenido += f"Total de memoria: {objMem.total / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Memoria disponible: {objMem.available / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Memoria en uso: {objMem.used / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Porcentaje de memoria usada: {objMem.percent}%\n\n"
   
   # Añadir información sobre la memoria swap
   strContenido += "===== INFORMACIÓN DE MEMORIA SWAP =====\n"
   strContenido += f"Total de memoria swap: {objSwap.total / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Memoria swap en uso: {objSwap.used / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Porcentaje de memoria swap usada: {objSwap.percent}%\n"

   return strContenido


def fListarProcesos(fUmbralMemoria=0):
   """
   Lista todos los procesos activos y su uso de memoria, filtrando por un umbral mínimo.
   
   Args:
      fUmbralMemoria (float): Umbral mínimo de memoria en MB para incluir un proceso
   
   Returns:
      tuple: (lista de procesos ordenados, cadena con la información formateada)
   """
   # Lista para almacenar la información de los procesos
   lstProcesos = []
   
   # Iterar sobre todos los procesos del sistema
   for objProc in psutil.process_iter(['pid', 'name', 'memory_info']):
      try:
         # Calcular la memoria en MB
         fMemoriaMB = objProc.info['memory_info'].rss / MB_DIVISOR
         
         # Aplicar filtro por umbral de memoria
         if fMemoriaMB > fUmbralMemoria:
               iTuple = (objProc.info['pid'], objProc.info['name'], fMemoriaMB)
               lstProcesos.append(iTuple)
      except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
         # Ignorar procesos que ya no existen o a los que no se puede acceder
         pass

   # Ordenar los procesos por memoria utilizada (de mayor a menor)
   lstProcesosOrdenados = sorted(lstProcesos, key=lambda x: x[2], reverse=True)

   # Construir el informe de procesos
   strContenido = "\n===== PROCESOS ACTIVOS POR USO DE MEMORIA =====\n"
   strContenido += f"(Mostrando procesos con más de {fUmbralMemoria} MB de uso)\n\n"
   
   # Formato de cabecera para mejor legibilidad
   strContenido += f"{'PID':<8} {'MEMORIA (MB)':<15} {'NOMBRE':<40}\n"
   strContenido += "-" * 63 + "\n"
   
   # Añadir cada proceso a la salida
   for iPid, strName, fMemoria in lstProcesosOrdenados:
      strContenido += f"{iPid:<8} {fMemoria:<15.2f} {strName:<40}\n"
   
   return lstProcesosOrdenados, strContenido


def fUsoMemoriaProceso(iPid):
   """
   Obtiene información detallada sobre la memoria utilizada por un proceso específico.
   
   Args:
      iPid (int): ID del proceso a analizar
   
   Returns:
      str: Cadena con la información formateada sobre el uso de memoria del proceso
   """
   try:
      # Obtener el objeto del proceso
      objProc = psutil.Process(iPid)
      
      # Obtener información de memoria
      objMemoryInfo = objProc.memory_info()
      
      # Obtener nombre e información adicional del proceso
      strNombreProc = objProc.name()
      
      # Intentar obtener el usuario (puede fallar en algunos casos)
      try:
         strUsuario = objProc.username()
      except:
         strUsuario = "N/A"
         
      strTiempoCreacion = datetime.fromtimestamp(objProc.create_time()).strftime('%Y-%m-%d %H:%M:%S')
      
      # Construir el informe detallado
      strContenido = f"\n===== DETALLES DE MEMORIA DEL PROCESO (PID: {iPid}) =====\n"
      strContenido += f"Nombre del proceso: {strNombreProc}\n"
      strContenido += f"Usuario: {strUsuario}\n"
      strContenido += f"Tiempo de creación: {strTiempoCreacion}\n\n"
      
      # Información sobre memoria RSS (siempre disponible)
      strContenido += f"Memoria física (RSS): {objMemoryInfo.rss / MB_DIVISOR:.2f} MB\n"
      
      # Información sobre memoria VMS (siempre disponible)
      strContenido += f"Memoria virtual (VMS): {objMemoryInfo.vms / MB_DIVISOR:.2f} MB\n"
      
      # Comprobar si atributos adicionales están disponibles (dependiente del sistema)
      # Usar hasattr para comprobar si el atributo existe antes de acceder a él
      if hasattr(objMemoryInfo, 'shared'):
         strContenido += f"Memoria compartida: {objMemoryInfo.shared / MB_DIVISOR:.2f} MB\n"
         
      if hasattr(objMemoryInfo, 'private'):
         strContenido += f"Memoria privada: {objMemoryInfo.private / MB_DIVISOR:.2f} MB\n"
      
      # Obtener información adicional si está disponible
      try:
         fPercentCPU = objProc.cpu_percent(interval=0.1)
         strContenido += f"Uso de CPU: {fPercentCPU:.1f}%\n"
      except:
         pass
         
      # Intentar obtener información de archivos abiertos
      try:
         lstArchivos = objProc.open_files()
         if lstArchivos:
               strContenido += f"\nArchivos abiertos ({len(lstArchivos)}):\n"
               # Mostrar solo los primeros 5 archivos para no sobrecargar el informe
               for i, archivo in enumerate(lstArchivos[:5]):
                  strContenido += f"  {i+1}. {archivo.path}\n"
               if len(lstArchivos) > 5:
                  strContenido += f"  ... y {len(lstArchivos) - 5} más\n"
      except:
         pass
         
      return strContenido
   except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
      return f"[!] Error: No se pudo obtener información del proceso con PID {iPid}.\n"


def fObtenerTopProcesos(iNumProcesos=5):
   """
   Obtiene información detallada sobre los N procesos que más memoria utilizan.
   
   Args:
      iNumProcesos (int): Número de procesos a analizar
   
   Returns:
      str: Cadena con la información formateada de los procesos que más memoria consumen
   """
   # Obtener todos los procesos ordenados por uso de memoria
   lstProcesosOrdenados, _ = fListarProcesos(fUmbralMemoria=0)
   
   # Validar que haya suficientes procesos
   iNumProcesosReal = min(iNumProcesos, len(lstProcesosOrdenados))
   
   # Tomar solo los N procesos principales
   lstTopProcesos = lstProcesosOrdenados[:iNumProcesosReal]
   
   # Construir el informe detallado
   strContenido = f"\n===== TOP {iNumProcesosReal} PROCESOS POR CONSUMO DE MEMORIA =====\n\n"
   
   # Analizar cada uno de los procesos top
   for i, (iPid, strName, _) in enumerate(lstTopProcesos, 1):
      strContenido += f"--- Proceso #{i} ---"
      strContenido += fUsoMemoriaProceso(iPid)
      strContenido += "\n"
   
   return strContenido


def fCapturarPantallaMemoria():
   """
   Genera un informe resumido con la información clave de memoria del sistema.
   
   Returns:
      str: Cadena con el resumen de memoria
   """
   # Obtener información de memoria
   objMem = psutil.virtual_memory()
   
   # Obtener todos los procesos ordenados por uso de memoria
   lstProcesosOrdenados, _ = fListarProcesos(fUmbralMemoria=100)  # Filtrar por más de 100MB
   
   # Tomar los 10 procesos principales
   lstTopProcesos = lstProcesosOrdenados[:10]
   
   # Construir informe resumido
   strContenido = "===== RESUMEN DE MEMORIA DEL SISTEMA =====\n"
   strContenido += f"Memoria Total: {objMem.total / GB_DIVISOR:.2f} GB\n"
   strContenido += f"Memoria En Uso: {objMem.used / GB_DIVISOR:.2f} GB ({objMem.percent}%)\n"
   strContenido += f"Memoria Disponible: {objMem.available / GB_DIVISOR:.2f} GB\n\n"
   
   strContenido += "TOP 10 PROCESOS POR CONSUMO DE MEMORIA:\n"
   strContenido += f"{'PID':<8} {'MEMORIA (MB)':<15} {'NOMBRE':<40}\n"
   strContenido += "-" * 63 + "\n"
   
   for iPid, strName, fMemoria in lstTopProcesos:
      strContenido += f"{iPid:<8} {fMemoria:<15.2f} {strName:<40}\n"
   
   return strContenido


def main():
   """
   Función principal que ejecuta el análisis completo de memoria y guarda los resultados.
   Coordina la ejecución de las diferentes funciones de análisis y combina sus resultados.
   """
   print("INFO    - Iniciando análisis de memoria del sistema y procesos...")

   try:
      # Obtener la información de la memoria del sistema
      strResultadoMemoria = fObtenerMemoriaSistema()

      # Listar los procesos y ordenarlos por la memoria utilizada (umbral de 50MB)
      _, strResultadoProcesos = fListarProcesos(fUmbralMemoria=50)

      # Obtener información detallada de los 3 procesos que más memoria consumen
      strTopProcesos = fObtenerTopProcesos(iNumProcesos=3)

      # Generar captura rápida del estado de memoria
      strCaptura = fCapturarPantallaMemoria()

      # Si se desea analizar un proceso específico por su PID
      # Comentar esta línea o cambiar a un PID válido
      # iPidAnalizar = 1234  # Cambia esto por el PID de un proceso válido que desees analizar
      # strAnalisisPid = fUsoMemoriaProceso(iPidAnalizar)
      
      # Como alternativa, buscar un proceso conocido como explorer.exe (Windows) o systemd (Linux)
      strAnalisisPid = ""
      bPidEncontrado = False
      
      # Intentar encontrar un proceso conocido según el sistema operativo
      for objProc in psutil.process_iter(['pid', 'name']):
         try:
               strNombreProc = objProc.info['name'].lower()
               if "explorer" in strNombreProc or "systemd" in strNombreProc:
                  iPidAnalizar = objProc.info['pid']
                  strAnalisisPid = fUsoMemoriaProceso(iPidAnalizar)
                  bPidEncontrado = True
                  break
         except:
               continue
      
      if not bPidEncontrado:
         strAnalisisPid = "INFO    - No se analizó ningún proceso específico por PID\n"

      # Obtener fecha y hora actual para el informe
      strFechaHora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
      # Construir el informe completo
      strContenidoFinal = f"===========================================\n"
      strContenidoFinal += f"ANÁLISIS DE MEMORIA DEL SISTEMA\n"
      strContenidoFinal += f"Fecha y hora: {strFechaHora}\n"
      strContenidoFinal += f"===========================================\n\n"
      strContenidoFinal += strCaptura
      strContenidoFinal += "\n\n"
      strContenidoFinal += strResultadoMemoria
      strContenidoFinal += strResultadoProcesos
      strContenidoFinal += strTopProcesos
      strContenidoFinal += strAnalisisPid

      # Guardar el resultado en un archivo
      strNombreArchivo = f"AnalisisMemoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
      fGuardarResultado(strNombreArchivo, strContenidoFinal)
      
      print("INFO    - Análisis de memoria completado exitosamente!")
      
   except Exception as e:
      print(f"ERROR   - Se produjo un error durante el análisis: {str(e)}")


# Punto de entrada del script
if __name__ == "__main__":
   main()
