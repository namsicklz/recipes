(function () {
  var btn = document.getElementById("shopping-list-btn");
  if (!btn) return;

  function findIngredientsList() {
    var headings = document.querySelectorAll(".recipe-card h3, .recipe-card h4");
    for (var i = 0; i < headings.length; i++) {
      if (headings[i].textContent.toLowerCase().indexOf("ingredient") !== -1) {
        var el = headings[i].nextElementSibling;
        while (el && el.tagName !== "UL") el = el.nextElementSibling;
        if (el) return el;
      }
    }
    return null;
  }

  var list = findIngredientsList();
  if (!list) {
    btn.style.display = "none";
    return;
  }

  function buildPrintContainer() {
    var existing = document.getElementById("print-shopping-list");
    if (existing) existing.remove();

    var titleEl = document.querySelector(".recipe-card h1");
    var title = titleEl ? titleEl.textContent.trim() : "Recipe";

    var container = document.createElement("div");
    container.id = "print-shopping-list";

    var h1 = document.createElement("h1");
    h1.textContent = title + " — Shopping List";
    container.appendChild(h1);

    var date = document.createElement("p");
    date.className = "print-date";
    date.textContent = new Date().toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
    container.appendChild(date);

    var ul = document.createElement("ul");
    Array.prototype.forEach.call(list.querySelectorAll("li"), function (li) {
      var item = document.createElement("li");
      item.textContent = li.textContent.trim();
      ul.appendChild(item);
    });
    container.appendChild(ul);

    document.body.appendChild(container);
  }

  btn.addEventListener("click", function () {
    buildPrintContainer();
    window.print();
  });

  window.addEventListener("afterprint", function () {
    var el = document.getElementById("print-shopping-list");
    if (el) el.remove();
  });
})();
