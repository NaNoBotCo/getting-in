/* Getting In — sharing, QR, print, install, text size, ticks, hours in local time. */
(function () {
  var b = document.body, url = b.dataset.url, title = b.dataset.title, text = b.dataset.text;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  var live = document.createElement("div"); live.className = "toast"; live.setAttribute("role", "status"); live.hidden = true;
  document.body.appendChild(live); var tt;
  function toast(msg) {
    clearTimeout(tt); live.hidden = false; live.textContent = msg;
    tt = setTimeout(function () { live.hidden = true; live.textContent = ""; }, Math.max(2500, msg.length * 80));
  }
  function copy(s, msg) {
    var done = function () { toast(msg || "✓"); };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(s).then(done, fallback); else fallback();
    function fallback() { var a = document.createElement("textarea"); a.value = s; document.body.appendChild(a); a.select(); try { document.execCommand("copy"); done(); } catch (e) {} a.remove(); }
  }
  function share(u, extra) {
    var data = { title: title, text: text + (extra ? " · " + extra : ""), url: u };
    if (navigator.share) { navigator.share(data).catch(function () {}); return; }
    copy(data.text + " " + u, document.querySelector(".js-copy").dataset.copied);
  }
  var qr = document.querySelector(".qr-dialog");
  document.addEventListener("click", function (ev) {
    var el = ev.target.closest("button, a"); if (!el) return;
    if (el.classList.contains("js-share")) share(url);
    else if (el.classList.contains("js-copy")) copy(url, el.dataset.copied);
    else if (el.classList.contains("js-copytext")) copy(el.dataset.text, el.dataset.copied);
    else if (el.classList.contains("js-qr")) { if (qr.showModal) qr.showModal(); else qr.setAttribute("open", ""); }
    else if (el.classList.contains("js-print")) window.print();
    else if (el.classList.contains("js-sec-share")) {
      var id = el.dataset.id, h = document.querySelector("#" + id + " h2");
      share(url + "#" + id, h ? h.textContent : "");
    }
    else if (el.classList.contains("js-install") && deferred) { deferred.prompt(); deferred = null; el.hidden = true; }
    else if (el.dataset.size) {
      var cur = parseFloat(store("gi-size") || "19"), next = Math.max(15, Math.min(30, cur + 2 * parseFloat(el.dataset.size)));
      document.documentElement.style.setProperty("--size", next + "px"); store("gi-size", String(next));
    }
  });
  var s = store("gi-size"); if (s) document.documentElement.style.setProperty("--size", s + "px");

  /* add to home screen: Android prompt, iPhone hint */
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (ev) {
    ev.preventDefault(); deferred = ev;
    document.querySelectorAll(".js-install").forEach(function (x) { x.hidden = false; });
  });
  if (/iphone|ipad|ipod/i.test(navigator.userAgent) && !navigator.standalone) {
    document.querySelectorAll(".js-install").forEach(function (x) {
      x.hidden = false; x.addEventListener("click", function () { toast(b.dataset.ios); });
    });
  }
  if ("serviceWorker" in navigator) navigator.serviceWorker.register(b.dataset.sw).catch(function () {});

  /* checklist ticks, kept in this browser */
  document.querySelectorAll(".tick").forEach(function (c) {
    var k = "gi-tick-" + c.dataset.k; if (store(k) === "1") c.checked = true;
    c.addEventListener("change", function () { store(k, c.checked ? "1" : "0"); });
  });

  /* print with every answer open */
  window.addEventListener("beforeprint", function () { document.querySelectorAll("details").forEach(function (d) { d.dataset.was = d.open ? "1" : ""; d.open = true; }); });
  window.addEventListener("afterprint", function () { document.querySelectorAll("details").forEach(function (d) { d.open = d.dataset.was === "1"; }); });

  /* open a problem linked by #w3 */
  if (/^#w\d+$/.test(location.hash)) { var d = document.querySelector(location.hash); if (d) d.open = true; }

  /* US Eastern hours shown in the reader's own time */
  var lang = document.documentElement.lang;
  function offset(tz, d) {
    var p = {}; new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric" })
      .formatToParts(d).forEach(function (x) { p[x.type] = x.value; });
    return Date.UTC(+p.year, p.month - 1, +p.day, +p.hour % 24, +p.minute) - d.getTime();
  }
  function wall(tz, hhmm, base) {
    var p = {}; new Intl.DateTimeFormat("en-US", { timeZone: tz, year: "numeric", month: "numeric", day: "numeric" }).formatToParts(base).forEach(function (x) { p[x.type] = x.value; });
    var hm = hhmm.split(":"), guess = Date.UTC(+p.year, p.month - 1, +p.day, +hm[0], +hm[1]);
    return new Date(guess - offset(tz, new Date(guess)));
  }
  try {
    var now = new Date();
    document.querySelectorAll(".js-hours").forEach(function (h) {
      var tz = h.dataset.tz, o = wall(tz, h.dataset.open, now), c = wall(tz, h.dataset.close, now);
      var thu = new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short" }).format(now) === "Thu";
      var cNow = thu && h.dataset.thu ? wall(tz, h.dataset.thu, now) : c;
      var f = new Intl.DateTimeFormat(lang, { hour: "numeric", minute: "2-digit" });
      var dayNY = new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short" }).format(now);
      var dnum = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 }[dayNY];
      var open = h.dataset.days.split(",").indexOf(String(dnum)) > -1 && now >= o && now < cNow;
      var line = document.createElement("span");
      line.innerHTML = "";
      line.appendChild(document.createTextNode(h.dataset.label + ": " + f.format(o) + "–" + f.format(c) + " · "));
      var st = document.createElement("b"); st.className = open ? "on" : "off"; st.textContent = open ? h.dataset.on : h.dataset.off;
      line.appendChild(st); h.appendChild(document.createElement("br")); h.appendChild(line);
    });
  } catch (e) {}

  /* offer the reader's own language, without redirecting */
  try {
    var sg = document.querySelector(".suggest"), langs = JSON.parse(sg.dataset.langs);
    var want = (navigator.languages || [navigator.language || ""]).map(function (l) { return l.toLowerCase().split("-")[0]; });
    var here = lang.toLowerCase().split("-")[0];
    if (want[0] && want[0] !== here) {
      var code = want[0] === "fil" ? "tl" : want[0];
      if (langs[code]) { var a = document.createElement("a"); a.href = langs[code].href; a.textContent = langs[code].name + " →"; sg.appendChild(a); sg.hidden = false; }
    }
  } catch (e) {}
})();
