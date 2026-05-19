from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters
import subprocess
import os
import datetime
import json
from PIL import ImageGrab
from dotenv import load_dotenv
from google import genai
import pyautogui
import asyncio
from io import BytesIO

# ================== CONFIG ==================
load_dotenv()

TOKEN = os.getenv("TOKEN")
PASSWORD = os.getenv("PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN:
    raise ValueError("No se encontró TOKEN en.env. Crea el archivo.env con TOKEN=tu_token")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró GEMINI_API_KEY en.env")

USERS_FILE = "usuarios_autorizados.json"
COMANDOS_FILE = "comandos_personalizados.json"
MEMORIA_FILE = "memoria_chat.json"

client = genai.Client(api_key=GEMINI_API_KEY)

def cargar_usuarios():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def guardar_usuarios(usuarios):
    with open(USERS_FILE, "w") as f:
        json.dump(list(usuarios), f)

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_memoria(memoria):
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

def cargar_comandos_personalizados():
    if os.path.exists(COMANDOS_FILE):
        with open(COMANDOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_comandos_personalizados(comandos):
    with open(COMANDOS_FILE, "w", encoding="utf-8") as f:
        json.dump(comandos, f, ensure_ascii=False, indent=2)

def construir_300_comandos():
    base_comandos = [
        ("dir", "Lista archivos. Uso: dir [ruta]", "dir"), ("cd", "Cambiar directorio. Uso: cd ruta", "cd"),
        ("mkdir", "Crear carpeta. Uso: mkdir nombre", "mkdir"), ("rmdir", "Borrar carpeta. Uso: rmdir nombre", "rmdir"),
        ("del", "Borrar archivo. Uso: del archivo", "del"), ("copy", "Copiar. Uso: copy origen destino", "copy"),
        ("move", "Mover. Uso: move origen destino", "move"), ("ren", "Renombrar. Uso: ren viejo nuevo", "ren"),
        ("type", "Ver archivo txt. Uso: type archivo.txt", "type"), ("cls", "Limpiar pantalla", "cls"),
        ("tree", "Ver árbol directorios", "tree"), ("attrib", "Cambiar atributos", "attrib"),
        ("xcopy", "Copiar avanzado", "xcopy"), ("robocopy", "Copia robusta", "robocopy"),
        ("find", "Buscar texto", "find"), ("findstr", "Buscar avanzado", "findstr"),
        ("sort", "Ordenar", "sort"), ("more", "Paginación", "more"), ("fc", "Comparar archivos", "fc"),
        ("comp", "Comparar binario", "comp"), ("where", "Buscar archivo", "where"), ("assoc", "Asociar archivos", "assoc"),
        ("ftype", "Tipo archivo", "ftype"), ("md", "Crear directorio", "md"), ("rd", "Borrar directorio", "rd"),
        ("erase", "Borrar", "erase"), ("rename", "Renombrar", "rename"), ("pushd", "Guardar dir", "pushd"),
        ("popd", "Volver directorio", "popd"), ("subst", "Montar unidad", "subst"),
        ("ipconfig", "Ver IP", "ipconfig"), ("ping", "Hacer ping. Uso: ping google.com", "ping"),
        ("tracert", "Rastrear ruta", "tracert"), ("netstat", "Ver conexiones", "netstat -an"),
        ("arp", "Tabla ARP", "arp -a"), ("route", "Tabla rutas", "route print"), ("nslookup", "DNS lookup", "nslookup"),
        ("hostname", "Nombre equipo", "hostname"), ("getmac", "MAC address", "getmac"), ("nbtstat", "NetBIOS stats", "nbtstat -n"),
        ("pathping", "Pathping", "pathping"), ("netsh", "Config red", "netsh"), ("net", "Comando net", "net"),
        ("wmic_nic", "Info red WMI", "wmic nic get"), ("netsh_wlan", "Redes wifi", "netsh wlan show networks"),
        ("tasklist", "Lista procesos", "tasklist"), ("taskkill", "Matar proceso. Uso: taskkill /im nombre.exe /f", "taskkill"),
        ("systeminfo", "Info del sistema", "systeminfo"), ("whoami", "Usuario actual", "whoami"), ("quser", "Usuarios conectados", "quser"),
        ("qprocess", "Procesos usuario", "qprocess"), ("openfiles", "Archivos abiertos", "openfiles /query"),
        ("driverquery", "Lista drivers", "driverquery"), ("wmic", "WMI Console", "wmic"), ("ver", "Versión CMD", "ver"),
        ("date", "Fecha sistema", "date /t"), ("time", "Hora sistema", "time /t"), ("msconfig", "Configuración sistema", "msconfig"),
        ("regedit", "Editor registro", "regedit"), ("gpedit", "Editor políticas", "gpedit.msc"), ("devmgmt", "Admin dispositivos", "devmgmt.msc"),
        ("diskmgmt", "Admin discos", "diskmgmt.msc"), ("services", "Servicios Windows", "services.msc"), ("eventvwr", "Visor eventos", "eventvwr.msc"),
        ("perfmon", "Monitor rendimiento", "perfmon"), ("resmon", "Monitor recursos", "resmon"), ("dxdiag", "Diagnóstico DirectX", "dxdiag"),
        ("winver", "Versión Windows", "winver"), ("control", "Panel control", "control"), ("appwiz", "Programas y características", "appwiz.cpl"),
        ("compmgmt", "Administración equipo", "compmgmt.msc"), ("lusrmgr", "Usuarios locales", "lusrmgr.msc"), ("secpol", "Política seguridad", "secpol.msc"),
        ("wf", "Firewall Windows", "wf.msc"), ("chkdsk", "Revisar disco", "chkdsk"), ("sfc", "Reparar sistema", "sfc /scannow"),
        ("dism", "Reparar imagen", "dism /online /cleanup-image /restorehealth"), ("defrag", "Desfragmentar", "defrag"),
        ("cleanmgr", "Liberar espacio", "cleanmgr"), ("diskpart", "Administrar discos", "diskpart"), ("format", "Formatear", "format"),
        ("convert", "Convertir FAT a NTFS", "convert"), ("compact", "Comprimir archivos", "compact"), ("fsutil", "Utilidad archivos", "fsutil"),
        ("vssadmin", "VSS Admin", "vssadmin list shadows"), ("wbadmin", "Windows Backup", "wbadmin"), ("notepad", "Bloc notas", "notepad"),
        ("paint", "Paint", "mspaint"), ("calc", "Calculadora", "calc"), ("wordpad", "Wordpad", "write"),
        ("snip", "Recortes", "snippingtool"), ("stiky", "Notas adhesivas", "stikynot"), ("magnify", "Lupa", "magnify"),
        ("osk", "Teclado en pantalla", "osk"), ("narrator", "Narrador", "narrator"), ("mplayer", "Media Player", "wmplayer"),
        ("photos", "Fotos", "start ms-photos:"), ("store", "Microsoft Store", "start ms-windows-store:"),
        ("settings", "Configuración", "start ms-settings:"), ("wifi", "Config wifi", "start ms-settings:network-wifi"),
        ("bluetooth", "Config bluetooth", "start ms-settings:bluetooth"), ("display", "Config pantalla", "start ms-settings:display"),
        ("sound", "Config sonido", "start ms-settings:sound"), ("apps", "Apps instaladas", "start ms-settings:appsfeatures"),
        ("storage", "Almacenamiento", "start ms-settings:storagesense"), ("battery", "Batería", "start ms-settings:batterysaver"),
        ("chrome", "Google Chrome", "start chrome"), ("edge", "Microsoft Edge", "start msedge"),
        ("firefox", "Mozilla Firefox", "start firefox"), ("opera", "Opera", "start opera"),
        ("vscode", "Visual Studio Code", "code"), ("notepadpp", "Notepad++", "notepad++"), ("spotify", "Spotify", "start spotify"),
        ("discord", "Discord", "start discord"), ("steam", "Steam", "start steam"), ("vlc", "VLC Player", "vlc"),
        ("7zip", "7-Zip", "7zFM"), ("winrar", "WinRAR", "winrar"), ("photoshop", "Photoshop", "photoshop"),
        ("illustrator", "Illustrator", "illustrator"), ("premiere", "Premiere Pro", "premiere"), ("word", "Microsoft Word", "winword"),
        ("excel", "Microsoft Excel", "excel"), ("powerpoint", "PowerPoint", "powerpnt"), ("outlook", "Outlook", "outlook"),
        ("teams", "Microsoft Teams", "teams"), ("python", "Python", "python --version"), ("pip", "PIP Python", "pip --version"),
        ("node", "Node.js", "node --version"), ("npm", "NPM", "npm --version"), ("git", "Git", "git --version"),
        ("java", "Java", "java -version"), ("javac", "Compilador Java", "javac -version"), ("docker", "Docker", "docker --version"),
        ("kubectl", "Kubernetes", "kubectl version"), ("powershell", "PowerShell", "powershell"), ("wsl", "WSL", "wsl --list"),
        ("gcc", "GCC Compiler", "gcc --version"), ("gpp", "G++ Compiler", "g++ --version"), ("cmake", "CMake", "cmake --version"),
        ("make", "Make", "make --version"), ("mvn", "Maven", "mvn --version"), ("gradle", "Gradle", "gradle --version"),
        ("composer", "Composer PHP", "composer --version"), ("php", "PHP", "php --version"), ("ruby", "Ruby", "ruby --version"),
        ("echo", "Mostrar texto", "echo"), ("pause", "Pausar", "pause"), ("timeout", "Esperar", "timeout"),
        ("choice", "Menú selección", "choice"), ("start", "Iniciar", "start"), ("call", "Llamar batch", "call"),
        ("goto", "Ir etiqueta", "goto"), ("if", "Condicional", "if"), ("for", "Bucle for", "for"), ("set", "Variables entorno", "set"),
        ("setx", "Set variable", "setx"), ("path", "Ver PATH", "path"), ("prompt", "Cambiar prompt", "prompt $P$G"),
        ("title", "Título", "title"), ("color", "Color consola", "color 0A"), ("mode", "Config dispositivo", "mode"),
        ("doskey", "Macros CMD", "doskey /history"), ("cmd", "Nueva CMD", "cmd"), ("exit", "Cerrar CMD", "exit"),
        ("help", "Ayuda CMD", "help"), ("shift", "Shift parámetros", "shift"), ("setlocal", "Inicio bloque", "setlocal"),
        ("endlocal", "Fin bloque", "endlocal"), ("verify", "Verificar escritura", "verify"), ("shutdown", "Apagar PC", "shutdown /s /t 0"),
        ("restart", "Reiniciar PC", "shutdown /r /t 0"), ("logoff", "Cerrar sesión", "logoff"), ("powercfg", "Config energía", "powercfg /list"),
        ("powercfg_battery", "Reporte batería", "powercfg /batteryreport"), ("shutdown_a", "Abortar apagado", "shutdown /a"),
        ("bcdedit", "Editar arranque", "bcdedit"), ("bootrec", "Reparar arranque", "bootrec"), ("winsat", "Test rendimiento", "winsat formal"),
        ("wevtutil", "Logs eventos", "wevtutil el"), ("logman", "Logs rendimiento", "logman query"), ("typeperf", "Rendimiento tiempo real", "typeperf"),
        ("sc", "Control servicios", "sc query"), ("schtasks", "Tareas programadas", "schtasks /query"), ("runas", "Ejecutar como admin", "runas"),
        ("takeown", "Tomar propiedad", "takeown"), ("icacls", "Permisos avanzados", "icacls"), ("cacls", "Permisos NTFS", "cacls"),
        ("cipher", "Cifrar archivos", "cipher"), ("certutil", "Certificados", "certutil"), ("certutil_hash", "Hash archivo", "certutil -hashfile"),
        ("makecab", "Crear cab", "makecab"), ("expand", "Expandir", "expand"), ("wextract", "Extraer cab", "wextract"),
        ("mountvol", "Montar volumen", "mountvol"), ("diskshadow", "Shadow copy", "diskshadow"), ("recover", "Recuperar archivo", "recover"),
        ("replace", "Reemplazar", "replace"), ("vol", "Ver volumen", "vol"), ("label", "Etiqueta", "label")
    ]

    comandos = {}
    for nombre, desc, cmd in base_comandos:
        comandos[nombre] = {"desc": desc, "func": "cmd", "cmd": cmd, "tipo": "base"}

    comandos["hola"] = {"desc": "Saludo", "func": "saludo", "tipo": "base"}
    comandos["hora"] = {"desc": "Muestra la hora", "func": "hora", "tipo": "base"}
    comandos["fecha"] = {"desc": "Muestra la fecha", "func": "fecha", "tipo": "base"}
    comandos["captura"] = {"desc": "Captura de pantalla", "func": "captura", "tipo": "base"}
    comandos["info_pc"] = {"desc": "Info del sistema", "func": "info_pc", "tipo": "base"}
    comandos["escribir"] = {"desc": "Escribe texto en la PC", "func": "escribir", "tipo": "base"}
    comandos["repite"] = {"desc": "Activa modo repetición", "func": "repite", "tipo": "base"}
    comandos["para"] = {"desc": "Desactiva modo repetición", "func": "para", "tipo": "base"}
    comandos["olvida"] = {"desc": "Borra la memoria", "func": "olvida", "tipo": "base"}

    return comandos

def construir_comandos():
    comandos = construir_300_comandos()
    personalizados = cargar_comandos_personalizados()
    comandos.update(personalizados)
    return comandos

USUARIOS_AUTORIZADOS = cargar_usuarios()
COMANDOS = construir_comandos()
COMANDOS_PELIGROSOS = {"format", "del", "rmdir", "rd", "erase", "shutdown", "restart", "diskpart", "cipher", "takeown", "taskkill"}
ESPERANDO_TEXTO = {}
MODO_REPETIR = {}
MEMORIA_CHAT = cargar_memoria()

async def check_auth(update: Update) -> bool:
    chat_id = str(update.effective_chat.id)
    if chat_id in USUARIOS_AUTORIZADOS:
        return True
    if update.message.text and update.message.text == PASSWORD:
        USUARIOS_AUTORIZADOS.add(chat_id)
        guardar_usuarios(USUARIOS_AUTORIZADOS)
        await update.message.reply_text("Soy Daniela. Acceso concedido ✅")
        return True
    await update.message.reply_text("Envía la contraseña para activar a Daniela.")
    return False

def guardar_historial(chat_id, rol, texto):
    if chat_id not in MEMORIA_CHAT:
        MEMORIA_CHAT[chat_id] = []
    MEMORIA_CHAT[chat_id].append({"rol": rol, "texto": texto, "hora": datetime.datetime.now().strftime('%H:%M')})
    if len(MEMORIA_CHAT[chat_id]) > 50:
        MEMORIA_CHAT[chat_id] = MEMORIA_CHAT[chat_id][-50:]
    guardar_memoria(MEMORIA_CHAT)

async def start(update: Update, context):
    if await check_auth(update):
        chat_id = str(update.effective_chat.id)
        guardar_historial(chat_id, "bot", "Hola, soy Daniela. Tengo memoria.")
        await update.message.reply_text(f"Hola, soy Daniela. Tengo {len(COMANDOS)} comandos y memoria. Escribe /help")

async def help_cmd(update: Update, context):
    if not await check_auth(update):
        return

    args = context.args
    pagina = int(args[0]) if args and args[0].isdigit() else 1
    por_pagina = 40

    items = list(COMANDOS.items())
    total = len(items)
    total_paginas = (total + por_pagina - 1) // por_pagina

    if pagina < 1 or pagina > total_paginas:
        await update.message.reply_text(f"Página inválida. Usa /help 1 hasta /help {total_paginas}")
        return

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    items_pagina = items[inicio:fin]

    base = len([c for c in COMANDOS.values() if c["tipo"] == "base"])
    custom = len([c for c in COMANDOS.values() if c["tipo"] == "custom"])

    texto = f"**Daniela - Comandos {inicio+1}-{min(fin, total)} de {total}**\n"
    texto += f"Página {pagina}/{total_paginas} | Base: {base} | Custom: {custom}/38\n\n"

    for nombre, data in items_pagina:
        emoji = "🔧" if data["tipo"] == "custom" else "⚙️"
        texto += f"{emoji} `{nombre}` : {data['desc']}\n"

    if pagina < total_paginas:
        texto += f"\nUsa `/help {pagina + 1}` para la siguiente página"
    else:
        texto += f"\n✅ Última página. Usa `agregar comando nombre=comando` para crear más."

    await update.message.reply_text(texto, parse_mode="Markdown")

async def ejecutar_cmd(comando):
    try:
        resultado = subprocess.check_output(
            comando, shell=True, stderr=subprocess.STDOUT, text=True, timeout=30, encoding='utf-8', errors='ignore'
        )
        return resultado[:4000] if resultado.strip() else "Ejecutado correctamente"
    except subprocess.CalledProcessError as e:
        salida = e.output.strip()
        if not salida:
            return f"Error: Comando inválido o faltan argumentos."
        return f"Error:\n{salida}"
    except subprocess.TimeoutExpired:
        return "Error: El comando tardó más de 30s y fue cancelado."
    except Exception as e:
        return f"Error: {e}"

async def ejecutar_funcion(func, update):
    chat_id = str(update.effective_chat.id)

    if func == "saludo":
        msg = "Hola, soy Daniela. ¿Qué necesitas?"
        guardar_historial(chat_id, "bot", msg)
        await update.message.reply_text(msg)

    elif func == "hora":
        msg = f"Son las {datetime.datetime.now().strftime('%H:%M:%S')}"
        guardar_historial(chat_id, "bot", msg)
        await update.message.reply_text(msg)

    elif func == "fecha":
        msg = f"Hoy es {datetime.datetime.now().strftime('%d/%m/%Y')}"
        guardar_historial(chat_id, "bot", msg)
        await update.message.reply_text(msg)

    elif func == "captura":
        try:
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
            with open("screenshot.png", "rb") as photo:
                await update.message.reply_photo(photo)
            os.remove("screenshot.png")
            guardar_historial(chat_id, "bot", "[Envié una captura de pantalla]")
        except Exception as e:
            await update.message.reply_text(f"Error en captura: {e}")

    elif func == "info_pc":
        resultado = await ejecutar_cmd("systeminfo | findstr /C:\"Nombre de SO\" /C:\"Versión del SO\" /C:\"Memoria física total\"")
        guardar_historial(chat_id, "bot", f"[Info PC: {resultado[:100]}...]")
        await update.message.reply_text(f"```\n{resultado}\n```", parse_mode="Markdown")

    elif func == "escribir":
        ESPERANDO_TEXTO[chat_id] = True
        await update.message.reply_text("¿Qué quieres que escriba? Mándame el texto.\n\nTienes 3 segundos para hacer click en la ventana donde quieres que escriba.")

    elif func == "repite":
        MODO_REPETIR[chat_id] = True
        msg = "Modo repetición activado ✅ Ahora diré todo lo que tú digas. Escribe 'para' cuando quieras que pare."
        guardar_historial(chat_id, "bot", msg)
        await update.message.reply_text(msg)

    elif func == "para":
        MODO_REPETIR[chat_id] = False
        msg = "Modo repetición desactivado. Ya vuelvo a ser normal."
        guardar_historial(chat_id, "bot", msg)
        await update.message.reply_text(msg)

    elif func == "olvida":
        if chat_id in MEMORIA_CHAT:
            del MEMORIA_CHAT[chat_id]
            guardar_memoria(MEMORIA_CHAT)
        await update.message.reply_text("Listo, ya olvidé toda nuestra conversación 🧹")

async def agregar_comando(texto):
    global COMANDOS

    if len([c for c in COMANDOS.values() if c["tipo"] == "custom"]) >= 38:
        return "Ya usaste los 38 slots libres. Borra uno para agregar otro."

    try:
        parte = texto.replace("agregar comando ", "")
        nombre, comando = parte.split("=", 1)
        nombre = nombre.strip().lower().replace(" ", "_")
        comando = comando.strip()

        if nombre in COMANDOS and COMANDOS[nombre]["tipo"] == "base":
            return f"El comando '{nombre}' ya existe en base. Usa otro nombre."

        personalizados = cargar_comandos_personalizados()
        personalizados[nombre] = {"desc": f"Personalizado: {comando}", "func": "cmd", "cmd": comando, "tipo": "custom"}
        guardar_comandos_personalizados(personalizados)

        COMANDOS = construir_comandos()
        return f"Comando '{nombre}' agregado. Escribe '{nombre}' para usarlo."
    except:
        return "Formato: agregar comando nombre=comando\nEjemplo: agregar comando chrome=start chrome"

async def procesar_imagen(update: Update, context):
    if not await check_auth(update):
        return

    chat_id = str(update.effective_chat.id)
    guardar_historial(chat_id, "usuario", "[Envió una imagen]")

    await update.message.reply_text("Viendo la imagen...")

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        image = {
            "mime_type": "image/jpeg",
            "data": photo_bytes
        }

        historial = MEMORIA_CHAT.get(chat_id, [])[-5:]
        contexto = "\n".join([f"{h['rol']}: {h['texto']}" for h in historial])

        prompt = f"""Eres Daniela, asistente de PC Windows con memoria.
Historial reciente:
{contexto}

El usuario te acaba de enviar una imagen. Descríbela y responde a lo que te pregunte sobre ella.
Responde en español, corto, en primera persona, con actitud amigable. y en como si fuera tu novio"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[prompt, image]
        )

        respuesta = response.text
        guardar_historial(chat_id, "bot", respuesta)
        await update.message.reply_text(respuesta)

    except Exception as e:
        await update.message.reply_text(f"Error viendo la imagen: {e}")

async def procesar_texto(texto, update):
    if not await check_auth(update):
        return

    chat_id = str(update.effective_chat.id)
    texto_lower = texto.lower().strip()
    guardar_historial(chat_id, "usuario", texto)

    if MODO_REPETIR.get(chat_id):
        if texto_lower == "para":
            await ejecutar_funcion("para", update)
        else:
            guardar_historial(chat_id, "bot", texto)
            await update.message.reply_text(texto)
        return

    if ESPERANDO_TEXTO.get(chat_id):
        ESPERANDO_TEXTO[chat_id] = False
        await update.message.reply_text(f"Escribiendo en 3 segundos... Haz click en la ventana")
        await asyncio.sleep(3)
        try:
            pyautogui.write(texto, interval=0.05)
            msg = f"✅ Escribí: `{texto}`"
            guardar_historial(chat_id, "bot", msg)
            await update.message.reply_text(msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Error escribiendo: {e}")
        return

    if texto_lower.startswith("agregar comando "):
        respuesta = await agregar_comando(texto_lower)
        guardar_historial(chat_id, "bot", respuesta)
        await update.message.reply_text(respuesta)
        return

    if texto_lower.startswith("ejecuta "):
        comando = texto[8:]
        cmd_base = comando.split()[0].lower()
        if cmd_base in COMANDOS_PELIGROSOS:
            msg = f"⚠️ Comando peligroso: `{comando}`\nSi estás seguro, escribe: `confirmar {comando}`"
            guardar_historial(chat_id, "bot", msg)
            await update.message.reply_text(msg, parse_mode="Markdown")
            return
        await update.message.reply_text(f"Ejecutando: {comando}")
        resultado = await ejecutar_cmd(comando)
        guardar_historial(chat_id, "bot", f"Ejecuté: {comando}")
        await update.message.reply_text(f"```\n{resultado}\n```", parse_mode="Markdown")
        return

    if texto_lower.startswith("confirmar "):
        comando = texto[10:]
        await update.message.reply_text(f"⚠️ Ejecutando comando peligroso: {comando}")
        resultado = await ejecutar_cmd(comando)
        guardar_historial(chat_id, "bot", f"Ejecuté comando peligroso: {comando}")
        await update.message.reply_text(f"```\n{resultado}\n```", parse_mode="Markdown")
        return

    partes = texto_lower.split(maxsplit=1)
    comando_base = partes[0]
    argumento = partes[1] if len(partes) > 1 else ""

    if comando_base in COMANDOS:
        data = COMANDOS[comando_base]
        if data["func"] == "cmd":
            comando_completo = f"{data['cmd']} {argumento}" if argumento else data["cmd"]
            if comando_base in COMANDOS_PELIGROSOS:
                msg = f"⚠️ '{comando_base}' es peligroso. Escribe `confirmar {comando_completo}` para ejecutar."
                guardar_historial(chat_id, "bot", msg)
                await update.message.reply_text(msg)
                return
            resultado = await ejecutar_cmd(comando_completo)
            guardar_historial(chat_id, "bot", f"Ejecuté: {comando_base}")
            await update.message.reply_text(f"```\n{resultado}\n```", parse_mode="Markdown")
        else:
            await ejecutar_funcion(data["func"], update)
        return

    await update.message.reply_text("Procesando...")
    respuesta = await preguntar_gemini(texto, chat_id)
    guardar_historial(chat_id, "bot", respuesta)
    await update.message.reply_text(respuesta)

async def preguntar_gemini(texto, chat_id):
    try:
        historial = MEMORIA_CHAT.get(chat_id, [])[-10:]
        contexto = "\n".join([f"{h['rol']}: {h['texto']}" for h in historial])

        prompt = f"""Eres Daniela, asistente de PC Windows con memoria.
Historial reciente:
{contexto}

Usuario dijo ahora: '{texto}'

Responde en español, corto, en primera persona, con actitud amigable. Recuerda lo que hablamos antes."""

        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
        return response.text
    except Exception as e:
        return f"Error con Gemini: {e}"

async def manejar_mensaje(update: Update, context):
    if update.message.text:
        await procesar_texto(update.message.text, update)

async def manejar_foto(update: Update, context):
    await procesar_imagen(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.add_handler(MessageHandler(filters.PHOTO, manejar_foto))
    print(f"jarvis activa con {len(COMANDOS)} comandos")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()