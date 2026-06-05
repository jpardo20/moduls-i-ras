// ======================================================
// web_v2.js — DEFINITIU
// Compatible amb JSON v3 (modules + RA + criteria)
// ======================================================

// ---------- CONFIG ----------
const DATA_FILES = {
    dam: "data/dam.json",
    smx: "data/smx.json"
};

const WEIGHTS_FILE = "data/ponderacions.json";

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
        const [curriculumRes, weightsRes] = await Promise.all([
            fetch(url),
            fetch(WEIGHTS_FILE)
        ]);
        const data = await curriculumRes.json();
        const weights = await weightsRes.json();
        renderDashboard(
            data.modules,
            weights[data.cycle_code] || {}
        );
        renderModules(
            data.modules,
            weights[data.cycle_code] || {}
        );
    } catch (err) {
        console.error("Error carregant JSON:", err);
    }
}

function renderDashboard(modules, weightsByModule) {

    const dashboard =
        document.getElementById("dashboard");

    if (!dashboard) return;

    const totalModules = modules.length;

    const totalRA = modules.reduce(
        (sum, m) => sum + m.ra.length,
        0
    );

    const totalCA = modules.reduce(
        (sum, m) =>
            sum +
            m.ra.reduce(
                (s, ra) =>
                    s + (ra.criteria?.length || 0),
                0
            ),
        0
    );

    let configured = 0;

    modules.forEach(module => {

        const moduleWeights =
            weightsByModule[module.id] || {};

        const totalWeight =
            Object.values(moduleWeights)
                .reduce(
                    (sum, value) =>
                        sum + value,
                    0
                );

        if (totalWeight === 100) {
            configured++;
        }
    });

    const pending =
        totalModules - configured;

    dashboard.innerHTML = `
        <div class="dashboard-grid">

            <div class="dashboard-card">
                <span class="dashboard-number">
                    ${totalModules}
                </span>
                <span class="dashboard-label">
                    Mòduls
                </span>
            </div>

            <div class="dashboard-card">
                <span class="dashboard-number">
                    ${totalRA}
                </span>
                <span class="dashboard-label">
                    RA
                </span>
            </div>

            <div class="dashboard-card">
                <span class="dashboard-number">
                    ${totalCA}
                </span>
                <span class="dashboard-label">
                    CA
                </span>
            </div>

            <div class="dashboard-card ok">
                <span class="dashboard-number">
                    ${configured}
                </span>
                <span class="dashboard-label">
                    Configurats
                </span>
            </div>

            <div class="dashboard-card warning">
                <span class="dashboard-number">
                    ${pending}
                </span>
                <span class="dashboard-label">
                    Pendents
                </span>
            </div>

        </div>
    `;
}

// ---------- RENDER PRINCIPAL ----------
function renderModules(modules, weightsByModule) {
    const container = document.getElementById("app");
    if (!container) {
        console.error("❌ No existeix #app al HTML");
        return;
    }
    container.innerHTML = "";
    modules.forEach(module => {
        const moduleWeights =
            weightsByModule[module.id] || {};
        container.appendChild(
            renderModule(
                module,
                moduleWeights
            )
        );
    });
}

// ---------- RENDER MÒDUL ----------
function renderModule(module, moduleWeights) {
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
    const totalWeight = Object.values(moduleWeights)
        .reduce((sum, value) => sum + value, 0);
    const isValidWeight = totalWeight === 100;

    const title = document.createElement("h2");
    title.textContent = `▶ ${module.id} — ${module.name}`;
    header.appendChild(title);
    const stats = document.createElement("div");
    stats.className = "module-stats";
    if (!isValidWeight) {
        stats.classList.add("weight-warning");
    }
    stats.textContent =
        `${totalRA} RA · ${totalCriteria} CA · ${
            isValidWeight
                ? "✓ 100%"
                : `⚠ ${totalWeight}%`
        }`;
    header.appendChild(stats);
    // LINK NOMÉS A NIVELL DE MÒDUL
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

        const weight =
            moduleWeights[ra.code] || 0;

        content.appendChild(
            renderRA(
                ra,
                weight
            )
        );
    });
    wrapper.appendChild(content);
    return wrapper;
}

// ---------- RENDER RA ----------
function renderRA(ra, weight) {
    const wrapper = document.createElement("div");
    wrapper.className = "ra";
    // Header clicable
    const header = document.createElement("div");
    header.className = "ra-header";


    header.textContent =
         `▶ ${ra.code} (${weight}%) — ${ra.short_description}`;

    const content = document.createElement("div");
    content.className = "ra-content hidden";
    // Toggle
    header.addEventListener("click", () => {
        const isHidden = content.classList.toggle("hidden");
        header.textContent =
            `${isHidden ? "▶" : "▼"} ${ra.code} (${weight}%) — ${ra.short_description}`;    });
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