(function () {
  "use strict";

  var input = document.getElementById("site-search-input");
  var resultsEl = document.getElementById("site-search-results");
  var statusEl = document.getElementById("site-search-status");
  var form = document.querySelector(".site-search");

  if (!input || !resultsEl || !statusEl || !form) {
    return;
  }

  var indexUrl = form.getAttribute("data-search-index") || "/search.json";
  var docs = null;
  var ready = null;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function setStatus(text) {
    statusEl.textContent = text || "";
  }

  function loadDocs() {
    if (ready) {
      return ready;
    }

    ready = fetch(indexUrl)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load search index");
        }
        return response.json();
      })
      .then(function (data) {
        docs = data.map(function (doc) {
          return {
            title: doc.title || "",
            subtitle: doc.subtitle || "",
            description: doc.description || "",
            tags: doc.tags || [],
            url: doc.url || "",
            date: doc.date || "",
            content: doc.content || "",
            haystack: [
              doc.title || "",
              doc.subtitle || "",
              doc.description || "",
              (doc.tags || []).join(" "),
              doc.content || ""
            ].join("\n").toLowerCase()
          };
        });
        return docs;
      });

    return ready;
  }

  function scoreDoc(doc, terms) {
    var score = 0;
    var title = doc.title.toLowerCase();
    var subtitle = doc.subtitle.toLowerCase();
    var description = doc.description.toLowerCase();
    var tags = doc.tags.join(" ").toLowerCase();

    for (var i = 0; i < terms.length; i += 1) {
      var term = terms[i];
      if (!term) {
        continue;
      }
      if (title.indexOf(term) !== -1) {
        score += 12;
      }
      if (tags.indexOf(term) !== -1) {
        score += 8;
      }
      if (subtitle.indexOf(term) !== -1) {
        score += 5;
      }
      if (description.indexOf(term) !== -1) {
        score += 3;
      }
      if (doc.haystack.indexOf(term) !== -1) {
        score += 1;
      } else {
        return 0;
      }
    }
    return score;
  }

  function searchDocs(query) {
    var terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length || !docs) {
      return [];
    }

    return docs
      .map(function (doc) {
        return { doc: doc, score: scoreDoc(doc, terms) };
      })
      .filter(function (item) {
        return item.score > 0;
      })
      .sort(function (a, b) {
        return b.score - a.score;
      })
      .slice(0, 20)
      .map(function (item) {
        return item.doc;
      });
  }

  function renderResults(hits) {
    if (!hits.length) {
      resultsEl.hidden = true;
      resultsEl.innerHTML = "";
      return;
    }

    resultsEl.hidden = false;
    resultsEl.innerHTML = hits.map(function (doc) {
      var subtitle = doc.subtitle
        ? '<h3 class="post-subtitle">' + escapeHtml(doc.subtitle) + "</h3>"
        : "";
      var snippet = doc.description || "";

      return (
        '<div class="post-preview">' +
          '<a href="' + escapeHtml(doc.url) + '">' +
            '<h2 class="post-title">' + escapeHtml(doc.title) + "</h2>" +
            subtitle +
            (snippet ? '<div class="post-content-preview">' + escapeHtml(snippet) + "</div>" : "") +
          "</a>" +
          '<p class="post-meta">' + escapeHtml(doc.date) + "</p>" +
        "</div><hr>"
      );
    }).join("");
  }

  function runSearch(query) {
    var q = (query || "").trim();
    if (!q) {
      setStatus("");
      renderResults([]);
      return;
    }

    setStatus("Searching…");
    loadDocs()
      .then(function () {
        var hits = searchDocs(q);
        setStatus(
          hits.length +
            (hits.length === 1 ? " result" : " results") +
            ' for "' +
            q +
            '"'
        );
        renderResults(hits);
      })
      .catch(function () {
        setStatus("Search index could not be loaded.");
        renderResults([]);
      });
  }

  var debounceTimer = null;
  input.addEventListener("input", function () {
    window.clearTimeout(debounceTimer);
    debounceTimer = window.setTimeout(function () {
      runSearch(input.value);
    }, 160);
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    runSearch(input.value);
  });

  var params = new URLSearchParams(window.location.search);
  var initial = params.get("q");
  if (initial) {
    input.value = initial;
    runSearch(initial);
  } else {
    loadDocs().catch(function () {});
  }
})();
