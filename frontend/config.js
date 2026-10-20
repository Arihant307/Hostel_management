/*
 * Frontend configuration + small shared helpers.
 * Every page that talks to the backend must load this file BEFORE its own
 * script:   <script src="../config.js"></script>
 *
 * API base URL
 * ------------
 * - Deployed on Render as one service (Flask serves these files): leave
 *   CONFIGURED_API_BASE_URL empty. Requests go to the same origin.
 * - Frontend hosted separately (e.g. a Render Static Site): set it to the
 *   backend URL, e.g. "https://hostel-management.onrender.com". See README.
 * - Local development with VS Code Live Server (port 5500/5501) is detected
 *   automatically and points to the Flask server on port 5000.
 */
(function () {
    "use strict";

    var CONFIGURED_API_BASE_URL = "";

    function detectApiBaseUrl() {
        if (CONFIGURED_API_BASE_URL) {
            return CONFIGURED_API_BASE_URL.replace(/\/+$/, "");
        }
        var loc = window.location;
        if (loc.protocol === "file:") {
            return "http://127.0.0.1:5000";
        }
        if (loc.port === "5500" || loc.port === "5501") {
            // Live Server: keep the same hostname so the session cookie is same-site.
            return loc.protocol + "//" + loc.hostname + ":5000";
        }
        return ""; // same origin
    }

    var API_BASE_URL = detectApiBaseUrl();

    function apiUrl(path) {
        if (/^https?:\/\//i.test(path)) return path;
        return API_BASE_URL + (path.charAt(0) === "/" ? path : "/" + path);
    }

    // fetch() wrapper: prefixes the API base URL and always sends the session cookie.
    function apiFetch(path, options) {
        var opts = Object.assign({}, options || {});
        opts.credentials = "include";
        return fetch(apiUrl(path), opts);
    }

    // Read a JSON body safely (returns {} for empty / non-JSON responses).
    function readJson(response) {
        return response.text().then(function (body) {
            if (!body) return {};
            try { return JSON.parse(body); } catch (e) { return {}; }
        });
    }

    // Escape user-provided text before inserting it with innerHTML.
    function escapeHtml(value) {
        if (value === null || value === undefined) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    /*
     * Ask the backend who is logged in. Redirects to `loginPage` when nobody is
     * logged in or the role does not match. Resolves to the user object, or
     * null after redirecting. (The backend enforces permissions on every API
     * call regardless; this only improves the page experience.)
     */
    function requireRole(role, loginPage) {
        return apiFetch("/auth/me")
            .then(function (res) {
                if (!res.ok) throw new Error("not logged in");
                return res.json();
            })
            .then(function (me) {
                if (role && me.role !== role) {
                    alert("You do not have access to this page.");
                    window.location.href = loginPage;
                    return null;
                }
                return me;
            })
            .catch(function () {
                window.location.href = loginPage;
                return null;
            });
    }

    function logout(redirectTo) {
        return apiFetch("/auth/logout", { method: "POST" })
            .catch(function () { /* ignore network errors on logout */ })
            .then(function () {
                ["token", "userEmail", "userName", "studentLoggedIn"].forEach(function (key) {
                    try { localStorage.removeItem(key); } catch (e) { /* storage unavailable */ }
                });
                window.location.href = redirectTo;
            });
    }

    window.API_BASE_URL = API_BASE_URL;
    window.apiUrl = apiUrl;
    window.apiFetch = apiFetch;
    window.readJson = readJson;
    window.escapeHtml = escapeHtml;
    window.requireRole = requireRole;
    window.logout = logout;
})();
