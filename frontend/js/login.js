// Inicio de sesion con usuario, contrasena y captcha (RF-01).
let captcha = { modo: "local", captcha_id: "" };

async function cargarCaptcha() {
  captcha = await API.get("/api/auth/captcha");
  if (captcha.modo === "recaptcha") {
    const div = document.getElementById("captcha-google");
    div.hidden = false;
    div.className = "g-recaptcha";
    div.dataset.sitekey = captcha.site_key;
    const s = document.createElement("script");
    s.src = "https://www.google.com/recaptcha/api.js";
    document.head.appendChild(s);
  } else {
    document.getElementById("captcha-local").hidden = false;
    document.getElementById("captcha-texto").hidden = false;
    document.getElementById("captcha-img").src = captcha.imagen;
    document.getElementById("captcha-texto").value = "";
  }
}

document.getElementById("captcha-nuevo").addEventListener("click", cargarCaptcha);

document.getElementById("form-login").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const msg = document.getElementById("mensaje");
  const boton = document.getElementById("entrar");
  const fd = new FormData();
  fd.append("username", document.getElementById("usuario").value.trim());
  fd.append("password", document.getElementById("clave").value);
  if (captcha.modo === "recaptcha") {
    fd.append("captcha_respuesta", window.grecaptcha ? grecaptcha.getResponse() : "");
  } else {
    fd.append("captcha_id", captcha.captcha_id);
    fd.append("captcha_respuesta", document.getElementById("captcha-texto").value);
  }
  boton.disabled = true;
  try {
    const r = await API.subir("/api/auth/login", fd);
    API.guardarSesion(r.access_token, r.usuario);
    location.href = "index.html";
  } catch (e) {
    mostrarMensaje(msg, e.message);
    if (captcha.modo === "recaptcha" && window.grecaptcha) grecaptcha.reset();
    else await cargarCaptcha();
  } finally {
    boton.disabled = false;
  }
});

if (API.token) location.href = "index.html";
cargarCaptcha().catch(e => mostrarMensaje(document.getElementById("mensaje"), "No hay conexión con la API: " + e.message));
