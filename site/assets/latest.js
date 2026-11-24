// Home page: copy the three newest entries from log.html into #latest.
// Same-origin request only. Without JavaScript, or opened as a local file, the link to the log stays.
(async () => {
  const box = document.getElementById("latest");
  if (!box) return;
  try {
    const res = await fetch("log.html");
    if (!res.ok) return;
    const doc = new DOMParser().parseFromString(await res.text(), "text/html");
    const items = [...doc.querySelectorAll("article.entry")].slice(0, 3);
    if (!items.length) return;
    box.replaceChildren();
    for (const item of items) {
      const copy = document.importNode(item, true);
      copy.removeAttribute("id");
      copy.querySelectorAll('a[href^="#"]').forEach(a => a.setAttribute("href", "log.html" + a.getAttribute("href")));
      box.append(copy);
    }
  } catch (e) {
    // keep the fallback link
  }
})();
