// Navegacion por modulos (RNF-06) y pantallas de administracion.
if (!API.token) location.href = "login.html";

const vista = document.getElementById("vista");
const modal = document.getElementById("modal");
const cajaModal = document.getElementById("modal-caja");
let entidades = [];

document.getElementById("quien").innerHTML = `<b>${esc(API.usuario?.nombre)}</b><br>${esc(API.usuario?.rol)}`;
document.getElementById("salir").onclick = async () => {
  try { await API.post("/api/auth/logout"); } finally { API.cerrarSesion(); }
};
if (!API.esAdmin()) document.querySelectorAll("[data-admin]").forEach(a => a.remove());
modal.addEventListener("click", ev => { if (ev.target === modal) modal.classList.remove("abierto"); });

const RUTAS = {
  inicio: vistaInicio,
  reportes: vistaReportes,
  datos: vistaDatos,
  cargas: vistaCargas,
  auditoria: () => vistaReporte(vista, "auditoria"),
};

async function navegar() {
  const [ruta, arg] = (location.hash.slice(1) || "inicio").split("/");
  document.querySelectorAll(".lateral a").forEach(a => a.classList.toggle("activo", a.getAttribute("href") === `#${ruta}`));
  const fn = RUTAS[ruta] || vistaInicio;
  vista.innerHTML = "";
  try { await fn(arg); } catch (e) { vista.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`; }
}
window.addEventListener("hashchange", navegar);

// ---------------------------------------------------------------- Inicio
async function vistaInicio() {
  vista.innerHTML = `
    <section class="panel vidrio"><h1>Hola, ${esc(API.usuario?.nombre?.split(" ")[0])}</h1>
      <p style="color:var(--texto-suave)">Elija un reporte o, si es administrador, gestione los datos del sistema.</p></section>
    <div class="tarjetas">${Object.entries(REPORTES).filter(([, d]) => !d.admin || API.esAdmin()).map(([k, d], i) => `
      <a class="tarjeta vidrio panel" style="text-decoration:none;color:inherit;animation-delay:${i * 60}ms" href="#reportes/${k}">
        <h3>${d.titulo}</h3><small>${d.desc}</small></a>`).join("")}</div>`;
}

// ---------------------------------------------------------------- Reportes
async function vistaReportes(clave) {
  const disponibles = Object.entries(REPORTES).filter(([k, d]) => k !== "auditoria" && (!d.admin || API.esAdmin()));
  clave = clave && REPORTES[clave] ? clave : disponibles[0][0];
  vista.innerHTML = `<div class="pestanas">${disponibles.map(([k, d]) =>
    `<button class="${k === clave ? "activo" : ""}" data-k="${k}">${d.titulo}</button>`).join("")}</div><div id="rep"></div>`;
  vista.querySelectorAll(".pestanas button").forEach(b => b.onclick = () => location.hash = `reportes/${b.dataset.k}`);
  await vistaReporte(vista.querySelector("#rep"), clave);
}

// ---------------------------------------------------------------- CRUD
async function vistaDatos(clave) {
  if (!entidades.length) entidades = await API.get("/api/crud");
  const ent = entidades.find(e => e.clave === clave) || entidades[0];
  const modulos = [...new Set(entidades.map(e => e.modulo))];
  vista.innerHTML = `
    <section class="panel vidrio">
      <div class="fila">
        <div><label>Entidad</label><select id="ent">${modulos.map(m => `<optgroup label="${m}">${entidades.filter(e => e.modulo === m)
          .map(e => `<option value="${e.clave}" ${e.clave === ent.clave ? "selected" : ""}>${e.titulo}</option>`).join("")}</optgroup>`).join("")}</select></div>
        <div><label>Buscar</label><input id="buscar" placeholder="Escriba y presione Enter"></div>
        ${ent.solo_lectura ? "" : `<button class="btn" id="nuevo">+ Nuevo</button>`}
      </div>
    </section>
    <section class="panel vidrio"><h2>${ent.titulo}</h2><div id="tabla"></div>
      <div class="paginacion"><button class="btn sec mini" id="ant">←</button><span id="pag"></span><button class="btn sec mini" id="sig">→</button></div>
    </section>`;
  let pagina = 1, q = "";
  const tam = 25;
  vista.querySelector("#ent").onchange = ev => location.hash = `datos/${ev.target.value}`;
  vista.querySelector("#buscar").onkeydown = ev => { if (ev.key === "Enter") { q = ev.target.value; pagina = 1; cargar(); } };
  vista.querySelector("#ant").onclick = () => { if (pagina > 1) { pagina--; cargar(); } };
  vista.querySelector("#sig").onclick = () => { pagina++; cargar(); };
  vista.querySelector("#nuevo")?.addEventListener("click", () => formulario(ent, null, cargar));

  async function cargar() {
    const r = await API.get(`/api/crud/${ent.clave}?pagina=${pagina}&tam=${tam}&q=${encodeURIComponent(q)}`);
    const paginas = Math.max(1, Math.ceil(r.total / tam));
    if (pagina > paginas) { pagina = paginas; return cargar(); }
    vista.querySelector("#pag").textContent = `Página ${pagina} de ${paginas} · ${r.total} registros`;
    const cols = r.filas.length ? Object.keys(r.filas[0]).filter(c => c !== "id" && c !== "etiqueta") : [];
    vista.querySelector("#tabla").innerHTML = r.filas.length ? `<div class="tabla-envoltura"><table>
      <thead><tr>${cols.map(c => `<th>${esc(c.replaceAll("_", " "))}</th>`).join("")}<th></th></tr></thead>
      <tbody>${r.filas.map(f => `<tr>${cols.map(c => `<td>${esc(formatear(f[c]))}</td>`).join("")}
        <td class="acciones">${ent.solo_lectura ? "" : `<button class="btn sec mini" data-ed="${esc(f.id)}">Editar</button>
        <button class="btn peligro mini" data-del="${esc(f.id)}">Eliminar</button>`}</td></tr>`).join("")}</tbody></table></div>`
      : `<p class="nota">No hay registros.</p>`;
    vista.querySelectorAll("[data-ed]").forEach(b => b.onclick = async () =>
      formulario(ent, await API.get(`/api/crud/${ent.clave}/${encodeURIComponent(b.dataset.ed)}`), cargar));
    vista.querySelectorAll("[data-del]").forEach(b => b.onclick = async () => {
      if (!confirm("¿Eliminar este registro? La acción queda en la auditoría.")) return;
      try { await API.del(`/api/crud/${ent.clave}/${encodeURIComponent(b.dataset.del)}`); cargar(); }
      catch (e) { alert(e.message); }
    });
  }
  await cargar();
}

async function opcionesFk(clave) {
  const r = await API.get(`/api/crud/${clave}?tam=500`);
  return r.filas.map(f => [f.id, f.etiqueta]);
}

async function formulario(ent, registro, alGuardar) {
  const editando = !!registro;
  const pk = ent.pk.split(",");
  const campos = await Promise.all(ent.campos.filter(c => !(c.auto && !editando)).map(async c => {
    const v = registro?.[c.nombre] ?? "";
    const bloqueado = (editando && pk.includes(c.nombre)) ? "disabled" : "";
    const req = c.requerido && !(c.tipo === "password" && editando) ? "required" : "";
    if (c.fk) {
      const ops = await opcionesFk(c.fk);
      return `<label>${c.etiqueta}</label><select name="${c.nombre}" ${req} ${bloqueado}>
        <option value="">—</option>${ops.map(([id, t]) => `<option value="${esc(id)}" ${String(id) === String(v) ? "selected" : ""}>${esc(t)}</option>`).join("")}</select>`;
    }
    if (c.tipo === "bool") {
      return `<label><input type="checkbox" name="${c.nombre}" style="width:auto" ${v === 0 ? "" : "checked"}> ${c.etiqueta}</label>`;
    }
    const tipo = { entero: "number", decimal: "number", fecha: "date", password: "password" }[c.tipo] || "text";
    const paso = c.tipo === "decimal" ? 'step="any"' : "";
    const valor = c.tipo === "password" ? "" : (c.tipo === "fecha" ? String(v).slice(0, 10) : v);
    const ayuda = c.tipo === "password" && editando ? ' placeholder="Dejar vacío para no cambiarla"' : "";
    return `<label>${c.etiqueta}</label><input name="${c.nombre}" type="${tipo}" ${paso} value="${esc(valor)}" ${req} ${bloqueado}${ayuda}>`;
  }));
  cajaModal.className = "caja vidrio";
  cajaModal.innerHTML = `<h2>${editando ? "Editar" : "Nuevo"} · ${ent.titulo}</h2>
    <form id="form-ent">${campos.join("")}
      <div class="fila" style="margin-top:18px;justify-content:flex-end">
        <button type="button" class="btn sec" id="cancelar">Cancelar</button><button class="btn">Guardar</button></div>
      <div id="msg-ent" class="mensaje"></div></form>`;
  modal.classList.add("abierto");
  cajaModal.querySelector("#cancelar").onclick = () => modal.classList.remove("abierto");
  cajaModal.querySelector("#form-ent").onsubmit = async ev => {
    ev.preventDefault();
    const datos = {};
    ent.campos.forEach(c => {
      const el = ev.target.elements[c.nombre];
      if (!el || el.disabled) return;
      datos[c.nombre] = c.tipo === "bool" ? el.checked : el.value;
    });
    try {
      if (editando) await API.put(`/api/crud/${ent.clave}/${encodeURIComponent(registro.id)}`, datos);
      else await API.post(`/api/crud/${ent.clave}`, datos);
      modal.classList.remove("abierto");
      alGuardar();
    } catch (e) { mostrarMensaje(cajaModal.querySelector("#msg-ent"), e.message); }
  };
}

// ---------------------------------------------------------------- Cargas ETL
function vistaCargas() {
  const origenes = [
    ["nomina", "Nómina (Excel)", ".xlsx", true],
    ["peliculas", "Películas (DAT)", ".dat,.txt", false],
    ["libros", "Libros (JSON)", ".json", false],
  ];
  vista.innerHTML = `<section class="panel vidrio"><h2>Carga de archivos</h2>
    <p class="nota">Puede volver a cargar un archivo con la misma estructura: los registros existentes se actualizan y no se duplican.
    Si la estructura no corresponde, no se modifica nada.</p></section>
    ${origenes.map(([k, t, ext, periodo], i) => `
    <section class="panel vidrio" style="animation-delay:${i * 70}ms"><h3>${t}</h3>
      <form class="fila" data-origen="${k}">
        <div><label>Archivo</label><input type="file" name="archivo" accept="${ext}" required></div>
        ${periodo ? `<div><label>Año del periodo (opcional)</label><input type="number" name="anio" min="1990" max="2100"></div>
          <div><label>Mes (opcional)</label><input type="number" name="mes" min="1" max="12"></div>` : ""}
        <button class="btn">Cargar</button>
      </form><div class="resumen"></div></section>`).join("")}`;
  vista.querySelectorAll("form[data-origen]").forEach(form => form.onsubmit = async ev => {
    ev.preventDefault();
    const destino = form.parentElement.querySelector(".resumen");
    const boton = form.querySelector("button");
    boton.disabled = true;
    boton.textContent = "Cargando…";
    destino.innerHTML = "";
    try {
      const r = await API.subir(`/api/etl/${form.dataset.origen}`, new FormData(form));
      destino.innerHTML = `<div class="kpis" style="margin-top:14px">
        ${[["Leídos", r.leidos], ["Insertados", r.insertados], ["Actualizados", r.actualizados], ["Sin cambios", r.sin_cambios], ["Rechazados", r.rechazados]]
          .map(([e, v]) => `<div class="kpi vidrio"><div class="v">${v}</div><div class="e">${e}</div></div>`).join("")}</div>
        ${r.avisos.length ? `<h3 style="margin-top:14px">Avisos</h3><ul class="nota">${r.avisos.map(a => `<li>${esc(a)}</li>`).join("")}</ul>` : ""}
        ${r.detalle_rechazos.length ? `<h3>Registros rechazados</h3><div class="tabla-envoltura"><table><thead><tr><th>Registro</th><th>Motivo</th></tr></thead>
          <tbody>${r.detalle_rechazos.map(x => `<tr><td>${esc(x.registro)}</td><td>${esc(x.motivo)}</td></tr>`).join("")}</tbody></table></div>` : ""}`;
    } catch (e) {
      destino.innerHTML = `<div class="mensaje error">${esc(e.message)}</div>`;
    } finally {
      boton.disabled = false;
      boton.textContent = "Cargar";
    }
  });
}

navegar();
