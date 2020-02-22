/*! pygal.js           2015-10-30 */
(function() {
    var a, b, c, d, e, f, g, h, i, j, k;
    i = "http://www.w3.org/2000/svg",
    k = "http://www.w3.org/1999/xlink",
    a = function(a, b) {
        return null == b && (b = null),
        b = b || document,
        Array.prototype.slice.call(b.querySelectorAll(a), 0).filter(function(a) {
            return a !== b
        })
    }
    ,
    e = function(a, b) {
        return (a.matches || a.matchesSelector || a.msMatchesSelector || a.mozMatchesSelector || a.webkitMatchesSelector || a.oMatchesSelector).call(a, b)
    }
    ,
    h = function(a, b) {
        return null == b && (b = null),
        Array.prototype.filter.call(a.parentElement.children, function(c) {
            return c !== a && (!b || e(c, b))
        })
    }
    ,
    Array.prototype.one = function() {
        return this.length > 0 && this[0] || {}
    }
    ,
    f = 5,
    j = null,
    g = /translate\((\d+)[ ,]+(\d+)\)/,
    b = function(a) {
        return (g.exec(a.getAttribute("transform")) || []).slice(1).map(function(a) {
            return +a
        })
    }
    ,
    c = function(c) {
        var d, g, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, A, B, C, D, E, F, G, H;
        for (a("svg", c).length ? (o = a("svg", c).one(),
        q = o.parentElement,
        g = o.viewBox.baseVal,
        d = q.getBBox(),
        w = function(a) {
            return (a - g.x) / g.width * d.width
        }
        ,
        x = function(a) {
            return (a - g.y) / g.height * d.height
        }
        ) : w = x = function(a) {
            return a
        }
        ,
        null != (null != (E = window.pygal) ? E.config : void 0) ? null != window.pygal.config.no_prefix ? l = window.pygal.config : (u = c.id.replace("chart-", ""),
        l = window.pygal.config[u]) : l = window.config,
        s = null,
        n = a(".graph").one(),
        t = a(".tooltip", c).one(),
        F = a(".reactive", c),
        y = 0,
        B = F.length; B > y; y++)
            m = F[y],
            m.addEventListener("mouseenter", function(a) {
                return function() {
                    return a.classList.add("active")
                }
            }(m)),
            m.addEventListener("mouseleave", function(a) {
                return function() {
                    return a.classList.remove("active")
                }
            }(m));
        for (G = a(".activate-serie", c),
        z = 0,
        C = G.length; C > z; z++)
            m = G[z],
            p = m.id.replace("activate-serie-", ""),
            m.addEventListener("mouseenter", function(b) {
                return function() {
                    var d, e, f, g, h, i, j, k;
                    for (i = a(".serie-" + b + " .reactive", c),
                    e = 0,
                    g = i.length; g > e; e++)
                        d = i[e],
                        d.classList.add("active");
                    for (j = a(".serie-" + b + " .showable", c),
                    k = [],
                    f = 0,
                    h = j.length; h > f; f++)
                        d = j[f],
                        k.push(d.classList.add("shown"));
                    return k
                }
            }(p)),
            m.addEventListener("mouseleave", function(b) {
                return function() {
                    var d, e, f, g, h, i, j, k;
                    for (i = a(".serie-" + b + " .reactive", c),
                    e = 0,
                    g = i.length; g > e; e++)
                        d = i[e],
                        d.classList.remove("active");
                    for (j = a(".serie-" + b + " .showable", c),
                    k = [],
                    f = 0,
                    h = j.length; h > f; f++)
                        d = j[f],
                        k.push(d.classList.remove("shown"));
                    return k
                }
            }(p)),
            m.addEventListener("click", function(b, d) {
                return function() {
                    var e, f, g, h, i, j, k, l, m, n, o;
                    for (g = a("rect", b).one(),
                    h = "" !== g.style.fill,
                    g.style.fill = h ? "" : "transparent",
                    m = a(".serie-" + d + " .reactive", c),
                    i = 0,
                    k = m.length; k > i; i++)
                        f = m[i],
                        f.style.display = h ? "" : "none";
                    for (n = a(".text-overlay .serie-" + d, c),
                    o = [],
                    j = 0,
                    l = n.length; l > j; j++)
                        e = n[j],
                        o.push(e.style.display = h ? "" : "none");
                    return o
                }
            }(m, p));
        for (H = a(".tooltip-trigger", c),
        A = 0,
        D = H.length; D > A; A++)
            m = H[A],
            m.addEventListener("mouseenter", function(a) {
                return function() {
                    return s = r(a)
                }
            }(m));
        return t.addEventListener("mouseenter", function() {
            return null != s ? s.classList.add("active") : void 0
        }),
        t.addEventListener("mouseleave", function() {
            return null != s ? s.classList.remove("active") : void 0
        }),
        c.addEventListener("mouseleave", function() {
            return j && clearTimeout(j),
            v(0)
        }),
        n.addEventListener("mousemove", function(a) {
            return !j && e(a.target, ".background") ? v(1e3) : void 0
        }),
        r = function(c) {
            var d, e, g, m, n, o, p, r, s, u, v, y, z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, $, _;
            for (clearTimeout(j),
            j = null,
            t.style.opacity = 1,
            t.style.display = "",
            G = a("g.text", t).one(),
            C = a("rect", t).one(),
            G.innerHTML = "",
            v = h(c, ".label").one().textContent,
            N = h(c, ".x_label").one().textContent,
            J = h(c, ".value").one().textContent,
            O = h(c, ".xlink").one().textContent,
            D = null,
            q = c,
            I = []; q && (I.push(q),
            !q.classList.contains("series")); )
                q = q.parentElement;
            if (q)
                for (X = q.classList,
                R = 0,
                S = X.length; S > R; R++)
                    if (g = X[R],
                    0 === g.indexOf("serie-")) {
                        D = +g.replace("serie-", "");
                        break
                    }
            for (y = null,
            null !== D && (y = l.legends[D]),
            o = 0,
            u = [[v, "label"]],
            Y = J.split("\n"),
            r = V = 0,
            T = Y.length; T > V; r = ++V)
                E = Y[r],
                u.push([E, "value-" + r]);
            for (l.tooltip_fancy_mode && (u.push([O, "xlink"]),
            u.unshift([N, "x_label"]),
            u.unshift([y, "legend"])),
            H = {},
            W = 0,
            U = u.length; U > W; W++)
                Z = u[W],
                s = Z[0],
                z = Z[1],
                s && (F = document.createElementNS(i, "text"),
                F.textContent = s,
                F.setAttribute("x", f),
                F.setAttribute("dy", o),
                F.classList.add(0 === z.indexOf("value") ? "value" : z),
                0 === z.indexOf("value") && l.tooltip_fancy_mode && F.classList.add("color-" + D),
                "xlink" === z ? (d = document.createElementNS(i, "a"),
                d.setAttributeNS(k, "href", s),
                d.textContent = void 0,
                d.appendChild(F),
                F.textContent = "Link >",
                G.appendChild(d)) : G.appendChild(F),
                o += F.getBBox().height + f / 2,
                e = f,
                void 0 !== F.style.dominantBaseline ? F.style.dominantBaseline = "text-before-edge" : e += .8 * F.getBBox().height,
                F.setAttribute("y", e),
                H[z] = F);
            return K = G.getBBox().width + 2 * f,
            p = G.getBBox().height + 2 * f,
            C.setAttribute("width", K),
            C.setAttribute("height", p),
            H.value && H.value.setAttribute("dx", (K - H.value.getBBox().width) / 2 - f),
            H.x_label && H.x_label.setAttribute("dx", K - H.x_label.getBBox().width - 2 * f),
            H.xlink && H.xlink.setAttribute("dx", K - H.xlink.getBBox().width - 2 * f),
            M = h(c, ".x").one(),
            Q = h(c, ".y").one(),
            L = parseInt(M.textContent),
            M.classList.contains("centered") ? L -= K / 2 : M.classList.contains("left") ? L -= K : M.classList.contains("auto") && (L = w(c.getBBox().x + c.getBBox().width / 2) - K / 2),
            P = parseInt(Q.textContent),
            Q.classList.contains("centered") ? P -= p / 2 : Q.classList.contains("top") ? P -= p : Q.classList.contains("auto") && (P = x(c.getBBox().y + c.getBBox().height / 2) - p / 2),
            $ = b(t.parentElement),
            A = $[0],
            B = $[1],
            L + K + A > l.width && (L = l.width - K - A),
            P + p + B > l.height && (P = l.height - p - B),
            0 > L + A && (L = -A),
            0 > P + B && (P = -B),
            _ = b(t),
            m = _[0],
            n = _[1],
            m === L && n === P ? c : (t.setAttribute("transform", "translate(" + L + " " + P + ")"),
            c)
        }
        ,
        v = function(a) {
            return j = setTimeout(function() {
                return t.style.display = "none",
                t.style.opacity = 0,
                null != s && s.classList.remove("active"),
                j = null
            }, a)
        }
    }
    ,
    d = function() {
        var b, d, e, f, g;
        if (d = a(".pygal-chart"),
        d.length) {
            for (g = [],
            e = 0,
            f = d.length; f > e; e++)
                b = d[e],
                g.push(c(b));
            return g
        }
    }
    ,
    "loading" !== document.readyState ? d() : document.addEventListener("DOMContentLoaded", function() {
        return d()
    }),
    window.pygal = window.pygal || {},
    window.pygal.init = c,
    window.pygal.init_svg = d
}
).call(this);


