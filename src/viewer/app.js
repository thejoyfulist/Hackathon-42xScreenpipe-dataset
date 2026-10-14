// Pipeline Workspace: a static viewer for the fictional dataset.
// Everything renders as plain DOM text so screenpipe can read it through
// the accessibility tree. Deep links: #mail/E06, #chat/sales-ops,
// #meetings/M01, #documents, #ledger/2026-03/5200.
(function () {
  const D = window.DATASET;
  const app = document.getElementById("app");
  const me = Object.values(D.people).find((p) => p.role === "Financial Controller");
  document.getElementById("user").textContent = `${me.name} - ${me.role}`;

  const el = (tag, attrs = {}, ...children) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") n.className = v; else if (k === "text") n.textContent = v; else n.setAttribute(k, v);
    }
    for (const c of children) if (c != null) n.append(c);
    return n;
  };
  const eur = (x) => x.toLocaleString("en-IE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function layout(listNodes, paneNode, searchNode) {
    app.replaceChildren();
    const list = el("div", { class: "list" });
    if (searchNode) list.append(el("div", { class: "search" }, searchNode));
    listNodes.forEach((n) => list.append(n));
    app.append(list, el("div", { class: "pane" }, paneNode));
  }

  function mail(id, q = "") {
    const search = el("input", { type: "search", placeholder: "Search mail", value: q, "aria-label": "Search mail" });
    search.addEventListener("input", () => mail(id, search.value));
    const ql = q.toLowerCase();
    const items = D.emails.filter((e) => !ql || (e.subject + e.body + e.from_display).toLowerCase().includes(ql));
    const cur = items.find((e) => e.id === id) || items[0];
    const nodes = items.map((e) => el("a", { class: "item" + (cur && e.id === cur.id ? " active" : ""), href: `#mail/${e.id}` },
      el("div", { class: "t", text: e.subject }), el("div", { class: "s", text: `${e.from_display.split(" <")[0]} - ${e.date}` })));
    let pane = el("p", { class: "empty", text: "No message." });
    if (cur) {
      pane = el("article", {},
        el("h1", { text: cur.subject }),
        el("div", { class: "meta" },
          el("div", { text: `From: ${cur.from_display}` }), el("div", { text: `To: ${cur.to_display.join(", ")}` }),
          cur.cc_display.length ? el("div", { text: `Cc: ${cur.cc_display.join(", ")}` }) : null,
          el("div", { text: `Date: ${cur.date}` })),
        el("div", { class: "body", text: cur.body }));
      if (cur.attachments) {
        const att = el("div", { class: "att" }, el("span", { text: "Attachments: " }));
        cur.attachments.forEach((a) => {
          const doc = D.documents.find((d) => d.id === a);
          att.append(doc ? el("a", { href: doc.file, target: "_blank", text: `${a} - ${doc.title}` })
                         : el("a", { href: "#documents", text: `${a} (presentation, see presentations folder)` }));
        });
        pane.append(att);
      }
    }
    layout(nodes, pane, search);
    search.focus();
    search.setSelectionRange(q.length, q.length);
  }

  function chat(channel) {
    const ch = D.channels[channel] ? channel : Object.keys(D.channels)[0];
    const nodes = Object.entries(D.channels).map(([k, v]) => el("a", { class: "item" + (k === ch ? " active" : ""), href: `#chat/${k}` },
      el("div", { class: "t", text: k.startsWith("dm-") ? v.replace("Direct messages: ", "") : `# ${k}` }), el("div", { class: "s", text: v })));
    const pane = el("section", {}, el("h1", { text: ch.startsWith("dm-") ? D.channels[ch] : `# ${ch}` }));
    D.chats.filter((c) => c.channel === ch).forEach((c) => pane.append(
      el("div", { class: "msg" }, el("span", { class: "who", text: c.author_name }), el("span", { class: "when", text: c.date }), el("div", { text: c.text }))));
    layout(nodes, pane);
  }

  function meetings(id) {
    const cur = D.meetings.find((m) => m.id === id) || D.meetings[0];
    const nodes = D.meetings.map((m) => el("a", { class: "item" + (m.id === cur.id ? " active" : ""), href: `#meetings/${m.id}` },
      el("div", { class: "t", text: m.title }), el("div", { class: "s", text: m.date })));
    const pane = el("section", {}, el("h1", { text: cur.title }),
      el("div", { class: "meta", text: `${cur.date} - Attendees: ${cur.attendees.join(", ")} - Transcript` }));
    cur.lines.forEach((l) => pane.append(el("div", { class: "line" + (/^(Decision|Action)/.test(l.text) ? " key" : "") }, el("strong", { text: `${l.speaker}: ` }), l.text)));
    layout(nodes, pane);
  }

  function documents() {
    const nodes = D.documents.map((d) => el("a", { class: "item", href: d.file, target: "_blank" },
      el("div", { class: "t", text: d.title }), el("div", { class: "s", text: `${d.id} - ${d.date}` })));
    const pane = el("section", {}, el("h1", { text: "Documents" }),
      el("p", { text: "Supplier and customer documents. Workbooks (.xlsx) and presentations (.pptx) are in the workbooks and presentations folders of the dataset." }));
    layout(nodes, pane);
  }

  function ledger(month, account) {
    const months = Object.keys(D.gl);
    const m = months.includes(month) ? month : months[months.length - 1];
    const rows = D.gl[m];
    const accounts = [...new Set(rows.map((r) => r.account))].sort();
    const acc = accounts.includes(account) ? account : "";
    const monthSel = el("select", { "aria-label": "Period" }); months.forEach((x) => monthSel.append(el("option", { value: x, text: x })));
    monthSel.value = m;
    const accSel = el("select", { "aria-label": "Account" }, el("option", { value: "", text: "All accounts" }));
    accounts.forEach((a) => accSel.append(el("option", { value: a, text: `${a} ${D.accounts[a].name}` })));
    accSel.value = acc;
    const q = el("input", { type: "search", placeholder: "Filter counterparty, document, description", "aria-label": "Filter" });
    const go = () => { location.hash = `#ledger/${monthSel.value}/${accSel.value}`; };
    monthSel.addEventListener("change", go); accSel.addEventListener("change", go);
    const table = el("table");
    const total = el("div", { class: "total" });
    const render = () => {
      const ql = q.value.toLowerCase();
      const shown = rows.filter((r) => (!acc || r.account === acc) && (!ql || (r.counterparty + r.document_ref + r.description).toLowerCase().includes(ql)));
      const head = el("tr"); ["Entry", "Date", "Account", "Counterparty", "Document", "Description", "Debit", "Credit"].forEach((h, i) => head.append(el("th", { class: i > 5 ? "num" : "", text: h })));
      table.replaceChildren(el("thead", {}, head));
      const body = el("tbody");
      let dr = 0, cr = 0;
      shown.forEach((r) => {
        dr += +r.debit; cr += +r.credit;
        const tr = el("tr");
        [r.entry_id, r.posting_date, r.account, r.counterparty, r.document_ref, r.description].forEach((v) => tr.append(el("td", { text: v })));
        tr.append(el("td", { class: "num", text: eur(+r.debit) }), el("td", { class: "num", text: eur(+r.credit) }));
        body.append(tr);
      });
      table.append(body);
      total.textContent = `${shown.length} entries - debit ${eur(dr)} - credit ${eur(cr)}`;
    };
    q.addEventListener("input", render);
    render();
    const nodes = months.map((x) => el("a", { class: "item" + (x === m ? " active" : ""), href: `#ledger/${x}/` }, el("div", { class: "t", text: `GL detail ${x}` }), el("div", { class: "s", text: `${D.gl[x].length} entries` })));
    layout(nodes, el("section", {}, el("h1", { text: `Pipeline ERP - GL detail ${m}` }), el("div", { class: "filters" }, monthSel, accSel, q), total, table));
  }

  function route() {
    const [tab, a, b] = location.hash.replace(/^#/, "").split("/");
    const t = ["mail", "chat", "meetings", "documents", "ledger"].includes(tab) ? tab : "mail";
    document.querySelectorAll(".tabs a").forEach((x) => x.classList.toggle("active", x.dataset.tab === t));
    document.title = `Pipeline Workspace - ${t[0].toUpperCase() + t.slice(1)}`;
    ({ mail: () => mail(a), chat: () => chat(a), meetings: () => meetings(a), documents, ledger: () => ledger(a, b) })[t]();
  }
  window.addEventListener("hashchange", route);
  route();
})();
