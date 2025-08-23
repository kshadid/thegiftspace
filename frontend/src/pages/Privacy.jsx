import React from 'react';
import Footer from '../components/layout/Footer';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-gray-600">Last updated: {new Date().toLocaleDateString()}</p>
          <div className="mt-6">
            <a href="/" className="text-rose-600 hover:text-rose-700 font-medium">
              ← Back to The giftspace
            </a>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-8 space-y-8">
          
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-gray-700 leading-relaxed">
              The giftspace ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains 
              how we collect, use, disclose, and safeguard your information when you use our wedding registry service 
              ("Service"). Please read this privacy policy carefully.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-3">Personal Information</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              We collect information that you provide directly to us, including:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Name and email address when you create an account</li>
              <li>Wedding details (couple names, event date, location)</li>
              <li>Registry information (fund descriptions, goals, images)</li>
              <li>Contribution details when you make or receive gifts</li>
              <li>Messages and communications through our Service</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Usage Information</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              We automatically collect certain information about your device and usage of our Service:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>IP address and browser type</li>
              <li>Device information and operating system</li>
              <li>Pages visited and time spent on our Service</li>
              <li>Referring website addresses</li>
              <li>Search terms and interactions with our features</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We use the information we collect to:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Provide, maintain, and improve our Service</li>
              <li>Process transactions and send related information</li>
              <li>Send you technical notices, updates, and support messages</li>
              <li>Respond to your comments, questions, and customer service requests</li>
              <li>Send you promotional communications about new features or services</li>
              <li>Monitor and analyze trends and usage patterns</li>
              <li>Detect, investigate, and prevent fraudulent transactions</li>
              <li>Comply with legal obligations and protect our rights</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Email Communications</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We use email to enhance your experience with our Service:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li><strong>Transaction Emails:</strong> We send receipts to guests who make contributions</li>
              <li><strong>Notification Emails:</strong> Registry owners receive notifications about new contributions</li>
              <li><strong>Account Emails:</strong> We send account-related updates and security notifications</li>
              <li><strong>Marketing Emails:</strong> We may send promotional emails (you can opt-out anytime)</li>
            </ul>
            <p className="text-gray-700 leading-relaxed">
              You can unsubscribe from marketing emails by clicking the unsubscribe link in any email or by contacting us directly.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Information Sharing and Disclosure</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We do not sell, trade, or otherwise transfer your personal information to third parties except as described below:
            </p>
            
            <h3 className="text-xl font-semibold text-gray-800 mb-3">With Your Consent</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              We share information when you have given us explicit consent to do so.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Service Providers</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              We work with third-party service providers who help us operate our Service:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Email service providers (for sending notifications and receipts)</li>
              <li>Cloud hosting and storage services</li>
              <li>Analytics and monitoring services</li>
              <li>Payment processors (when integrated)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Legal Requirements</h3>
            <p className="text-gray-700 leading-relaxed">
              We may disclose your information if required to do so by law or in response to valid requests by public authorities.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Data Security</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We implement appropriate technical and organizational measures to protect your personal information:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Encryption of data in transit and at rest</li>
              <li>Secure authentication and access controls</li>
              <li>Regular security assessments and updates</li>
              <li>Limited access to personal information on a need-to-know basis</li>
              <li>Employee training on data protection practices</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Retention</h2>
            <p className="text-gray-700 leading-relaxed">
              We retain your personal information for as long as necessary to provide our Service and fulfill the purposes 
              outlined in this Privacy Policy. We may retain certain information for longer periods as required by law, 
              to resolve disputes, or to enforce our agreements.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Your Rights and Choices</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              You have certain rights regarding your personal information:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li><strong>Access:</strong> Request access to your personal information</li>
              <li><strong>Correction:</strong> Request correction of inaccurate information</li>
              <li><strong>Deletion:</strong> Request deletion of your personal information</li>
              <li><strong>Portability:</strong> Request a copy of your data in a portable format</li>
              <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Cookies and Tracking Technologies</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              We use cookies and similar technologies to:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Remember your preferences and settings</li>
              <li>Provide personalized content and features</li>
              <li>Analyze how our Service is used</li>
              <li>Improve our Service performance</li>
            </ul>
            <p className="text-gray-700 leading-relaxed">
              You can control cookies through your browser settings, but some features of our Service may not function properly if you disable cookies.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. International Data Transfers</h2>
            <p className="text-gray-700 leading-relaxed">
              Your information may be transferred to and processed in countries other than your own. We ensure that such 
              transfers comply with applicable data protection laws and implement appropriate safeguards to protect your information.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Children's Privacy</h2>
            <p className="text-gray-700 leading-relaxed">
              Our Service is not directed to children under the age of 13. We do not knowingly collect personal information 
              from children under 13. If we learn that we have collected personal information from a child under 13, we will 
              delete that information as quickly as possible.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Changes to This Privacy Policy</h2>
            <p className="text-gray-700 leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new 
              Privacy Policy on this page and updating the effective date. You are advised to review this Privacy Policy 
              periodically for any changes.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Contact Information</h2>
            <p className="text-gray-700 leading-relaxed">
              If you have any questions about this Privacy Policy or our data practices, please contact us at:
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-700">
                <strong>The giftspace</strong><br />
                Email: privacy@thegiftspace.com<br />
                Support: support@thegiftspace.com<br />
                Website: https://thegiftspace.com
              </p>
            </div>
          </section>

        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} The giftspace. All rights reserved.</p>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}