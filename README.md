# La tiendita de Don Pepe - Sistema de inventario

Proyecto para el curso de Estructura de Datos.

## Objetivo

Diseñar e implementar un sistema básico de control de inventarios que permita registrar productos, compras, ventas y comparar los métodos FIFO y LIFO.

## Archivos

```text
sistema_inventario_consola_fifo_lifo/
├── main.py
├── README.md
├── interfaz_web/
│   ├── index.html
│   └── assets/
│       └── don-pepe.png
└── data/
    ├── base_datos_inventario.json
    └── sistema_inventario.json
```

Cuando ejecutes el sistema por consola se creará automáticamente:

```text
reportes/
```

## Ejecución por consola

```bash
cd sistema_inventario_consola_fifo_lifo
python3 main.py
```

No requiere instalar librerías externas.

## Interfaz web

Para probar la interfaz web con lectura del JSON del proyecto:

Abre:

```text
https://ansistgel28.github.io/sistema-inventario-don-pepe/interfaz_web/
```

## Menú principal

1. Inicio
2. Productos
3. Compras
4. Ventas
5. Reportes
6. Cargar caso de prueba obligatorio
7. Crear backup de la base JSON
0. Salir

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

## Relación con estructura de datos

- FIFO se implementa como una cola.
- LIFO se implementa como una pila.
- El sistema permite comparar costo de ventas e inventario final.
