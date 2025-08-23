import React from "react";
import { Link } from "react-router-dom";

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-3xl font-semibold">Terms & Conditions</h1>
      <p className="text-muted-foreground mt-2">These terms govern your use of the wedding registry service.</p>
      <div className="prose prose-neutral dark:prose-invert mt-6">
        <h2>1. Accounts</h2>
        <p>You are responsible for maintaining the confidentiality of your account credentials.</p>
        <h2>2. Content</h2>
        <p>You must have rights to images and content you upload. Do not upload illegal or harmful content.</p>
        <h2>3. Payments</h2>
        <p>Payment processing is handled by third-party providers (to be integrated). Terms may apply.</p>
        <h2>4. Limitation of Liability</h2>
        <p>This service is provided “as is”. We are not liable for indirect or consequential damages.</p>
        <h2>5. Changes</h2>
        <p>We may update these terms. Continued use constitutes acceptance of the updated terms.</p>
      </div>
      <Link to="/" className="inline-block mt-8 underline">Back to home</Link>
    </div>
  );
}