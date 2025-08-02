document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("addForm");
  const tableBody = document.querySelector("#debtTable tbody");
  const themeToggle = document.getElementById("themeToggle");
  const chartCanvas = document.getElementById("summaryChart");
  let chart;

  async function loadData() {
    const res = await fetch("/data");
    const data = await res.json();
    tableBody.innerHTML = "";
    let paid = 0, unpaid = 0;
    let totals = {};
    data.forEach(d => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><input value="${d.name}" class="form-control name"></td>
        <td><input value="${d.amount}" class="form-control amount" type="number"></td>
        <td><input value="${d.reason}" class="form-control reason"></td>
        <td><input value="${d.lender}" class="form-control lender"></td>
        <td class="text-center"><input type="checkbox" class="form-check-input status" ${d.status ? "checked" : ""}></td>
        <td>
          <button class="btn btn-primary btn-sm edit" data-id="${d.id}">Edit</button>
          <button class="btn btn-danger btn-sm delete" data-id="${d.id}">Delete</button>
        </td>`;
      tableBody.appendChild(row);

      if (d.status) paid++; else unpaid++;
      totals[d.name] = (totals[d.name] || 0) + d.amount;
    });

    if (chart) chart.destroy();
    chart = new Chart(chartCanvas, {
      type: 'pie',
      data: {
        labels: ['Paid', 'Unpaid'],
        datasets: [{ data: [paid, unpaid], backgroundColor: ['green', 'red'] }]
      }
    });

    document.querySelectorAll(".edit").forEach(btn => {
      btn.onclick = async () => {
        const tr = btn.closest("tr");
        const id = btn.dataset.id;
        const body = {
          name: tr.querySelector(".name").value,
          amount: parseFloat(tr.querySelector(".amount").value),
          reason: tr.querySelector(".reason").value,
          lender: tr.querySelector(".lender").value,
          status: tr.querySelector(".status").checked,
        };
        await fetch(`/edit/${id}`, { method: "POST", headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
        loadData();
      };
    });

    document.querySelectorAll(".delete").forEach(btn => {
      btn.onclick = async () => {
        await fetch(`/delete/${btn.dataset.id}`, { method: "POST" });
        loadData();
      };
    });

    document.querySelectorAll(".status").forEach(chk => {
      chk.onchange = async () => {
        const id = chk.closest("tr").querySelector(".edit").dataset.id;
        await fetch(`/toggle_status/${id}`, { method: "POST" });
        loadData();
      };
    });
  }

  form.onsubmit = async e => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.amount = parseFloat(data.amount);
    data.status = formData.has("status");
    await fetch("/add", { method: "POST", headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
    form.reset();
    loadData();
  };

  themeToggle.onclick = () => {
    const html = document.documentElement;
    const isDark = html.getAttribute("data-bs-theme") === "dark";
    html.setAttribute("data-bs-theme", isDark ? "light" : "dark");
    themeToggle.textContent = isDark ? "🌞 Light" : "🌙 Dark";
    localStorage.setItem("theme", isDark ? "light" : "dark");
  };

  if (localStorage.getItem("theme") === "light") {
    document.documentElement.setAttribute("data-bs-theme", "light");
    themeToggle.textContent = "🌞 Light";
  }

  loadData();
});
