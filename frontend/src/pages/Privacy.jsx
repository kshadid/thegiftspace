import React from "react";
import { Link } from "react-router-dom";

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-semibold">Privacy Policy</h1>
      <p className="text-muted-foreground mt-2">How we collect, use, and protect your information.</p>
      <div className="prose prose-neutral dark:prose-invert mt-6">
        <h2>Information We Collect</h2>
        <p>Account details (name, email), registry data (event details, funds), and contributions.</p>
        <h2>Use of Information</h2>
        <p>To provide and improve the service, and for analytics with your consent.</p>
        <h2>Data Sharing</h2>
        <p>We do not sell personal data. We may share with service providers (hosting, payments).</p>
        <h2>Data Retention</h2>
        <p>We retain your data as long as necessary to provide the service and comply with law.</p>
        <h2>Your Rights</h2>
        <p>You can request access, correction, or deletion subject to legal obligations.</p>
      </div>
      <Link to="/" className="inline-block mt-8 underline">Back to home</Link>
    </div>
  );
}