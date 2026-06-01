# Principios de sistemas computacionales 2026-1
# CA1 - Toolkit Regex ↔ NFA ↔ DFA

Proyecto en Python para construir un NFA desde una regex con Thompson, convertirlo a DFA con subset construction y probar cadenas.
Realizado por Nicolas Carrillo R.

## Archivos del .zip
- `main.py`: menú principal. (a ejecutar)
- `funciones.py`: parser, Thompson, subset construction y simulación.
- `pruebas.txt`: documento con casos de prueba.
- `informeCA1.pdf`: informe del caso con su prueba

## Cómo correr
En la carpeta del proyecto, click derecho -> Powershell/Open in terminal. 
Digite el siguiente comando y el proyecto se ejecutara en su totalidad:
```bash
python main.py
```

## Qué hace
1. Recibe una regex.
2. Construye el NFA.
3. Construye el DFA.
4. Permite probar cadenas escritas por teclado.
5. Muestra la tabla de transiciones del NFA.
6. Muestra la tabla de transiciones del DFA.

## Epsilon
Tambien es posible escribir epsilon como `ϵ`, `EPS` o `eps`.
