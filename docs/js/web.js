
let data = {
  dam: null,
  smx: null
};

async function loadData() {
  const dam = await fetch("./data/dam.json").then(r => r.json());
  const smx = await fetch("./data/smx.json").then(r => r.json());

  data.dam = dam.modules || dam;
  data.smx = smx.modules || smx;

  render("dam");
}

function render(cycle) {
  const container = document.getElementById("content");
  container.innerHTML = "";

  const modules = data[cycle];

  modules.forEach(module => {
    const div = document.createElement("div");
    div.className = "module";

    const title = document.createElement("h2");
    title.textContent = `${module.id} - ${module.name}`;
    div.appendChild(title);

    const raContainer = document.createElement("div");
    raContainer.className = "hidden";

    module.ra.forEach(ra => {
      const raDiv = document.createElement("div");
      raDiv.className = "ra";

      const url = module.sources?.[0]?.official_url || "#";

      raDiv.innerHTML = `
        <strong>${ra.code}</strong>: 
        <a href="${url}" target="_blank">${ra.long_description}</a>
      `;

      raContainer.appendChild(raDiv);
    });

    div.appendChild(raContainer);

    div.addEventListener("click", () => {
      raContainer.classList.toggle("hidden");
    });

    container.appendChild(div);
  });
}

document.getElementById("cycle").addEventListener("change", (e) => {
  render(e.target.value);
});

loadData();
