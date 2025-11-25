import React from "react";

const IntakePage: React.FC = () => {
  return (
    <div className="page-container">
      <h2>Intake</h2>
      <p>Upload resumes, sync ATS pipelines, and invite hiring teams.</p>
      <div className="card">
        <h3>Upload Candidates</h3>
        <p>Drag & drop CSV, PDF, or sync directly from ATS.</p>
        <button className="primary-btn">Select Files</button>
      </div>
    </div>
  );
};

export default IntakePage;
