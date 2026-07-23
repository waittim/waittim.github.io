/*!
 * Hux Blog theme scripts (vanilla JS)
 * Navbar scroll, responsive tables/embeds, side catalog, tag cloud.
 */

(function () {
  "use strict";

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function wrapTables() {
    document.querySelectorAll(".post-container table").forEach(function (table) {
      if (table.parentElement && table.parentElement.classList.contains("table-responsive")) {
        return;
      }
      table.classList.add("table");
      var wrap = document.createElement("div");
      wrap.className = "table-responsive";
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    });
  }

  function wrapEmbeds() {
    document.querySelectorAll(".post-container iframe").forEach(function (iframe) {
      if (iframe.classList.contains("utterances-frame")) {
        return;
      }
      if (iframe.closest(".embed-responsive")) {
        return;
      }

      var width = parseInt(iframe.getAttribute("width"), 10) || 16;
      var height = parseInt(iframe.getAttribute("height"), 10) || 9;
      var wrap = document.createElement("div");
      wrap.className = "embed-responsive";
      wrap.style.paddingBottom = ((height / width) * 100) + "%";

      iframe.classList.add("embed-responsive-item");
      iframe.removeAttribute("width");
      iframe.removeAttribute("height");

      iframe.parentNode.insertBefore(wrap, iframe);
      wrap.appendChild(iframe);
    });
  }

  function initNavbarScroll() {
    var MQL = 1170;
    if (window.innerWidth <= MQL) {
      return;
    }

    var navbar = document.querySelector(".navbar-custom");
    var catalog = document.querySelector(".side-catalog");
    var intro = document.querySelector(".intro-header .container");
    if (!navbar) {
      return;
    }

    var headerHeight = navbar.offsetHeight;
    var bannerHeight = intro ? intro.offsetHeight : 0;
    var previousTop = 0;

    window.addEventListener("scroll", function () {
      var currentTop = window.pageYOffset || document.documentElement.scrollTop;

      if (currentTop < previousTop) {
        if (currentTop > 0 && navbar.classList.contains("is-fixed")) {
          navbar.classList.add("is-visible");
        } else {
          navbar.classList.remove("is-visible", "is-fixed");
        }
      } else {
        navbar.classList.remove("is-visible");
        if (currentTop > headerHeight && !navbar.classList.contains("is-fixed")) {
          navbar.classList.add("is-fixed");
        }
      }
      previousTop = currentTop;

      if (catalog) {
        if (currentTop > bannerHeight + 41) {
          catalog.classList.add("fixed");
        } else {
          catalog.classList.remove("fixed");
        }
      }
    }, { passive: true });
  }

  function generateCatalog(selector) {
    var post = document.querySelector("div.post-container");
    var root = document.querySelector(selector);
    if (!post || !root) {
      return;
    }

    var levelNodes = {};
    post.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach(function (heading) {
      if (!heading.id) {
        return;
      }

      var level = parseInt(heading.tagName.substring(1), 10);
      var link = document.createElement("a");
      link.href = "#" + heading.id;
      link.rel = "nofollow";
      link.textContent = heading.textContent;

      var item = document.createElement("li");
      item.className = heading.tagName.toLowerCase() + "_nav";
      item.appendChild(link);

      var parentLevel = level - 1;
      while (parentLevel > 0 && !levelNodes[parentLevel]) {
        parentLevel -= 1;
      }

      if (parentLevel > 0) {
        var parentItem = levelNodes[parentLevel];
        var sublist = null;
        Array.prototype.forEach.call(parentItem.children, function (child) {
          if (!sublist && child.classList && child.classList.contains("catalog-sublist")) {
            sublist = child;
          }
        });
        if (!sublist) {
          sublist = document.createElement("ul");
          sublist.className = "catalog-sublist";
          parentItem.appendChild(sublist);
        }
        sublist.appendChild(item);
      } else {
        root.appendChild(item);
      }

      for (var clearLevel = level; clearLevel <= 6; clearLevel += 1) {
        delete levelNodes[clearLevel];
      }
      levelNodes[level] = item;
    });
  }

  function initCatalogNav(catalogBody) {
    var links = Array.prototype.slice.call(catalogBody.querySelectorAll("a[href^='#']"));
    if (!links.length) {
      return;
    }

    var entries = links.map(function (link) {
      var id = decodeURIComponent(link.getAttribute("href").slice(1));
      return {
        link: link,
        item: link.parentElement,
        target: document.getElementById(id)
      };
    }).filter(function (entry) {
      return !!entry.target;
    });

    if (!entries.length) {
      return;
    }

    var padding = 80;

    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        var id = decodeURIComponent(link.getAttribute("href").slice(1));
        var target = document.getElementById(id);
        if (!target) {
          return;
        }
        event.preventDefault();
        var top = target.getBoundingClientRect().top + window.pageYOffset - padding;
        window.scrollTo({ top: top, behavior: "smooth" });
      });
    });

    function setActive(activeEntry) {
      entries.forEach(function (entry) {
        entry.item.classList.toggle("active", entry === activeEntry);
      });
    }

    if ("IntersectionObserver" in window) {
      var visible = new Map();
      var observer = new IntersectionObserver(function (observed) {
        observed.forEach(function (obs) {
          visible.set(obs.target, obs.isIntersecting && obs.intersectionRatio > 0);
        });

        var current = null;
        entries.forEach(function (entry) {
          if (visible.get(entry.target)) {
            current = entry;
          }
        });
        if (current) {
          setActive(current);
        }
      }, {
        rootMargin: "-" + padding + "px 0px -55% 0px",
        threshold: [0, 1]
      });

      entries.forEach(function (entry) {
        observer.observe(entry.target);
      });
    } else {
      window.addEventListener("scroll", function () {
        var scrollPos = window.pageYOffset + padding + 1;
        var current = entries[0];
        entries.forEach(function (entry) {
          if (entry.target.offsetTop <= scrollPos) {
            current = entry;
          }
        });
        setActive(current);
      }, { passive: true });
    }
  }

  function initCatalog() {
    var catalogBody = document.querySelector(".catalog-body");
    if (!catalogBody) {
      return;
    }

    generateCatalog(".catalog-body");
    initCatalogNav(catalogBody);

    var toggle = document.querySelector(".catalog-toggle");
    if (toggle) {
      toggle.addEventListener("click", function (event) {
        event.preventDefault();
        var catalog = document.querySelector(".side-catalog");
        if (catalog) {
          catalog.classList.toggle("fold");
        }
      });
    }
  }

  function toRGB(code) {
    var hex = code.replace("#", "");
    if (hex.length === 3) {
      hex = hex.split("").map(function (ch) { return ch + ch; }).join("");
    }
    return [
      parseInt(hex.slice(0, 2), 16),
      parseInt(hex.slice(2, 4), 16),
      parseInt(hex.slice(4, 6), 16)
    ];
  }

  function toHex(rgb) {
    return "#" + rgb.map(function (value) {
      var hex = Math.max(0, Math.min(255, value)).toString(16);
      return hex.length === 1 ? "0" + hex : hex;
    }).join("");
  }

  function readableTextColor(background) {
    var channels = toRGB(background).map(function (channel) {
      channel = channel / 255;
      return channel <= 0.04045
        ? channel / 12.92
        : Math.pow((channel + 0.055) / 1.055, 2.4);
    });
    var luminance = (0.2126 * channels[0]) + (0.7152 * channels[1]) + (0.0722 * channels[2]);
    var lightContrast = 1.05 / (luminance + 0.05);
    var darkLuminance = 0.014443843596092545;
    var darkContrast = (luminance + 0.05) / (darkLuminance + 0.05);
    return lightContrast >= darkContrast ? "#ffffff" : "#202124";
  }

  function renderTagCloud(links, color) {
    var weights = links.map(function (link) {
      return parseFloat(link.getAttribute("rel")) || 0;
    }).sort(function (a, b) { return a - b; });

    var lowest = weights[0];
    var highest = weights[weights.length - 1];
    var range = highest - lowest || 1;
    var colorIncr = toRGB(color.end).map(function (n, i) {
      return (n - toRGB(color.start)[i]) / range;
    });

    links.forEach(function (link) {
      var weighting = (parseFloat(link.getAttribute("rel")) || 0) - lowest;
      var background = toHex(toRGB(color.start).map(function (n, i) {
        return Math.round(n + (colorIncr[i] * weighting));
      }));
      link.style.backgroundColor = background;
      link.style.color = readableTextColor(background);
    });
  }

  function initTagCloud() {
    var cloud = document.getElementById("tag_cloud");
    if (!cloud) {
      return;
    }

    var links = Array.prototype.slice.call(cloud.querySelectorAll("a"));
    if (!links.length) {
      return;
    }

    var scheme = window.matchMedia("(prefers-color-scheme: dark)");

    function paint() {
      renderTagCloud(links, scheme.matches
        ? { start: "#4a416f", end: "#00677d" }
        : { start: "#bbbbee", end: "#0085a1" });
    }

    paint();
    if (scheme.addEventListener) {
      scheme.addEventListener("change", paint);
    } else if (scheme.addListener) {
      scheme.addListener(paint);
    }
  }

  onReady(function () {
    wrapTables();
    wrapEmbeds();
    initNavbarScroll();
    initCatalog();
    initTagCloud();
  });
})();
