import React from "react";

const IntegrationsPage: React.FC = () => {
  return (
    <div className="page-container">
      <h2>ATS Integrations</h2>
      <p>Connect Greenhouse, Lever, Workday, or custom ATS APIs.</p>
      <div className="card">
        <h3>Integration Status</h3>
        <ul>
          <li>OpenRouter: Connected</li>
          <li>Deepgram: Pending</li>
          <li>Zoom: Connect now</li>
        </ul>
      </div>
    </div>
  );
};

export default IntegrationsPage;
