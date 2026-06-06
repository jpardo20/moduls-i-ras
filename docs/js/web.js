// ======================================================
// web_v2.js: DEFINITIU
// Compatible amb JSON v3 (modules + RA + criteria)
// ======================================================

const MAX_LEN = 120

// ---------- CONFIG ----------
const DATA_FILES = {
    dam: "data/dam.json",
    smx: "data/smx.json"
};

const LOCAL_MODULE_FILES = {
    dam: "data/moduls-locals-dam.json",
    smx: "data/moduls-locals-smx.json"
};
const WEIGHTS_FILE = "data/ponderacions.json";

const IMPLANTACIO_FILE =
    "data/implantacio.json";

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
        const [
            curriculumRes,
            weightsRes,
            localModulesRes,
            implantacioRes
        ] = await Promise.all([
            fetch(url),
            fetch(WEIGHTS_FILE),
            fetch(LOCAL_MODULE_FILES[cycle]),
            fetch(IMPLANTACIO_FILE)
        ]);
        const implantacio =
            await implantacioRes.json();
        const data =
            await curriculumRes.json();

        const weights =
            await weightsRes.json();
        const localModules =
            await localModulesRes.json();

        const modules = [
            ...data.modules,
            ...localModules.modules
        ];

        renderDashboard(
            modules,
            weights[data.cycle_code] || {}
        );

        renderModules(
            modules,
            weights[data.cycle_code] || {},
            implantacio[cycle]
        );
    } catch (err) {
        console.error("Error carregant JSON:", err);
    }
}

function getShortDescription(text, maxLen = 120) {

    if (!text) return "";

    const cleanText = text
        .replace(/\s+/g, " ")
        .trim();

    if (cleanText.length <= maxLen) {
        return cleanText;
    }

    const cut = cleanText.substring(0, maxLen);

    return (
        cut.substring(
            0,
            cut.lastIndexOf(" ")
        ) + "..."
    );
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

           ${pending > 0
            ? `
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
                    `
            : ""
        }

        </div>
    `;
}

// ---------- RENDER PRINCIPAL ----------
function renderModules(
    modules,
    weightsByModule,
    implantacio
) {
    const cursos = ["1", "2"];



    const container = document.getElementById("app");
    if (!container) {
        console.error("❌ No existeix #app al HTML");
        return;
    }

    container.innerHTML = "";

    cursos.forEach(curs => {

        const titol =
            document.createElement("div");

        titol.className =
            "course-title";

        titol.textContent =
            `▶${curs}r curs`;

        container.appendChild(titol);

        const courseContent =
            document.createElement("div");

        titol.addEventListener(
            "click",
            () => {
                const hidden =
                    courseContent.classList.toggle(
                        "hidden"
                    );
                titol.textContent =
                    `${hidden ? "▶" : "▼"} ${curs}r curs`;
            }
        );

        courseContent.className =
            "course-content hidden";

        container.appendChild(
            courseContent
        );

        const modulsCurs =
            modules.filter(module =>
                implantacio[curs]
                    ?.includes(module.id)
            );

        modulsCurs.forEach(module => {

            const moduleWeights =
                weightsByModule[module.id] || {};
            courseContent.appendChild(
                renderModule(
                    module,
                    moduleWeights
                )
            );
        });

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
    title.textContent = `▶${module.id}: ${module.name}`;
    header.appendChild(title);
    const stats = document.createElement("div");
    stats.className = "module-stats";
    if (!isValidWeight) {
        stats.classList.add("weight-warning");
    }

    stats.textContent =
        `${totalRA} RA${totalRA > 1 ? "s" : ""}  · ` +
        `${totalCriteria} CA${totalCriteria > 1 ? "s" : ""} · ${isValidWeight
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

    const weightsButton =
        document.createElement("button");

    weightsButton.className =
        "weights-button";

    weightsButton.textContent =
        "Pesos RA";

    const weightsPanel =
        document.createElement("div");

    weightsPanel.className =
        "weights-panel hidden";

    module.ra.forEach(ra => {
        const shortText =
            getShortDescription(
                ra.long_description,
                MAX_LEN
            );

        const weight =
            moduleWeights[ra.code];
        if (!weight) return;
        const row =
            document.createElement("div");
        row.className =
            "weight-row";
        row.innerHTML = `
            <div class="weight-info">
                <strong>${ra.code}</strong>
                <span>${shortText}</span>
            </div>

            <span class="weight-value">
                ${weight}%
            </span>
        `;
        weightsPanel.appendChild(row);
    });

    weightsButton.addEventListener(
        "click",
        (e) => {
            e.stopPropagation();
            const modal =
                document.getElementById(
                    "weightsModal"
                );
            const modalTitle =
                document.getElementById(
                    "weightsModalTitle"
                );
            const modalBody =
                document.getElementById(
                    "weightsModalBody"
                );
            modalTitle.textContent =
                `${module.id}: ${module.name}`;
            modalBody.innerHTML =
                weightsPanel.innerHTML;
            modal.classList.remove(
                "hidden"
            );
        }
    );

    if (Object.keys(moduleWeights).length > 0) {
        header.appendChild(weightsButton);
        wrapper.appendChild(content);
    }

    header.addEventListener("click", (e) => {
        if (e.target.tagName === "A") return;
        const hidden = content.classList.toggle("hidden");
        title.textContent =
            `${hidden ? "▶" : "▼"} ${module.id}: ${module.name}`;
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
        `▶${ra.code}: ${getShortDescription(
            ra.long_description
        )
        } (${weight}%)`;

    const content = document.createElement("div");
    content.className = "ra-content hidden";
    // Toggle
    header.addEventListener("click", () => {
        const isHidden =
            content.classList.toggle("hidden");

        header.textContent =
            `${isHidden ? "▶" : "▼"} ${ra.code}: ${getShortDescription(
                ra.long_description
            )
            } (${weight}%)`;

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
    li.innerHTML = `<strong>${c.code}</strong>: ${c.description}`;
    return li;
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        const modal =
            document.getElementById(
                "weightsModal"
            );

        const closeButton =
            document.getElementById(
                "closeWeightsModal"
            );

        if (!modal) return;

        closeButton.addEventListener(
            "click",
            () =>
                modal.classList.add(
                    "hidden"
                )
        );

        modal.addEventListener(
            "click",
            (e) => {
                if (e.target === modal) {
                    modal.classList.add(
                        "hidden"
                    );
                }
            }
        );
    }
);