# La tiendita de Don Pepe - Sistema de inventario FIFO y LIFO

Proyecto integrador del curso **Estructura de Datos**.

El sistema permite registrar productos, entradas/compras, salidas/ventas y reportes de inventario aplicando los métodos **FIFO** y **LIFO**.

## Objetivo

Implementar un sistema de inventario que use estructuras de datos vistas en el curso para comparar el costo de ventas y el valor final del inventario usando:

- **FIFO**: primero entra, primero sale. Funciona como una cola.
- **LIFO**: último entra, primero sale. Funciona como una pila.

## Estructura del proyecto

```text
sistema_inventario_consola_fifo_lifo/
├── main.py
├── README.md
├── data/
│   ├── base_datos_inventario.json
│   ├── sistema_inventario.json
│   ├── sistema_inventario_main2.json
│   └── sistema_inventario_main2_copy.json
├── interfaz_web/
│   ├── index.html
│   └── assets/
│       └── don-pepe.png
└── reportes/
```

## Ejecución por consola

Desde la carpeta del proyecto:

```bash
python3 main.py
```

También puede ejecutarse desde otra carpeta porque `main.py` usa la ruta real del archivo para leer `data/`:

```python
CARPETA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATA = os.path.join(CARPETA_PROYECTO, "data")
```

No requiere instalar librerías externas.

## Interfaz web

Desde la carpeta del proyecto:

```bash
python3 -m http.server 8020
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8020/interfaz_web/index.html
```

## Menú principal de consola

1. Dashboard general
2. Gestión de productos
3. Entradas / compras
4. Salidas / ventas
5. Reportes FIFO y LIFO
6. Cargar caso de prueba obligatorio
7. Crear backup de la base JSON
0. Salir

## Reportes

El sistema genera:

- Inventario disponible.
- Kardex FIFO.
- Kardex LIFO.
- Comparación FIFO vs LIFO.
- Historial de movimientos.
- Exportación CSV en la carpeta `reportes/`.

En la interfaz web, estos reportes se muestran como:

- Primeras compras (FIFO).
- Últimas compras (LIFO).
- Comparación de costos.

## Caso de prueba obligatorio

Entradas:

- 10 unidades a S/ 3.00
- 10 unidades a S/ 4.00
- 10 unidades a S/ 5.00

Salida:

- 15 unidades

Resultados esperados:

- FIFO = S/ 50.00
- LIFO = S/ 70.00

## Conceptos del sílabo usados

En el código se agregaron comentarios con el formato `# Aca se uso...` para identificar los conceptos aplicados:

- Registros o datos compuestos: `dataclass Producto`, `Entrada` y `Salida`.
- Listas: productos, entradas, salidas, historial, lotes y movimientos.
- Diccionarios: base JSON, stock por producto y lotes por producto.
- Búsqueda lineal: búsqueda de producto por código.
- Ordenamiento: movimientos ordenados por fecha, tipo e ID.
- Recorrido y acumulación: cálculo de stock, saldo y valor del inventario.
- Cola FIFO: consumo del primer lote ingresado.
- Pila LIFO: consumo del último lote ingresado.
- Inserción y eliminación en listas: uso de `append` y `pop`.

Relación con el sílabo:

- Semana 6: pilas y colas.
- Semana 7: búsqueda y ordenamiento.
- Semana 14: proyecto integrador con sistema de inventarios FIFO y LIFO.

## Archivos de datos

- `data/base_datos_inventario.json`: base principal convertida desde Excel.
- `data/sistema_inventario.json`: base usada por `main.py`.
- `data/sistema_inventario_main2.json`: base alternativa para pruebas.
- `data/sistema_inventario_main2_copy.json`: copia de respaldo.

## Verificación rápida

Para comprobar que el programa no tiene errores de sintaxis:

```bash
python3 -m py_compile main.py
```
