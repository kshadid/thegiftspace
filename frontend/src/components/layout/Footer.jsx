import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t mt-12">
      <div className="max-w-6xl mx-auto px-4 py-8 text-sm flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="text-muted-foreground">© {new Date().getFullYear()} The giftspace</div>
        <nav className="flex items-center gap-4">
          <Link className="text-muted-foreground hover:text-foreground" to="/legal/terms">Terms</Link>
          <Link className="text-muted-foreground hover:text-foreground" to="/legal/privacy">Privacy</Link>
          <a className="text-muted-foreground hover:text-foreground" href="mailto:support@thegiftspace.com">Support</a>
        </nav>
      </div>
    </footer>
  );
}