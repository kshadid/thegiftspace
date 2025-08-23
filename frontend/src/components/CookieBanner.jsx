import React from "react";
import { Button } from "./ui/button";

// Banner only shows when analytics is enabled (localStorage.analytics_enabled === 'true') and no consent yet
export default function CookieBanner() {
  const [visible, setVisible] = React.useState(false);
  React.useEffect(() => {
    const enabled = localStorage.getItem("analytics_enabled") === "true";
    const consent = localStorage.getItem("cookie_consent");
    setVisible(enabled && !consent);
  }, []);

  if (!visible) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 z-50 bg-background/95 border-t backdrop-blur">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center gap-3 md:gap-6">
        <div className="text-sm text-muted-foreground">
          We use cookies for analytics to understand engagement. By clicking “Allow”, you consent to storing cookies on your device.
        </div>
        <div className="ml-auto flex gap-2">
          <Button variant="secondary" onClick={() => { localStorage.setItem("cookie_consent", "dismissed"); setVisible(false); }}>Dismiss</Button>
          <Button onClick={() => { localStorage.setItem("cookie_consent", "allowed"); setVisible(false); }}>Allow</Button>
        </div>
      </div>
    </div>
  );
}