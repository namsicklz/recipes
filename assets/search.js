(function () {
  var input = document.getElementById("search");
  if (input) {
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var sections = document.querySelectorAll(".category");

      sections.forEach(function (section) {
        var items = section.querySelectorAll(".recipe-list li");
        var visibleCount = 0;

        items.forEach(function (li) {
          var text = li.textContent.toLowerCase();
          var match = q === "" || text.indexOf(q) !== -1;
          li.classList.toggle("hidden", !match);
          if (match) visibleCount++;
        });

        section.classList.toggle("hidden", visibleCount === 0);
      });
    });
  }

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
