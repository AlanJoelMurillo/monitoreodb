from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import pyodbc
import environ
import os
from django.utils import timezone
import socket
import json

#variables de entorno
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env = environ.Env(DEBUG=(bool,False))
env.read_env(os.path.join(BASE_DIR,".env"))
SOCKET_PATH = "/tmp/frecuencia.sock"


#variables de entorno
credentials = [
        {"ip":env("DB_MPIO3_IP"),"pass":env("DB_MPIO3_PASS"), "name":env("DB_MPIO3_NAME")},
        {"ip":env("DB_MPIO4_IP"),"pass":env("DB_MPIO4_PASS"), "name":env("DB_MPIO4_NAME")},
        {"ip":env("DB_MPIOACT_IP"),"pass":env("DB_MPIOACT_PASS"), "name":env("DB_MPIOACT_NAME")},
        {"ip":env("DB_MPIOAF_IP"),"pass":env("DB_MPIOAF_PASS"), "name":env("DB_MPIOAF_NAME")},
        {"ip":env("DB_MPIOPRE_IP"),"pass":env("DB_MPIOPRE_PASS"), "name":env("DB_MPIOPRE_NAME")},
        {"ip":env("DB_MPIOAE_IP"),"pass":env("DB_MPIOAE_PASS"), "name":env("DB_MPIOAE_NAME")},
        {"ip":env("DB_MPIOPRU_IP"),"pass":env("DB_MPIOPRU_PASS"), "name":env("DB_MPIOPRU_NAME")},
]


#Mostrar estado de servidores
@login_required
def show_status(request):
    newDic = {}         #diccionario con IPs y Status
    i = 0               #variable de iteracion

    #Se crea un string con las credenciales
    for cred in credentials:
        i = i + 1
        conn_str = f'DRIVER={{{env("DRIVER")}}};SERVER={cred["ip"]};PORT=5000;DATABASE=master;UID=usr_monitorweb;PWD={cred["pass"]};TDS_Version=5.0;'

        try: 
            newDic[i] = {
                 "id" : i,
                 "ipaddr": cred["ip"],
                 "status": "down",
                 "server": cred["name"]
            }
            
            conn = pyodbc.connect(conn_str,timeout=1)
            cursor = conn.cursor()
            cursor.execute("sp_who2")
            newDic[i]["status"] = "running"
            conn.close()

            
        except pyodbc.Error as e:
            print(" Error de conexión o ejecución del SP:", e)

        except Exception as e:
            print(" Error inesperado:", e)
            return HttpResponse("Error: " + str(e) )
    now = timezone.now()

    context = { 
        "data": newDic,
        "time" :now,
        }
    return render(request, "db_monitor/app.html",context)

@login_required
def check_status(request):
    newDic = {}         #diccionario con IPs y Status
    i = 0    
    for cred in credentials:
        i = i + 1
        conn_str = f'DRIVER={{{env("DRIVER")}}};SERVER={cred["ip"]};PORT=5000;DATABASE=master;UID=usr_monitorweb;PWD={cred["pass"]};TDS_Version=5.0;'
        try: 
            newDic[i] = {
                 "id" : i,
                 "status": "down",
            }
            
            conn = pyodbc.connect(conn_str,timeout=1)
            cursor = conn.cursor()
            cursor.execute("sp_who2")
            newDic[i]["status"] = "running"
            conn.close()

        except pyodbc.Error as e:
            print(" Error de conexión o ejecución del SP:", e)

        except Exception as e:
            print(" Error inesperado:", e)
    now = timezone.now().isoformat()
    context = { "data": newDic,
                "time": now}
    return JsonResponse(context)



#Mostrar reporte de servidor

@login_required
def show_report(request,server):
    for cred in credentials:
         if cred["name"] == server:
            conn_str = f'DRIVER={{{env("DRIVER")}}};SERVER={cred["ip"]};PORT=5000;DATABASE=master;UID=usr_monitorweb;PWD={cred["pass"]};TDS_Version=5.0;'
            try: 
                conn = pyodbc.connect(conn_str,timeout=1)
                cursor = conn.cursor()
                cursor.execute("sp_who2")
                columnas = [col[0] for col in cursor.description]
                resultados = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
                context = {"reporte" : resultados}
         
                conn.close()
                
                return render(request,"db_monitor/reporte.html",context)
            
            except pyodbc.Error as e:
                errorContext = {"error":e}
                print(" Error de conexión o ejecución del SP:", e)
                return render(request, "db_monitor/error.html",errorContext)

            except Exception as e:
                errorContext = {"error":e}
                print(" Error inesperado:", e)
                return render(request, "db_monitor/error.html",errorContext)

def enviar_comando_unix(data_dict):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as cliente:
            cliente.connect(SOCKET_PATH)
            mensaje = json.dumps(data_dict).encode()
            cliente.sendall(mensaje)
            respuesta = cliente.recv(1024)
            return respuesta.decode()
    except Exception as e:
        print("Error al comunicarse con el socket Unix:", e)
        return "Servidor Apagado, logica correcta"

@login_required
def mensajeria(request):
    mensaje_respuesta = ""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")
            value = data.get("value")
            if action in ["change_state", "pause_messages", "change_interval"]:
                mensaje_respuesta = enviar_comando_unix({"action": action, "value": value})
                return JsonResponse({"respuesta": mensaje_respuesta})
            else:
                mensaje_respuesta = "Acción no válida"
        except json.JSONDecodeError:
            mensaje_respuesta = "Error al decodificar JSON"
        except Exception as e:
            mensaje_respuesta = f"Error inesperado: {e}"
    return render(request, "db_monitor/mensajeria.html", {"respuesta": mensaje_respuesta})

def login(request):
    
    return render(request,"db_monitor/login.html")
    



