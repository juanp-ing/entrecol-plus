// Reportes: formulario de parametros, render en pantalla (RF-13) y vista previa PDF (RF-14).
const PALETA = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16",
  "#f97316", "#6366f1", "#14b8a6", "#a855f7", "#eab308", "#64748b", "#0ea5e9", "#d946ef"];

const ORDEN = { nombre: "orden", etiqueta: "Orden de nombres", tipo: "select", opciones: [["asc", "Ascendente"], ["desc", "Descendente"]] };

const REPORTES = {
  nomina: { titulo: "Nómina", desc: "Empleados por dependencia y cargo", params: [ORDEN] },
  personal: { titulo: "Información personal", desc: "Ficha del empleado y novedades",
    params: [{ nombre: "codigo", etiqueta: "Empleado", tipo: "empleado" }] },
  "salud-pension": { titulo: "Salud y pensión", desc: "EPS y fondos por dependencia y cargo", params: [ORDEN] },
  novedades: { titulo: "Novedades", desc: "Incapacidades y vacaciones en un rango",
    params: [{ nombre: "desde", etiqueta: "Desde (MM/AAAA)", tipo: "mes", valor: "01/2022" },
      { nombre: "hasta", etiqueta: "Hasta (MM/AAAA)", tipo: "mes", valor: "12/2022" }, ORDEN] },
  entretenimiento: { titulo: "Entretenimiento", desc: "Películas y libros",
    params: [{ nombre: "anio_desde", etiqueta: "Año desde", tipo: "number", valor: 1990 },
      { nombre: "anio_hasta", etiqueta: "Año hasta", tipo: "number", valor: 2000 },
      { nombre: "n_top", etiqueta: "Top N libros", tipo: "number", valor: 10 },
      { nombre: "n_generos", etiqueta: "Películas con N géneros", tipo: "number", valor: 3 },
      { ...ORDEN, etiqueta: "Orden de títulos" }] },
  auditoria: { titulo: "Auditoría", desc: "Cambios de datos y eventos", admin: true,
    params: [{ nombre: "desde", etiqueta: "Desde", tipo: "date" }, { nombre: "hasta", etiqueta: "Hasta", tipo: "date" },
      { nombre: "usuario", etiqueta: "Usuario (opcional)", tipo: "text" }] },
};

let graficos = [];

async function campoParametro(p) {
  const id = `p-${p.nombre}`;
  if (p.tipo === "select") {
    return `<div><label for="${id}">${p.etiqueta}</label><select id="${id}" name="${p.nombre}">
      ${p.opciones.map(([v, t]) => `<option value="${v}">${t}</option>`).join("")}</select></div>`;
  }
  if (p.tipo === "empleado") {
    const r = await API.get("/api/crud/empleados?tam=500");
    return `<div><label for="${id}">${p.etiqueta}</label><select id="${id}" name="${p.nombre}" required>
      ${r.filas.map(f => `<option value="${f.id}">${esc(f.id)} · ${esc(f.etiqueta)}</option>`).join("")}</select></div>`;
  }
  const tipo = p.tipo === "mes" ? "text" : p.tipo;
  const patron = p.tipo === "mes" ? 'pattern="(0[1-9]|1[0-2])/\\d{4}" placeholder="MM/AAAA"' : "";
  return `<div><label for="${id}">${p.etiqueta}</label>
    <input id="${id}" name="${p.nombre}" type="${tipo}" value="${p.valor ?? ""}" ${patron}></div>`;
}

async function vistaReporte(contenedor, clave) {
  const def = REPORTES[clave];
  const campos = (await Promise.all(def.params.map(campoParametro))).join("");
  contenedor.innerHTML = `
    <section class="panel vidrio">
      <h2>Reporte de ${def.titulo.toLowerCase()}</h2>
      <form id="form-reporte" class="fila">${campos}
        <button class="btn">Generar</button>
        <button class="btn sec" type="button" id="ver-pdf">Vista previa PDF</button>
      </form>
      <div id="msg-reporte" class="mensaje"></div>
    </section>
    <div id="resultado"></div>`;
  const form = contenedor.querySelector("#form-reporte");
  const query = () => new URLSearchParams([...new FormData(form)].filter(([, v]) => v !== "")).toString();
  const msg = contenedor.querySelector("#msg-reporte");

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    msg.className = "mensaje";
    try {
      const rep = await API.get(`/api/reportes/${clave}?${query()}`);
      pintarReporte(contenedor.querySelector("#resultado"), rep);
    } catch (e) { mostrarMensaje(msg, e.message); }
  });
  contenedor.querySelector("#ver-pdf").addEventListener("click", async () => {
    try { await vistaPreviaPdf(`/api/reportes/${clave}/pdf?${query()}`, def.titulo); }
    catch (e) { mostrarMensaje(msg, e.message); }
  });
}

