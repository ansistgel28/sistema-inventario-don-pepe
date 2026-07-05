# Sistema de Inventarios FIFO y LIFO - Consola

Proyecto para el curso de Estructura de Datos.

## Objetivo
Diseñar e implementar un sistema básico de control de inventarios que permita registrar productos, entradas, salidas y comparar los métodos FIFO y LIFO.

## Archivos

```text
sistema_inventario_consola_fifo_lifo/
├── main.py
├── README.md
└── data/
    └── base_datos_inventario.json
```

Cuando ejecutes el sistema se creará automáticamente:

```text
data/sistema_inventario.json
reportes/
```

## Ejecución

```bash
cd sistema_inventario_consola_fifo_lifo
python3 main.py
```

No requiere instalar librerías externas.

## Menú principal

1. Dashboard general
2. Gestión de productos
3. Entradas / compras
4. Salidas / ventas
5. Reportes FIFO y LIFO
6. Cargar caso de prueba obligatorio
7. Fundamento teórico y algoritmo
8. Crear backup de la base JSON
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
