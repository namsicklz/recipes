(function () {
  var input = document.getElementById("search");
  var chips = document.querySelectorAll(".owner-chip");
  var activeOwner = "all";

  function applyFilters() {
    var q = input ? input.value.trim().toLowerCase() : "";
    var sections = document.querySelectorAll(".category");

    sections.forEach(function (section) {
      var items = section.querySelectorAll(".recipe-list li");
      var visibleCount = 0;

      items.forEach(function (li) {
        var text = li.textContent.toLowerCase();
        var owner = li.getAttribute("data-owner") || "";
        var matchesText = q === "" || text.indexOf(q) !== -1;
        var matchesOwner = activeOwner === "all" || owner === activeOwner;
        var match = matchesText && matchesOwner;
        li.classList.toggle("hidden", !match);
        if (match) visibleCount++;
      });

      section.classList.toggle("hidden", visibleCount === 0);
    });
  }

  if (input) {
    input.addEventListener("input", applyFilters);
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) { c.classList.remove("active"); });
      chip.classList.add("active");
      activeOwner = chip.getAttribute("data-owner");
      applyFilters();
    });
  });

  var jump = document.getElementById("cat-jump");
  if (jump) {
    jump.addEventListener("change", function () {
      var target = jump.value ? document.querySelector(jump.value) : null;
      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      jump.selectedIndex = 0;
    });
  }
})();
