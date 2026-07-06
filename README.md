<div align="center">
  <img src="https://raw.githubusercontent.com/PeraltaHD4K/risansym/main/web/public/globe.svg" alt="Risansym Logo" width="120" />
</div>

<h1 align="center">Risansym</h1>
<p align="center">
  <em>A powerful, Python-based discrete event simulator for distributed systems with a gorgeous React/Next.js visualizer.</em>
</p>

---

**Risansym** is an educational and research tool designed to simulate distributed algorithms (like Chandy-Lamport, Ping-Pong, and more) and visualize their execution traces in a browser.

## 📖 Documentación Oficial

Toda la documentación sobre cómo instalar la librería, escribir algoritmos, interactuar con la API y utilizar el visualizador web está disponible en:

👉 **[https://peraltahd4k.github.io/risansym/](https://peraltahd4k.github.io/risansym/)** 👈

---

## Estructura del Proyecto
Este repositorio se compone de dos partes fundamentales:
1. **`core/`**: El motor de simulación escrito en Python estricto (Pydantic, uv).
2. **`web/`**: La interfaz gráfica en React / Next.js para renderizar los `.json` generados.

## Instalación Rápida
Puedes instalar la librería usando pip:
```bash
pip install risansym
```

Para correr el visualizador de forma local:
```bash
cd web
npm install
npm run dev
```
