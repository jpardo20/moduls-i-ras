// ======================================================
// web_v2.js — DEFINITIU
// Compatible amb JSON v3 (modules + RA + criteria)
// ======================================================

// ---------- CONFIG ----------
const DATA_FILES = {
    dam: "data/dam.json",
    smx: "data/smx.json"
};

// ---------- INIT ----------
document.addEventListener("DOMContentLoaded", async () => {
    const select = document.getElementById("cycleSelect");

    select.addEventListener("change", () => {
        loadAndRender(select.value);
    });

    // Càrrega inicial
    loadAndRender(select.value);
});

// ---------- LOAD ----------
async function loadAndRender(cycle) {

    const badge = document.getElementById("cycleBadge");

    badge.textContent = cycle.toUpperCase();

    badge.className =
        cycle === "dam"
            ? "cycle-badge badge-dam"
            : "cycle-badge badge-smx";

    const url = DATA_FILES[cycle];

    try {
        const res = await fetch(url);
        const data = await res.json();

        renderModules(data.modules);
    } catch (err) {
        console.error("Error carregant JSON:", err);
    }
}

// ---------- RENDER PRINCIPAL ----------
function renderModules(modules) {
    const container = document.getElementById("app");

    if (!container) {
        console.error("❌ No existeix #app al HTML");
        return;
    }

    container.innerHTML = "";

    modules.forEach(module => {
        container.appendChild(renderModule(module));
    });
}

// ---------- RENDER MÒDUL ----------
function renderModule(module) {
    const wrapper = document.createElement("div");
    wrapper.className = "module";

    // Header
    const header = document.createElement("div");
    header.className = "module-header";

    const totalRA = module.ra.length;

    const totalCriteria = module.ra.reduce(
        (total, ra) => total + (ra.criteria?.length || 0),
        0
    );

    const title = document.createElement("h2");
    title.textContent = `▶ ${module.id} — ${module.name}`;
    header.appendChild(title);

    const stats = document.createElement("div");
    stats.className = "module-stats";
    stats.textContent = `${totalRA} RA · ${totalCriteria} CA`;

    header.appendChild(stats);

    // 🔗 LINK NOMÉS A NIVELL DE MÒDUL
    if (module.sources && module.sources.length > 0) {
        const link = document.createElement("a");
        link.href = module.sources[0].official_url;
        link.target = "_blank";
        link.textContent = "📄 Document oficial";
        link.className = "module-link";
        header.appendChild(link);
    }

    wrapper.appendChild(header);

    // RA container
    const content = document.createElement("div");
    content.className = "module-content";
    content.classList.add("hidden");

    header.addEventListener("click", (e) => {

        if (e.target.tagName === "A") return;

        const hidden = content.classList.toggle("hidden");

        title.textContent =
            `${hidden ? "▶" : "▼"} ${module.id} — ${module.name}`;
    });
    module.ra.forEach(ra => {
        content.appendChild(renderRA(ra));
    });

    wrapper.appendChild(content);

    return wrapper;
}

// ---------- RENDER RA ----------
function renderRA(ra) {
    const wrapper = document.createElement("div");
    wrapper.className = "ra";

    // Header clicable
    const header = document.createElement("div");
    header.className = "ra-header";
    header.textContent = `▶ ${ra.code} — ${ra.short_description}`;

    const content = document.createElement("div");
    content.className = "ra-content hidden";

    // Toggle
    header.addEventListener("click", () => {
        const isHidden = content.classList.toggle("hidden");
        header.textContent = `${isHidden ? "▶" : "▼"} ${ra.code} — ${ra.short_description}`;
    });

    // Descripció
    if (ra.long_description) {
        const desc = document.createElement("p");
        desc.textContent = ra.long_description;
        desc.className = "ra-desc";
        content.appendChild(desc);
    }

    // Criteris
    if (ra.criteria && ra.criteria.length > 0) {
        const list = document.createElement("ul");
        list.className = "criteria-list";

        ra.criteria.forEach(c => {
            list.appendChild(renderCriterion(c));
        });

        content.appendChild(list);
    }

    wrapper.appendChild(header);
    wrapper.appendChild(content);

    return wrapper;
}

// ---------- RENDER CRITERI ----------
function renderCriterion(c) {
    const li = document.createElement("li");
    li.className = "criterion";

    li.textContent = `${c.code} — ${c.description}`;

    return li;
}