# Solución: Desconexión del Relé USB LCUS-1 con Carga Inductiva

Este documento explica por qué el relé USB se desconecta (error: "El puerto está cerrado") al activar cargas como timbres escolares y cómo solucionarlo.

## 1. El Problema
El sistema funciona perfectamente en las pruebas de software (sin carga), pero al conectar el timbre escolar, el script falla con el error:
> `ERROR al comunicarse con el puerto COM3 : Excepción al llamar a "Write" con los argumentos "3": "El puerto está cerrado."`

## 2. La Causa Técnica
Los timbres escolares son **cargas inductivas**. Al interrumpirse el paso de corriente (cuando el relé se abre), la bobina del timbre genera un pico de voltaje muy alto conocido como **Fuerza Contraelectromotriz (Back EMF)** o **Interferencia Electromagnética (EMI)**.

Debido a que el módulo LCUS-1 es económico y no posee aislamiento galvánico avanzado (optoacopladores), este ruido eléctrico viaja por el circuito y llega al chip **CH340** (el controlador USB), causando que este se bloquee o se reinicie, provocando que Windows pierda la conexión con el puerto COM por un instante.

---

## 3. Soluciones Recomendadas

### Opción A: Para Timbres de Corriente Alterna (220V AC / 110V AC)
Esta es la solución más común para escuelas. Se debe instalar un **Filtro RC (Snubber)**.

*   **Componentes:** Un capacitor de 0.1µF (400V) en serie con una resistencia de 100 Ohms. (Venden el bloque armado como "Snubber RC").
*   **Conexión:** Se conecta en **paralelo** con los contactos del relé (puenteando `COM` y `NO`) o directamente en los terminales del timbre.
*   **Función:** Absorbe el chispazo eléctrico y suprime el ruido.

### Opción B: Para Timbres de Corriente Continua (12V DC / 24V DC)
Si el timbre funciona con una fuente de 12V o similar, se usa un **Diodo Flyback**.

*   **Componentes:** Un diodo común (ej. **1N4007**).
*   **Conexión:** En **paralelo** con los terminales del timbre, en **polaridad inversa** (la franja blanca del diodo va hacia el positivo `+`).
*   **Función:** Proporciona un camino seguro para que el pico de voltaje se disipe sin volver al relé.

---

## 4. Mejores Prácticas de Cableado
Para minimizar las interferencias sin gastar dinero extra:

1.  **Separación Física:** No pases el cable USB de la laptop pegado a los cables de 220V que van al timbre. Mantén al menos 10-15 cm de separación.
2.  **Cable USB de Calidad:** Usa un cable USB corto y, de ser posible, que tenga un núcleo de **ferrita** (el cilindro de plástico cerca del conector).
3.  **Caja de Aislamiento:** Monta el relé en una caja plástica separada de la caja donde están las conexiones de potencia del timbre.

---

## 5. Resumen de Diagnóstico
| Síntoma | Estado | Causa |
| :--- | :--- | :--- |
| Click sin cables conectados | OK | Software y Driver correctos |
| Click con lámpara simple | OK | Carga resistiva (poco ruido) |
| Click con timbre escolar | **FALLA** | Ruido inductivo (EMI/Back-EMF) |
