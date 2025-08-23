// Placeholder analytics loader. Will inject GA tag if ga_id is present in localStorage.
export function initAnalytics() {
  try {
    const gaId = localStorage.getItem("ga_id");
    const enabled = localStorage.getItem("analytics_enabled") === "true";
    if (!enabled || !gaId || document.getElementById("ga-script")) return;
    const s1 = document.createElement("script");
    s1.async = true;
    s1.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`;
    s1.id = "ga-script";
    document.head.appendChild(s1);
    const s2 = document.createElement("script");
    s2.innerHTML = `window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', '${gaId}');`;
    document.head.appendChild(s2);
  } catch (e) {
    // silently ignore
  }
}