window.pygal = window.pygal || {};
window.pygal.config = window.pygal.config || {};
window.pygal.config['627efa6d-bd6c-4a0b-a693-dd3e40ead6d7'] = {
 "allow_interruptions": false,
 "box_mode": "extremes",
 "classes": ["pygal-chart"],
 "css": ["file://style.css", "file://graph.css"],
 "defs": [],
 "disable_xml_declaration": false,
 "dots_size": 2.5,
 "dynamic_print_values": false,
 "explicit_size": false,
 "fill": false,
 "force_uri_protocol": "https",
 "formatter": null,
 "half_pie": false,
 "height": 600,
 "include_x_axis": false,
 "inner_radius": 0,
 "interpolate": null,
 "interpolation_parameters": {},
 "interpolation_precision": 250,
 "inverse_y_axis": false,
 "js": ["//kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js"],
 "legend_at_bottom": false,
 "legend_at_bottom_columns": null,
 "legend_box_size": 12,
 "logarithmic": false,
 "margin": 20,
 "margin_bottom": null,
 "margin_left": null,
 "margin_right": null,
 "margin_top": null,
 "max_scale": 16,
 "min_scale": 4,
 "missing_value_fill_truncation": "x",
 "no_data_text": "No data",
 "no_prefix": false,
 "order_min": null,
 "pretty_print": false,
 "print_labels": false,
 "print_values": false,
 "print_values_position": "center",
 "print_zeroes": true,
 "range": null,
 "rounded_bars": null,
 "secondary_range": null,
 "show_dots": true,
 "show_legend": true,
 "show_minor_x_labels": true,
 "show_minor_y_labels": true,
 "show_only_major_dots": false,
 "show_x_guides": false,
 "show_x_labels": true,
 "show_y_guides": true,
 "show_y_labels": true,
 "spacing": 10,
 "stack_from_top": false,
 "strict": false,
 "stroke": true,
 "stroke_style": null,
 "style": {
   "background": "rgba(249, 249, 249, 1)",
   "ci_colors": [],
   "colors": ["#F44336", "#3F51B5", "#009688", "#FFC107", "#FF5722", "#9C27B0", "#03A9F4", "#8BC34A", "#FF9800", "#E91E63", "#2196F3", "#4CAF50", "#FFEB3B", "#673AB7", "#00BCD4", "#CDDC39", "#9E9E9E", "#607D8B"],
   "font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "foreground": "rgba(0, 0, 0, .87)",
   "foreground_strong": "rgba(0, 0, 0, 1)",
   "foreground_subtle": "rgba(0, 0, 0, .54)",
   "guide_stroke_dasharray": "4,4",
   "label_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "label_font_size": 10,
   "legend_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "legend_font_size": 14,
   "major_guide_stroke_dasharray": "6,6",
   "major_label_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "major_label_font_size": 10,
   "no_data_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "no_data_font_size": 64,
   "opacity": ".7",
   "opacity_hover": ".8",
   "plot_background": "rgba(255, 255, 255, 1)",
   "stroke_opacity": ".8",
   "stroke_opacity_hover": ".9",
   "title_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "title_font_size": 16,
   "tooltip_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "tooltip_font_size": 14,
   "transition": "150ms",
   "value_background": "rgba(229, 229, 229, 1)",
   "value_colors": [],
   "value_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "value_font_size": 16,
   "value_label_font_family": "Consolas, \"Liberation Mono\", Menlo, Courier, monospace",
   "value_label_font_size": 10
 },
 "title": "Results of rolling one D6 100000 times.",
 "tooltip_border_radius": 0,
 "tooltip_fancy_mode": true,
 "truncate_label": null,
 "truncate_legend": null,
 "width": 800,
 "x_label_rotation": 0,
 "x_labels": ["", "2\u70b9", "3\u70b9", "4\u70b9", "5\u70b9", "6\u70b9", "7\u70b9", "8\u70b9", "9\u70b9", "10\u70b9", "11\u70b9", "12\u70b9"],
 "x_labels_major": null,
 "x_labels_major_count": null,
 "x_labels_major_every": null,
 "x_title": "Result",
 "xrange": null,
 "y_label_rotation": 0,
 "y_labels": null,
 "y_labels_major": null,
 "y_labels_major_count": null,
 "y_labels_major_every": null,
 "y_title": "Frequency of Result",
 "zero": 0,
 "legends": ["D6+D6"]
}