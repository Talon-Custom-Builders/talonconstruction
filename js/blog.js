/* The Journal — category filter.
 *
 * Progressive enhancement, and the order matters. The filter row ships
 * `hidden` in the generated markup and this reveals it. So with JavaScript
 * off, or before this runs, every post is visible and no control is offered
 * that cannot work. A crawler always sees the full archive.
 *
 * Loaded only by /blog/; null-guarded so it costs nothing if it ever ends up
 * on a page without a grid.
 */
(function () {
  "use strict";

  var filters = document.getElementById("blogFilters");
  var grid = document.getElementById("postGrid");
  var empty = document.getElementById("blogNoResults");
  if (!filters || !grid) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll(".post-card"));
  var buttons = Array.prototype.slice.call(filters.querySelectorAll(".blog-filter"));
  if (!cards.length || !buttons.length) return;

  filters.hidden = false;

  function apply(tag) {
    var shown = 0;
    cards.forEach(function (card) {
      var match = tag === "*" || card.getAttribute("data-tag") === tag;
      card.hidden = !match;
      if (match) shown++;
    });

    buttons.forEach(function (b) {
      var on = b.getAttribute("data-filter") === tag;
      b.classList.toggle("is-active", on);
      /* aria-pressed, not just a class: a screen-reader user needs to know
         which filter is on, and the visual state alone does not say. */
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });

    if (empty) empty.hidden = shown !== 0;
  }

  buttons.forEach(function (b) {
    b.setAttribute("aria-pressed", b.classList.contains("is-active") ? "true" : "false");
    b.addEventListener("click", function () {
      apply(b.getAttribute("data-filter"));
    });
  });
})();