function pintarReporte(destino, rep) {
  graficos.forEach(g => g.destroy());
  graficos = [];
  destino.innerHTML = "";
  rep.secciones.forEach((s, i) => {
    const panel = document.createElement("section");
    panel.className = "panel vidrio";
    panel.style.animationDelay = `${i * 60}ms`;
    if (s.tipo === "kpi") {
      panel.className = "kpis";
      panel.style.marginBottom = "18px";
      panel.innerHTML = s.items.map(k => `<div class="kpi vidrio"><div class="v">${esc(k.valor)}</div><div class="e">${esc(k.etiqueta)}</div></div>`).join("");
    } else if (s.tipo === "tabla") {
      panel.innerHTML = `<h3>${esc(s.titulo)} <small style="color:var(--texto-suave)">(${s.filas.length})</small></h3>
        ${s.filas.length ? `<div class="tabla-envoltura" style="max-height:420px"><table>
          <thead><tr>${s.columnas.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead>
          <tbody>${s.filas.map(f => `<tr>${f.map(v => `<td>${esc(formatear(v))}</td>`).join("")}</tr>`).join("")}</tbody>
        </table></div>` : ""}
        ${s.nota ? `<div class="nota">${esc(s.nota)}</div>` : ""}`;
    } else if (s.tipo === "grafico") {
      panel.innerHTML = `<h3>${esc(s.titulo)}</h3><div class="grafico"><canvas></canvas></div>`;
      destino.appendChild(panel);
      graficos.push(crearGrafico(panel.querySelector("canvas"), s));
      return;
    }
    destino.appendChild(panel);
  });
}

function formatear(v) {
  if (typeof v === "number" && !Number.isInteger(v)) return v.toLocaleString("es-CO", { maximumFractionDigits: 2 });
  return v;
}

function crearGrafico(canvas, s) {
  const torta = s.grafico === "pie";
  Chart.defaults.color = "#cbd5e1";
  Chart.defaults.borderColor = "rgba(255,255,255,.08)";
  return new Chart(canvas, {
    type: torta ? "pie" : "bar",
    data: {
      labels: s.etiquetas,
      datasets: s.series.map((serie, i) => ({
        label: serie.nombre,
        data: serie.datos,
        backgroundColor: torta ? PALETA : PALETA[i % PALETA.length],
        borderRadius: torta ? 0 : 6,
        borderColor: torta ? "#0b1220" : undefined,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 900, easing: "easeOutQuart" },
      plugins: { legend: { display: torta || s.series.length > 1, position: torta ? "right" : "top" } },
      scales: torta ? {} : { x: { stacked: s.apilado }, y: { stacked: s.apilado, beginAtZero: true, ticks: { precision: 0 } } },
    },
  });
}

async function vistaPreviaPdf(ruta, titulo) {
  const blob = await API.get(ruta);
  const url = URL.createObjectURL(blob);
  const caja = document.getElementById("modal-caja");
  caja.className = "caja vidrio ancha";
  caja.innerHTML = `<div class="barra"><h3 style="margin:0">Vista previa · ${esc(titulo)}</h3>
      <div><button class="btn mini" id="imprimir">Imprimir</button>
      <a class="btn sec mini" href="${url}" download="entrecol-${esc(titulo)}.pdf">Descargar</a>
      <button class="btn sec mini" id="cerrar-modal">Cerrar</button></div></div>
    <iframe src="${url}" title="Vista previa del PDF"></iframe>`;
  const modal = document.getElementById("modal");
  modal.classList.add("abierto");
  caja.querySelector("#imprimir").onclick = () => caja.querySelector("iframe").contentWindow.print();
  caja.querySelector("#cerrar-modal").onclick = () => { modal.classList.remove("abierto"); URL.revokeObjectURL(url); };
}
