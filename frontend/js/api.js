// Cliente de la API: la interfaz solo se comunica con la API (RNF-07).
const API = {
  get token() { return sessionStorage.getItem("token"); },
  get usuario() {
    try { return JSON.parse(sessionStorage.getItem("usuario") || "null"); } catch { return null; }
  },
  guardarSesion(token, usuario) {
    sessionStorage.setItem("token", token);
    sessionStorage.setItem("usuario", JSON.stringify(usuario));
  },
  cerrarSesion() {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");
    location.href = "login.html";
  },
  esAdmin() { return this.usuario?.rol === "ADMINISTRADOR"; },

  async pedir(ruta, opciones = {}) {
    const cab = { ...(opciones.headers || {}) };
    if (this.token) cab.Authorization = `Bearer ${this.token}`;
    if (opciones.json !== undefined) {
      cab["Content-Type"] = "application/json";
      opciones.body = JSON.stringify(opciones.json);
    }
    const r = await fetch(ruta, { ...opciones, headers: cab });
    if (r.status === 401 && !ruta.endsWith("/login")) {
      alert("La sesión expiró. Inicie sesión de nuevo.");
      this.cerrarSesion();
      throw new Error("Sesión expirada");
    }
    if (!r.ok) {
      let detalle = `Error ${r.status}`;
      try {
        const j = await r.json();
        detalle = Array.isArray(j.detail) ? j.detail.map(d => d.msg).join("; ") : (j.detail || detalle);
      } catch { /* respuesta sin JSON */ }
      throw new Error(detalle);
    }
    const tipo = r.headers.get("content-type") || "";
    if (tipo.includes("application/json")) return r.json();
    return r.blob();
  },
  get(ruta) { return this.pedir(ruta); },
  post(ruta, json) { return this.pedir(ruta, { method: "POST", json }); },
  put(ruta, json) { return this.pedir(ruta, { method: "PUT", json }); },
  del(ruta) { return this.pedir(ruta, { method: "DELETE" }); },
  subir(ruta, formData) { return this.pedir(ruta, { method: "POST", body: formData }); },
};

function esc(v) {
  return String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function mostrarMensaje(el, texto, tipo = "error") {
  el.textContent = texto;
  el.className = `mensaje ${tipo}`;
}
