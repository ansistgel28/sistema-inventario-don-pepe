"""
SISTEMA DE INVENTARIOS FIFO Y LIFO - CONSOLA
Curso: Estructura de Datos
Proyecto: Sistema de inventarios aplicando los métodos FIFO y LIFO

Autor: adaptar nombres del grupo
Descripción:
    Sistema funcional por consola que usa JSON como base de datos.
    Permite gestionar productos, entradas, salidas, movimientos FIFO, movimientos LIFO,
    comparación de resultados, historial y exportación CSV.

Estructuras usadas:
    - Listas: almacenan productos, entradas, salidas, historial y movimientos.
    - Diccionarios: permiten acceder a los datos por clave y agrupar lotes.
    - Búsqueda lineal: se usa para ubicar productos por código.
    - Ordenamiento: se usa para procesar movimientos por fecha e ID.
    - FIFO: Cola de lotes. Se consume el primer lote ingresado.
    - LIFO: Pila de lotes. Se consume el último lote ingresado.

Relación con el sílabo:
    - Semana 6: Pilas y colas.
    - Semana 7: Búsqueda y ordenamiento.
    - Semana 14: Proyecto integrador - Sistema de inventarios FIFO y LIFO.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


# ============================================================
# RUTAS
# ============================================================

CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATA = os.path.join(CARPETA_PROYECTO, "data")
BASE_JSON = os.path.join(CARPETA_DATA, "base_datos_inventario.json")
DB_JSON = os.path.join(CARPETA_DATA, "sistema_inventario.json")
CARPETA_REPORTES = os.path.join(CARPETA_PROYECTO, "reportes")


# ============================================================
# MODELOS DE DATOS
# ============================================================

# Aca se uso el concepto de registro / dato compuesto del silabo:
# cada dataclass representa una entidad con varios campos.
@dataclass
class Producto:
    codigo: str
    nombre: str
    categoria: str
    unidad: str
    stock_inicial: float = 0.0
    precio_referencia: float = 0.0


@dataclass
class Entrada:
    id: str
    fecha: str
    codigo_producto: str
    cantidad: float
    precio_unitario: float
    lote: str
    observacion: str = "Compra"


@dataclass
class Salida:
    id: str
    fecha: str
    codigo_producto: str
    cantidad: float
    estado: str = "Atendido"
    observacion: str = "Venta"


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_pantalla() -> None:
    os.system("clear" if os.name == "posix" else "cls")


def pausa() -> None:
    input("\nPresiona ENTER para continuar...")


def crear_carpetas() -> None:
    os.makedirs(CARPETA_DATA, exist_ok=True)
    os.makedirs(CARPETA_REPORTES, exist_ok=True)


def ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validar_fecha(fecha: str) -> bool:
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def leer_texto(mensaje: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor or not obligatorio:
            return valor
        print("El campo no puede estar vacío.")


def leer_fecha(mensaje: str) -> str:
    while True:
        fecha = input(mensaje).strip()
        if validar_fecha(fecha):
            return fecha
        print("Fecha inválida. Usa el formato YYYY-MM-DD. Ejemplo: 2026-07-04")


def leer_float(mensaje: str, minimo: float = 0.0) -> float:
    while True:
        try:
            valor = float(input(mensaje).replace(",", "."))
            if valor >= minimo:
                return valor
            print(f"El valor debe ser mayor o igual que {minimo}.")
        except ValueError:
            print("Ingresa un número válido.")


def leer_opcion(mensaje: str, opciones: List[str]) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor in opciones:
            return valor
        print(f"Opción inválida. Opciones permitidas: {', '.join(opciones)}")


def dinero(valor: float) -> str:
    return f"S/ {valor:,.2f}"


def cantidad(valor: float) -> str:
    if abs(valor - int(valor)) < 0.000001:
        return str(int(valor))
    return f"{valor:.2f}"


def recortar(texto: Any, ancho: int) -> str:
    texto = str(texto)
    if len(texto) <= ancho:
        return texto
    return texto[: ancho - 3] + "..."


def imprimir_tabla(filas: List[Dict[str, Any]], columnas: List[str], limite: Optional[int] = None) -> None:
    if not filas:
        print("No hay registros para mostrar.")
        return

    datos = filas[:limite] if limite else filas
    ancho_maximo = 22
    anchos = {}

    for col in columnas:
        anchos[col] = min(max(len(col), *(len(recortar(f.get(col, ""), ancho_maximo)) for f in datos)), ancho_maximo)

    linea = "+" + "+".join("-" * (anchos[col] + 2) for col in columnas) + "+"
    encabezado = "|" + "|".join(f" {col:<{anchos[col]}} " for col in columnas) + "|"

    print(linea)
    print(encabezado)
    print(linea)
    for fila in datos:
        print("|" + "|".join(f" {recortar(fila.get(col, ''), anchos[col]):<{anchos[col]}} " for col in columnas) + "|")
    print(linea)

    if limite and len(filas) > limite:
        print(f"Mostrando {limite} de {len(filas)} registros.")


# ============================================================
# CLASE PRINCIPAL DEL SISTEMA
# ============================================================

class SistemaInventario:
    def __init__(self) -> None:
        crear_carpetas()
        self.data = self.cargar_o_crear_base()

    # --------------------------------------------------------
    # BASE DE DATOS JSON
    # --------------------------------------------------------

    def estructura_vacia(self) -> Dict[str, Any]:
        # Aca se uso el concepto de diccionario y listas:
        # el diccionario guarda claves y cada clave contiene una lista de datos.
        return {
            "productos": [],
            "entradas": [],
            "salidas": [],
            "historial": [],
            "metadatos": {
                "nombre_sistema": "Sistema de Inventarios FIFO y LIFO",
                "creado": ahora(),
                "descripcion": "Base de datos JSON para proyecto de estructura de datos"
            }
        }

    def cargar_o_crear_base(self) -> Dict[str, Any]:
        if os.path.exists(DB_JSON):
            with open(DB_JSON, "r", encoding="utf-8") as archivo:
                return json.load(archivo)

        data = self.estructura_vacia()

        # Si existe el JSON principal convertido desde Excel, cargamos productos.
        if os.path.exists(BASE_JSON):
            try:
                with open(BASE_JSON, "r", encoding="utf-8") as archivo:
                    base = json.load(archivo)

                productos = []
                for p in base.get("productos", []):
                    productos.append(asdict(Producto(
                        codigo=str(p.get("ID_Producto", "")).strip(),
                        nombre=str(p.get("Producto", "")).strip(),
                        categoria=str(p.get("Categoría", "Sin categoría")).strip(),
                        unidad=str(p.get("Unidad", "unidad")).strip(),
                        stock_inicial=0.0,
                        precio_referencia=float(p.get("Precio_Base_Soles", 0) or 0)
                    )))
                data["productos"] = productos
                data["historial"].append({
                    "fecha_hora": ahora(),
                    "accion": "Carga inicial",
                    "detalle": f"Se importaron {len(productos)} productos desde base_datos_inventario.json"
                })
            except Exception as error:
                print(f"No se pudo leer el JSON principal: {error}")

        self.guardar(data)
        return data

    def guardar(self, data: Optional[Dict[str, Any]] = None) -> None:
        if data is None:
            data = self.data
        with open(DB_JSON, "w", encoding="utf-8") as archivo:
            json.dump(data, archivo, ensure_ascii=False, indent=4)

    def backup(self) -> None:
        if os.path.exists(DB_JSON):
            nombre = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(DB_JSON, os.path.join(CARPETA_DATA, nombre))
            print(f"Backup creado: data/{nombre}")
        else:
            print("No existe base de datos para respaldar.")

    def registrar_historial(self, accion: str, detalle: str) -> None:
        self.data["historial"].append({
            "fecha_hora": ahora(),
            "accion": accion,
            "detalle": detalle
        })
        self.guardar()

    # --------------------------------------------------------
    # BÚSQUEDAS Y CÓDIGOS AUTOMÁTICOS
    # --------------------------------------------------------

    def buscar_producto(self, codigo: str) -> Optional[Dict[str, Any]]:
        codigo = codigo.strip().upper()
        # Aca se uso busqueda lineal:
        # se recorre la lista producto por producto hasta encontrar el codigo.
        for producto in self.data["productos"]:
            if producto["codigo"].upper() == codigo:
                return producto
        return None

    def nombre_producto(self, codigo: str) -> str:
        producto = self.buscar_producto(codigo)
        return producto["nombre"] if producto else "Producto no encontrado"

    def siguiente_id(self, tipo: str) -> str:
        if tipo == "entrada":
            return f"E{len(self.data['entradas']) + 1:04d}"
        if tipo == "salida":
            return f"S{len(self.data['salidas']) + 1:04d}"
        if tipo == "producto":
            return f"P{len(self.data['productos']) + 1:03d}"
        return "ID000"

    def siguiente_lote(self, codigo_producto: str) -> str:
        # Aca se uso recorrido de lista con acumulacion:
        # cuenta cuantos lotes existen para generar el siguiente lote.
        total = sum(1 for e in self.data["entradas"] if e["codigo_producto"] == codigo_producto)
        return f"L-{codigo_producto}-{total + 1:03d}"

    # --------------------------------------------------------
    # PRODUCTOS - CRUD
    # --------------------------------------------------------

    def listar_productos(self) -> None:
        filas = []
        stock = self.calcular_stock_general()
        for p in self.data["productos"]:
            filas.append({
                "Código": p["codigo"],
                "Nombre": p["nombre"],
                "Categoría": p["categoria"],
                "Unidad": p["unidad"],
                "Stock": cantidad(stock.get(p["codigo"], 0)),
                "Precio ref.": dinero(float(p.get("precio_referencia", 0)))
            })
        imprimir_tabla(filas, ["Código", "Nombre", "Categoría", "Unidad", "Stock", "Precio ref."], limite=50)

    def registrar_producto(self) -> None:
        print("\nREGISTRAR PRODUCTO")
        print("Deja el código vacío para generarlo automáticamente.")
        codigo = leer_texto("Código: ", obligatorio=False).upper()
        if not codigo:
            codigo = self.siguiente_id("producto")

        if self.buscar_producto(codigo):
            print("Ya existe un producto con ese código.")
            return

        nombre = leer_texto("Nombre: ")
        categoria = leer_texto("Categoría: ")
        unidad = leer_texto("Unidad de medida: ")
        stock_inicial = leer_float("Stock inicial disponible: ", minimo=0)
        precio = leer_float("Precio referencial: S/ ", minimo=0)

        producto = Producto(codigo, nombre, categoria, unidad, stock_inicial, precio)
        # Aca se uso insercion en lista:
        # append agrega el producto al final de la lista.
        self.data["productos"].append(asdict(producto))
        self.registrar_historial("Producto registrado", f"{codigo} - {nombre} | Stock inicial: {cantidad(stock_inicial)}")
        print("Producto registrado correctamente.")

    def editar_producto(self) -> None:
        print("\nEDITAR PRODUCTO")
        codigo = leer_texto("Código del producto: ").upper()
        producto = self.buscar_producto(codigo)
        if not producto:
            print("Producto no encontrado.")
            return

        print("Presiona ENTER para mantener el valor actual.")
        nombre = leer_texto(f"Nombre [{producto['nombre']}]: ", obligatorio=False) or producto["nombre"]
        categoria = leer_texto(f"Categoría [{producto['categoria']}]: ", obligatorio=False) or producto["categoria"]
        unidad = leer_texto(f"Unidad [{producto['unidad']}]: ", obligatorio=False) or producto["unidad"]
        stock_txt = leer_texto(f"Stock inicial [{producto.get('stock_inicial', 0)}]: ", obligatorio=False)
        precio_txt = leer_texto(f"Precio referencial [{producto.get('precio_referencia', 0)}]: ", obligatorio=False)

        producto["nombre"] = nombre
        producto["categoria"] = categoria
        producto["unidad"] = unidad
        if stock_txt:
            try:
                stock = float(stock_txt.replace(",", "."))
                if stock >= 0:
                    producto["stock_inicial"] = stock
                else:
                    print("Stock inválido. Se mantuvo el stock inicial anterior.")
            except ValueError:
                print("Stock inválido. Se mantuvo el stock inicial anterior.")
        if precio_txt:
            try:
                producto["precio_referencia"] = float(precio_txt.replace(",", "."))
            except ValueError:
                print("Precio inválido. Se mantuvo el precio anterior.")

        self.registrar_historial("Producto editado", f"{codigo} - {nombre}")
        print("Producto actualizado correctamente.")

    def eliminar_producto(self) -> None:
        print("\nELIMINAR PRODUCTO")
        codigo = leer_texto("Código del producto: ").upper()
        producto = self.buscar_producto(codigo)
        if not producto:
            print("Producto no encontrado.")
            return

        tiene_entradas = any(e["codigo_producto"] == codigo for e in self.data["entradas"])
        tiene_salidas = any(s["codigo_producto"] == codigo for s in self.data["salidas"])

        if tiene_entradas or tiene_salidas:
            print("No se puede eliminar porque el producto tiene movimientos registrados.")
            return

        confirmar = leer_opcion(f"¿Eliminar {producto['nombre']}? 1=Sí, 2=No: ", ["1", "2"])
        if confirmar == "1":
            # Aca se uso eliminacion en lista:
            # se reconstruye la lista quitando el producto seleccionado.
            self.data["productos"] = [p for p in self.data["productos"] if p["codigo"] != codigo]
            self.registrar_historial("Producto eliminado", f"{codigo} - {producto['nombre']}")
            print("Producto eliminado.")
        else:
            print("Operación cancelada.")

    # --------------------------------------------------------
    # ENTRADAS
    # --------------------------------------------------------

    def listar_entradas(self) -> None:
        filas = []
        # Aca se uso ordenamiento:
        # sorted ordena las entradas por fecha y luego por ID.
        for e in sorted(self.data["entradas"], key=lambda x: (x["fecha"], x["id"])):
            filas.append({
                "ID": e["id"],
                "Fecha": e["fecha"],
                "Producto": self.nombre_producto(e["codigo_producto"]),
                "Código": e["codigo_producto"],
                "Cantidad": cantidad(float(e["cantidad"])),
                "P. Unit.": dinero(float(e["precio_unitario"])),
                "Total": dinero(float(e["cantidad"]) * float(e["precio_unitario"])),
                "Lote": e["lote"]
            })
        imprimir_tabla(filas, ["ID", "Fecha", "Código", "Producto", "Cantidad", "P. Unit.", "Total", "Lote"], limite=100)

    def registrar_entrada(self) -> None:
        print("\nREGISTRAR ENTRADA / COMPRA")
        codigo = leer_texto("Código del producto: ").upper()
        producto = self.buscar_producto(codigo)
        if not producto:
            print("Producto no encontrado. Primero registra el producto.")
            return

        fecha = leer_fecha("Fecha de compra [YYYY-MM-DD]: ")
        cantidad_ = leer_float("Cantidad comprada: ", minimo=0.0001)
        precio = leer_float("Precio unitario de compra: S/ ", minimo=0.0001)
        lote = self.siguiente_lote(codigo)

        entrada = Entrada(
            id=self.siguiente_id("entrada"),
            fecha=fecha,
            codigo_producto=codigo,
            cantidad=cantidad_,
            precio_unitario=precio,
            lote=lote,
            observacion="Compra registrada manualmente"
        )
        # Aca se uso insercion en lista:
        # cada entrada se agrega como lote para luego aplicar FIFO o LIFO.
        self.data["entradas"].append(asdict(entrada))
        self.registrar_historial("Entrada registrada", f"{entrada.id} | {codigo} | {cantidad(cantidad_)} unidades | {dinero(precio)}")
        print(f"Entrada registrada correctamente. Lote generado: {lote}")

    # --------------------------------------------------------
    # SALIDAS
    # --------------------------------------------------------

    def listar_salidas(self) -> None:
        filas = []
        # Aca se uso ordenamiento:
        # sorted muestra las salidas en orden cronologico.
        for s in sorted(self.data["salidas"], key=lambda x: (x["fecha"], x["id"])):
            filas.append({
                "ID": s["id"],
                "Fecha": s["fecha"],
                "Producto": self.nombre_producto(s["codigo_producto"]),
                "Código": s["codigo_producto"],
                "Cantidad": cantidad(float(s["cantidad"])),
                "Estado": s.get("estado", "Atendido"),
                "Obs.": s.get("observacion", "Venta")
            })
        imprimir_tabla(filas, ["ID", "Fecha", "Código", "Producto", "Cantidad", "Estado", "Obs."], limite=100)

    def registrar_salida(self) -> None:
        print("\nREGISTRAR SALIDA / VENTA")
        codigo = leer_texto("Código del producto: ").upper()
        producto = self.buscar_producto(codigo)
        if not producto:
            print("Producto no encontrado.")
            return

        stock = self.calcular_stock_general().get(codigo, 0)
        print(f"Stock disponible aproximado: {cantidad(stock)} {producto['unidad']}")

        fecha = leer_fecha("Fecha de salida [YYYY-MM-DD]: ")
        cantidad_salida = leer_float("Cantidad vendida/salida: ", minimo=0.0001)

        if cantidad_salida > stock:
            print("No hay stock suficiente para registrar la salida.")
            print("Primero registra una entrada de inventario.")
            return

        salida = Salida(
            id=self.siguiente_id("salida"),
            fecha=fecha,
            codigo_producto=codigo,
            cantidad=cantidad_salida,
            estado="Atendido",
            observacion="Salida registrada manualmente"
        )
        # Aca se uso insercion en lista:
        # la salida se agrega al historial de movimientos de venta.
        self.data["salidas"].append(asdict(salida))
        self.registrar_historial("Salida registrada", f"{salida.id} | {codigo} | {cantidad(cantidad_salida)} unidades")
        print("Salida registrada correctamente.")

    # --------------------------------------------------------
    # CÁLCULO DE STOCK SIMPLE
    # --------------------------------------------------------

    def calcular_stock_general(self) -> Dict[str, float]:
        # Aca se uso diccionario de acumulacion:
        # la clave es el codigo del producto y el valor es su stock.
        stock = {p["codigo"]: float(p.get("stock_inicial", 0)) for p in self.data["productos"]}

        # Aca se uso recorrido de lista:
        # suma todas las entradas al stock.
        for e in self.data["entradas"]:
            codigo = e["codigo_producto"]
            stock[codigo] = stock.get(codigo, 0) + float(e["cantidad"])

        # Aca se uso recorrido de lista:
        # resta las salidas atendidas o entregadas.
        for s in self.data["salidas"]:
            if s.get("estado", "Atendido") in ["Atendido", "Entregado"]:
                codigo = s["codigo_producto"]
                stock[codigo] = stock.get(codigo, 0) - float(s["cantidad"])

        return stock

    # --------------------------------------------------------
    # ALGORITMOS FIFO Y LIFO
    # --------------------------------------------------------

    def generar_movimientos_ordenados(self) -> List[Dict[str, Any]]:
        # Aca se uso lista:
        # se unen entradas y salidas en una sola lista de movimientos.
        movimientos = []

        for e in self.data["entradas"]:
            movimientos.append({
                "tipo": "entrada",
                "orden_tipo": 1,
                "fecha": e["fecha"],
                "id": e["id"],
                "codigo_producto": e["codigo_producto"],
                "cantidad": float(e["cantidad"]),
                "precio_unitario": float(e["precio_unitario"]),
                "lote": e["lote"],
                "observacion": e.get("observacion", "Compra")
            })

        for s in self.data["salidas"]:
            if s.get("estado", "Atendido") in ["Atendido", "Entregado"]:
                movimientos.append({
                    "tipo": "salida",
                    "orden_tipo": 2,
                    "fecha": s["fecha"],
                    "id": s["id"],
                    "codigo_producto": s["codigo_producto"],
                    "cantidad": float(s["cantidad"]),
                    "estado": s.get("estado", "Atendido"),
                    "observacion": s.get("observacion", "Venta")
                })

        # Aca se uso ordenamiento:
        # se ordena por fecha, tipo de movimiento e ID.
        return sorted(movimientos, key=lambda x: (x["fecha"], x["orden_tipo"], x["id"]))

    def calcular_movimientos_inventario(self, metodo: str) -> Dict[str, Any]:
        """
        metodo = "FIFO" o "LIFO"

        FIFO: usa una cola de lotes.
              Sale primero el lote que ingresó primero.

        LIFO: usa una pila de lotes.
              Sale primero el lote que ingresó último.

        En el sílabo, esto corresponde a pilas y colas:
        - Cola FIFO: enqueue al agregar lote y dequeue al consumir el primero.
        - Pila LIFO: push al agregar lote y pop al consumir el último.
        """
        metodo = metodo.upper()
        if metodo not in ["FIFO", "LIFO"]:
            raise ValueError("Método inválido. Usa FIFO o LIFO.")

        # Aca se uso diccionario de listas:
        # cada producto tiene su propia lista de lotes.
        # Esa lista se comporta como cola FIFO o pila LIFO segun el metodo.
        lotes_por_producto: Dict[str, List[Dict[str, Any]]] = {}

        # Aca se uso lista:
        # movimientos_reporte guarda cada operacion como una fila del reporte.
        movimientos_reporte: List[Dict[str, Any]] = []
        costo_ventas_total = 0.0
        faltantes_total = 0.0

        def saldo_producto(codigo: str) -> Tuple[float, float]:
            # Aca se uso recorrido y acumulacion:
            # suma cantidades y valores de los lotes restantes.
            lotes = lotes_por_producto.get(codigo, [])
            cant = sum(float(l["cantidad_restante"]) for l in lotes)
            val = sum(float(l["cantidad_restante"]) * float(l["precio_unitario"]) for l in lotes)
            return cant, val

        movimientos = self.generar_movimientos_ordenados()

        for p in self.data["productos"]:
            stock_inicial = float(p.get("stock_inicial", 0) or 0)
            if stock_inicial <= 0:
                continue

            codigo = p["codigo"]
            precio = float(p.get("precio_referencia", 0) or 0)
            lote_inicial = f"STOCK-INICIAL-{codigo}"
            # Aca se uso lista de lotes:
            # se inicia la lista del producto con su stock inicial.
            lotes_por_producto[codigo] = [{
                "lote": lote_inicial,
                "fecha": "INICIAL",
                "id_entrada": "STOCK-INICIAL",
                "cantidad_inicial": stock_inicial,
                "cantidad_restante": stock_inicial,
                "precio_unitario": precio
            }]

            movimientos_reporte.append({
                "Fecha": "INICIAL",
                "Movimiento": "STOCK-INICIAL",
                "Tipo": "STOCK INICIAL",
                "Código": codigo,
                "Producto": p["nombre"],
                "Lote usado": lote_inicial,
                "Entrada cant.": stock_inicial,
                "Entrada P.U.": precio,
                "Entrada total": stock_inicial * precio,
                "Salida cant.": 0,
                "Salida P.U.": 0,
                "Costo venta": 0,
                "Saldo cant.": stock_inicial,
                "Saldo valor": stock_inicial * precio,
                "Detalle": "Stock disponible al registrar el producto"
            })

        for mov in movimientos:
            codigo = mov["codigo_producto"]
            producto = self.nombre_producto(codigo)
            lotes_por_producto.setdefault(codigo, [])

            if mov["tipo"] == "entrada":
                lote_nuevo = {
                    "lote": mov["lote"],
                    "fecha": mov["fecha"],
                    "id_entrada": mov["id"],
                    "cantidad_inicial": mov["cantidad"],
                    "cantidad_restante": mov["cantidad"],
                    "precio_unitario": mov["precio_unitario"]
                }
                # Aca se uso cola FIFO y pila LIFO:
                # append agrega el lote al final. En FIFO es enqueue y en LIFO es push.
                lotes_por_producto[codigo].append(lote_nuevo)

                saldo_cant, saldo_valor = saldo_producto(codigo)
                movimientos_reporte.append({
                    "Fecha": mov["fecha"],
                    "Movimiento": mov["id"],
                    "Tipo": "ENTRADA",
                    "Código": codigo,
                    "Producto": producto,
                    "Lote usado": mov["lote"],
                    "Entrada cant.": mov["cantidad"],
                    "Entrada P.U.": mov["precio_unitario"],
                    "Entrada total": mov["cantidad"] * mov["precio_unitario"],
                    "Salida cant.": 0,
                    "Salida P.U.": 0,
                    "Costo venta": 0,
                    "Saldo cant.": saldo_cant,
                    "Saldo valor": saldo_valor,
                    "Detalle": "Ingreso de lote al inventario"
                })

            elif mov["tipo"] == "salida":
                cantidad_por_vender = mov["cantidad"]
                costo_salida = 0.0

                while cantidad_por_vender > 0.000001 and lotes_por_producto[codigo]:
                    # Aca se uso FIFO y LIFO:
                    # FIFO usa indice 0 porque sale primero el lote mas antiguo.
                    # LIFO usa indice -1 porque sale primero el lote mas reciente.
                    indice = 0 if metodo == "FIFO" else -1
                    lote = lotes_por_producto[codigo][indice]

                    disponible = float(lote["cantidad_restante"])
                    usado = min(cantidad_por_vender, disponible)
                    precio = float(lote["precio_unitario"])
                    costo = usado * precio

                    lote["cantidad_restante"] = disponible - usado
                    cantidad_por_vender -= usado
                    costo_salida += costo
                    costo_ventas_total += costo

                    if lote["cantidad_restante"] <= 0.000001:
                        # Aca se uso eliminacion en cola/pila:
                        # pop elimina el lote agotado del frente FIFO o del tope LIFO.
                        lotes_por_producto[codigo].pop(indice)

                    saldo_cant, saldo_valor = saldo_producto(codigo)
                    movimientos_reporte.append({
                        "Fecha": mov["fecha"],
                        "Movimiento": mov["id"],
                        "Tipo": "SALIDA",
                        "Código": codigo,
                        "Producto": producto,
                        "Lote usado": lote["lote"],
                        "Entrada cant.": 0,
                        "Entrada P.U.": 0,
                        "Entrada total": 0,
                        "Salida cant.": usado,
                        "Salida P.U.": precio,
                        "Costo venta": costo,
                        "Saldo cant.": saldo_cant,
                        "Saldo valor": saldo_valor,
                        "Detalle": f"Venta procesada con método {metodo}"
                    })

                if cantidad_por_vender > 0.000001:
                    faltantes_total += cantidad_por_vender
                    saldo_cant, saldo_valor = saldo_producto(codigo)
                    movimientos_reporte.append({
                        "Fecha": mov["fecha"],
                        "Movimiento": mov["id"],
                        "Tipo": "SALIDA SIN STOCK",
                        "Código": codigo,
                        "Producto": producto,
                        "Lote usado": "SIN LOTE",
                        "Entrada cant.": 0,
                        "Entrada P.U.": 0,
                        "Entrada total": 0,
                        "Salida cant.": cantidad_por_vender,
                        "Salida P.U.": 0,
                        "Costo venta": 0,
                        "Saldo cant.": saldo_cant,
                        "Saldo valor": saldo_valor,
                        "Detalle": "No había stock suficiente para cubrir toda la salida"
                    })

        inventario_final = []
        valor_total_inventario = 0.0
        # Aca se uso recorrido de diccionario:
        # recorre los lotes restantes para calcular el inventario final.
        for codigo, lotes in lotes_por_producto.items():
            for lote in lotes:
                cant_rest = float(lote["cantidad_restante"])
                precio = float(lote["precio_unitario"])
                valor = cant_rest * precio
                valor_total_inventario += valor
                inventario_final.append({
                    "Código": codigo,
                    "Producto": self.nombre_producto(codigo),
                    "Lote": lote["lote"],
                    "Cantidad": cant_rest,
                    "Precio unitario": precio,
                    "Valor": valor,
                    "Fecha lote": lote["fecha"]
                })

        return {
            "metodo": metodo,
            "movimientos": movimientos_reporte,
            "inventario_final": inventario_final,
            "costo_ventas_total": costo_ventas_total,
            "valor_total_inventario": valor_total_inventario,
            "faltantes_total": faltantes_total
        }

    # --------------------------------------------------------
    # REPORTES
    # --------------------------------------------------------

    def dashboard(self) -> None:
        limpiar_pantalla()
        print("=" * 70)
        print("DASHBOARD GENERAL DEL SISTEMA")
        print("=" * 70)

        total_productos = len(self.data["productos"])
        total_entradas = len(self.data["entradas"])
        total_salidas = len(self.data["salidas"])
        stock = self.calcular_stock_general()
        productos_con_stock = sum(1 for v in stock.values() if v > 0)
        productos_sin_stock = sum(1 for p in self.data["productos"] if stock.get(p["codigo"], 0) <= 0)

        print(f"Productos registrados       : {total_productos}")
        print(f"Entradas registradas        : {total_entradas}")
        print(f"Salidas registradas         : {total_salidas}")
        print(f"Productos con stock         : {productos_con_stock}")
        print(f"Productos sin stock         : {productos_sin_stock}")

        if total_entradas > 0 or total_salidas > 0:
            fifo = self.calcular_movimientos_inventario("FIFO")
            lifo = self.calcular_movimientos_inventario("LIFO")
            print("-" * 70)
            print(f"Costo de ventas FIFO        : {dinero(fifo['costo_ventas_total'])}")
            print(f"Costo de ventas LIFO        : {dinero(lifo['costo_ventas_total'])}")
            print(f"Valor inventario FIFO       : {dinero(fifo['valor_total_inventario'])}")
            print(f"Valor inventario LIFO       : {dinero(lifo['valor_total_inventario'])}")
            print(f"Diferencia costo venta      : {dinero(abs(fifo['costo_ventas_total'] - lifo['costo_ventas_total']))}")
        else:
            print("-" * 70)
            print("Aún no hay movimientos de entrada o salida.")

        pausa()

    def mostrar_inventario_disponible(self) -> None:
        limpiar_pantalla()
        print("INVENTARIO DISPONIBLE")
        stock = self.calcular_stock_general()
        filas = []
        for p in self.data["productos"]:
            filas.append({
                "Código": p["codigo"],
                "Producto": p["nombre"],
                "Categoría": p["categoria"],
                "Unidad": p["unidad"],
                "Stock": cantidad(stock.get(p["codigo"], 0))
            })
        imprimir_tabla(filas, ["Código", "Producto", "Categoría", "Unidad", "Stock"], limite=100)
        pausa()

    def mostrar_movimientos_inventario(self, metodo: str) -> None:
        limpiar_pantalla()
        resultado = self.calcular_movimientos_inventario(metodo)
        print("=" * 90)
        print(f"MOVIMIENTOS DE INVENTARIO {metodo.upper()}")
        print("=" * 90)

        filas = []
        for r in resultado["movimientos"]:
            filas.append({
                "Fecha": r["Fecha"],
                "Mov.": r["Movimiento"],
                "Tipo": r["Tipo"],
                "Código": r["Código"],
                "Lote": r["Lote usado"],
                "Ent.": cantidad(r["Entrada cant."]),
                "Sal.": cantidad(r["Salida cant."]),
                "P.U.": dinero(r["Salida P.U."] if r["Salida P.U."] else r["Entrada P.U."]),
                "Costo": dinero(r["Costo venta"]),
                "Saldo": cantidad(r["Saldo cant."]),
                "Valor saldo": dinero(r["Saldo valor"])
            })

        imprimir_tabla(filas, ["Fecha", "Mov.", "Tipo", "Código", "Lote", "Ent.", "Sal.", "P.U.", "Costo", "Saldo", "Valor saldo"], limite=120)
        print(f"\nCosto total de ventas {metodo.upper()}: {dinero(resultado['costo_ventas_total'])}")
        print(f"Valor final del inventario {metodo.upper()}: {dinero(resultado['valor_total_inventario'])}")
        if resultado["faltantes_total"] > 0:
            print(f"Unidades sin stock suficiente: {cantidad(resultado['faltantes_total'])}")
        pausa()

    def comparar_fifo_lifo(self) -> None:
        limpiar_pantalla()
        fifo = self.calcular_movimientos_inventario("FIFO")
        lifo = self.calcular_movimientos_inventario("LIFO")

        filas = [
            {
                "Concepto": "Costo de ventas",
                "FIFO": dinero(fifo["costo_ventas_total"]),
                "LIFO": dinero(lifo["costo_ventas_total"]),
                "Diferencia": dinero(abs(fifo["costo_ventas_total"] - lifo["costo_ventas_total"]))
            },
            {
                "Concepto": "Valor inventario final",
                "FIFO": dinero(fifo["valor_total_inventario"]),
                "LIFO": dinero(lifo["valor_total_inventario"]),
                "Diferencia": dinero(abs(fifo["valor_total_inventario"] - lifo["valor_total_inventario"]))
            },
            {
                "Concepto": "Movimientos registrados",
                "FIFO": len(fifo["movimientos"]),
                "LIFO": len(lifo["movimientos"]),
                "Diferencia": abs(len(fifo["movimientos"]) - len(lifo["movimientos"]))
            }
        ]

        print("COMPARACIÓN FIFO VS LIFO")
        imprimir_tabla(filas, ["Concepto", "FIFO", "LIFO", "Diferencia"])
        print("\nInterpretación:")
        # Aca se uso comparacion de estructuras:
        # se comparan los resultados de una cola FIFO y una pila LIFO.
        print("- FIFO consume primero los lotes más antiguos. Funciona como una COLA.")
        print("- LIFO consume primero los lotes más recientes. Funciona como una PILA.")
        print("- Si los precios cambian entre compras, el costo de ventas y el inventario final también cambian.")
        pausa()

    def mostrar_historial(self) -> None:
        limpiar_pantalla()
        print("HISTORIAL DE MOVIMIENTOS DEL SISTEMA")
        filas = []
        for h in self.data["historial"]:
            filas.append({
                "Fecha y hora": h["fecha_hora"],
                "Acción": h["accion"],
                "Detalle": h["detalle"]
            })
        imprimir_tabla(filas, ["Fecha y hora", "Acción", "Detalle"], limite=100)
        pausa()

    # --------------------------------------------------------
    # DATOS DE PRUEBA Y CARGA DESDE JSON PRINCIPAL
    # --------------------------------------------------------

    def cargar_caso_prueba_obligatorio(self) -> None:
        """
        Caso usado para explicar claramente la diferencia:
        Entradas:
            10 unidades a S/ 3.00
            10 unidades a S/ 4.00
            10 unidades a S/ 5.00
        Salida:
            15 unidades
        FIFO = 10*3 + 5*4 = S/ 50
        LIFO = 10*5 + 5*4 = S/ 70
        """
        confirmar = leer_opcion("Esto limpiará la base actual y cargará el caso obligatorio. ¿Continuar? 1=Sí, 2=No: ", ["1", "2"])
        if confirmar != "1":
            print("Operación cancelada.")
            return

        self.backup()
        self.data = self.estructura_vacia()

        producto = Producto("P001", "Arroz extra", "Abarrotes", "kg", 0, 3.0)
        self.data["productos"].append(asdict(producto))

        entradas = [
            # Aca se uso lista de prueba:
            # el orden de los lotes demuestra la diferencia entre FIFO y LIFO.
            Entrada("E0001", "2026-07-01", "P001", 10, 3.0, "L-P001-001", "Caso de prueba"),
            Entrada("E0002", "2026-07-02", "P001", 10, 4.0, "L-P001-002", "Caso de prueba"),
            Entrada("E0003", "2026-07-03", "P001", 10, 5.0, "L-P001-003", "Caso de prueba"),
        ]
        salida = Salida("S0001", "2026-07-04", "P001", 15, "Atendido", "Caso de prueba")

        self.data["entradas"] = [asdict(e) for e in entradas]
        self.data["salidas"] = [asdict(salida)]
        self.data["historial"].append({
            "fecha_hora": ahora(),
            "accion": "Caso obligatorio cargado",
            "detalle": "Caso FIFO S/ 50.00 y LIFO S/ 70.00"
        })
        self.guardar()
        print("Caso de prueba cargado correctamente.")
        print("Resultado esperado: FIFO = S/ 50.00 | LIFO = S/ 70.00")

    def generar_entradas_prueba_desde_productos(self) -> None:
        if not self.data["productos"]:
            print("No hay productos registrados.")
            return

        confirmar = leer_opcion("Se crearán 3 lotes de compra por producto. ¿Continuar? 1=Sí, 2=No: ", ["1", "2"])
        if confirmar != "1":
            print("Operación cancelada.")
            return

        creadas = 0
        existentes = {(e["codigo_producto"], e["lote"]) for e in self.data["entradas"]}

        for p in self.data["productos"]:
            codigo = p["codigo"]
            precio_base = float(p.get("precio_referencia", 10) or 10)
            cantidades = [50, 60, 70]
            precios = [precio_base * 0.75, precio_base * 0.82, precio_base * 0.90]
            fechas = ["2026-01-01", "2026-02-01", "2026-03-01"]

            for i in range(3):
                lote = f"L-{codigo}-{i + 1:03d}"
                if (codigo, lote) in existentes:
                    continue
                entrada = Entrada(
                    id=self.siguiente_id("entrada"),
                    fecha=fechas[i],
                    codigo_producto=codigo,
                    cantidad=cantidades[i],
                    precio_unitario=round(precios[i], 2),
                    lote=lote,
                    observacion="Entrada de prueba generada automáticamente"
                )
                self.data["entradas"].append(asdict(entrada))
                creadas += 1

        self.registrar_historial("Entradas de prueba", f"Se generaron {creadas} lotes de compra")
        print(f"Entradas de prueba generadas: {creadas}")

    def importar_ventas_desde_json_principal(self) -> None:
        if not os.path.exists(BASE_JSON):
            print("No se encontró data/base_datos_inventario.json")
            return

        try:
            with open(BASE_JSON, "r", encoding="utf-8") as archivo:
                base = json.load(archivo)
        except Exception as error:
            print(f"No se pudo leer el JSON principal: {error}")
            return

        ventas = base.get("ventas_salidas", [])
        if not ventas:
            print("El JSON principal no contiene ventas_salidas.")
            return

        print(f"Ventas encontradas en JSON principal: {len(ventas)}")
        print("Solo se importarán ventas con estado Atendido o Entregado.")
        confirmar = leer_opcion("¿Importar ventas como salidas? 1=Sí, 2=No: ", ["1", "2"])
        if confirmar != "1":
            print("Operación cancelada.")
            return

        ids_existentes = {s["id"] for s in self.data["salidas"]}
        importadas = 0
        omitidas = 0

        for v in ventas:
            estado = str(v.get("Estado_Atencion", "")).strip()
            if estado not in ["Atendido", "Entregado"]:
                omitidas += 1
                continue

            id_venta = str(v.get("ID_Venta", self.siguiente_id("salida")))
            if id_venta in ids_existentes:
                omitidas += 1
                continue

            codigo = str(v.get("ID_Producto", "")).strip()
            if not self.buscar_producto(codigo):
                omitidas += 1
                continue

            try:
                cant = float(v.get("Cantidad", 0) or 0)
            except ValueError:
                cant = 0
            if cant <= 0:
                omitidas += 1
                continue

            salida = Salida(
                id=id_venta,
                fecha=str(v.get("Fecha", "2026-01-01"))[:10],
                codigo_producto=codigo,
                cantidad=cant,
                estado=estado,
                observacion="Venta importada desde Excel convertido a JSON"
            )
            # Aca se uso insercion en lista:
            # se agrega cada venta importada a la lista de salidas.
            self.data["salidas"].append(asdict(salida))
            ids_existentes.add(id_venta)
            importadas += 1

        self.registrar_historial("Ventas importadas", f"Importadas: {importadas} | Omitidas: {omitidas}")
        print(f"Ventas importadas como salidas: {importadas}")
        print(f"Registros omitidos: {omitidas}")

    # --------------------------------------------------------
    # EXPORTACIÓN
    # --------------------------------------------------------

    def exportar_csv(self, nombre: str, filas: List[Dict[str, Any]]) -> None:
        if not filas:
            print(f"No hay datos para exportar: {nombre}")
            return
        ruta = os.path.join(CARPETA_REPORTES, nombre)
        with open(ruta, "w", encoding="utf-8-sig", newline="") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=list(filas[0].keys()))
            writer.writeheader()
            writer.writerows(filas)
        print(f"Exportado: {ruta}")

    def exportar_reportes(self) -> None:
        fifo = self.calcular_movimientos_inventario("FIFO")
        lifo = self.calcular_movimientos_inventario("LIFO")
        self.exportar_csv("movimientos_fifo.csv", fifo["movimientos"])
        self.exportar_csv("movimientos_lifo.csv", lifo["movimientos"])
        self.exportar_csv("inventario_final_fifo.csv", fifo["inventario_final"])
        self.exportar_csv("inventario_final_lifo.csv", lifo["inventario_final"])
        self.exportar_csv("productos.csv", self.data["productos"])
        self.exportar_csv("entradas.csv", self.data["entradas"])
        self.exportar_csv("salidas.csv", self.data["salidas"])
        self.exportar_csv("historial.csv", self.data["historial"])
        print("Exportación finalizada.")


# ============================================================
# MENÚS
# ============================================================

def menu_productos(sistema: SistemaInventario) -> None:
    while True:
        limpiar_pantalla()
        print("=" * 60)
        print("MÓDULO DE PRODUCTOS")
        print("=" * 60)
        print("1. Listar productos")
        print("2. Registrar producto")
        print("3. Editar producto")
        print("4. Eliminar producto")
        print("0. Volver")
        op = input("Selecciona una opción: ").strip()

        if op == "1":
            limpiar_pantalla()
            sistema.listar_productos()
            pausa()
        elif op == "2":
            sistema.registrar_producto()
            pausa()
        elif op == "3":
            sistema.editar_producto()
            pausa()
        elif op == "4":
            sistema.eliminar_producto()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")
            pausa()


def menu_entradas(sistema: SistemaInventario) -> None:
    while True:
        limpiar_pantalla()
        print("=" * 60)
        print("MÓDULO DE ENTRADAS / COMPRAS")
        print("=" * 60)
        print("1. Listar entradas")
        print("2. Registrar entrada")
        print("3. Generar entradas de prueba")
        print("0. Volver")
        op = input("Selecciona una opción: ").strip()

        if op == "1":
            limpiar_pantalla()
            sistema.listar_entradas()
            pausa()
        elif op == "2":
            sistema.registrar_entrada()
            pausa()
        elif op == "3":
            sistema.generar_entradas_prueba_desde_productos()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")
            pausa()


def menu_salidas(sistema: SistemaInventario) -> None:
    while True:
        limpiar_pantalla()
        print("=" * 60)
        print("MÓDULO DE SALIDAS / VENTAS")
        print("=" * 60)
        print("1. Listar salidas")
        print("2. Registrar salida")
        print("3. Importar ventas desde JSON principal")
        print("0. Volver")
        op = input("Selecciona una opción: ").strip()

        if op == "1":
            limpiar_pantalla()
            sistema.listar_salidas()
            pausa()
        elif op == "2":
            sistema.registrar_salida()
            pausa()
        elif op == "3":
            sistema.importar_ventas_desde_json_principal()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")
            pausa()


def menu_reportes(sistema: SistemaInventario) -> None:
    while True:
        limpiar_pantalla()
        print("=" * 60)
        print("MÓDULO DE REPORTES")
        print("=" * 60)
        print("1. Inventario disponible")
        print("2. Movimientos FIFO")
        print("3. Movimientos LIFO")
        print("4. Comparación FIFO vs LIFO")
        print("5. Historial de movimientos")
        print("6. Exportar reportes CSV")
        print("0. Volver")
        op = input("Selecciona una opción: ").strip()

        if op == "1":
            sistema.mostrar_inventario_disponible()
        elif op == "2":
            sistema.mostrar_movimientos_inventario("FIFO")
        elif op == "3":
            sistema.mostrar_movimientos_inventario("LIFO")
        elif op == "4":
            sistema.comparar_fifo_lifo()
        elif op == "5":
            sistema.mostrar_historial()
        elif op == "6":
            sistema.exportar_reportes()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")
            pausa()


def menu_principal() -> None:
    sistema = SistemaInventario()

    while True:
        limpiar_pantalla()
        print("=" * 70)
        print("SISTEMA DE INVENTARIOS APLICANDO FIFO Y LIFO")
        print("Proyecto Integrador - Estructura de Datos")
        print("=" * 70)
        print("1. Dashboard general")
        print("2. Gestión de productos")
        print("3. Entradas / compras")
        print("4. Salidas / ventas")
        print("5. Reportes FIFO y LIFO")
        print("6. Cargar caso de prueba obligatorio")
        print("7. Crear backup de la base JSON")
        print("0. Salir")
        print("=" * 70)
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            sistema.dashboard()
        elif opcion == "2":
            menu_productos(sistema)
        elif opcion == "3":
            menu_entradas(sistema)
        elif opcion == "4":
            menu_salidas(sistema)
        elif opcion == "5":
            menu_reportes(sistema)
        elif opcion == "6":
            sistema.cargar_caso_prueba_obligatorio()
            pausa()
        elif opcion == "7":
            sistema.backup()
            pausa()
        elif opcion == "0":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida.")
            pausa()


if __name__ == "__main__":
    menu_principal()
    
