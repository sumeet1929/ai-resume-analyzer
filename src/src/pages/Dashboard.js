import React from "react";

function Dashboard() {
  return (
    <div className="dashboard">
      <h1>AI Resume Analyzer Dashboard</h1>

      <div className="card">
        <h3>Upload Resume</h3>
        <input type="file" />
        <button>Analyze</button>
      </div>

      <div className="card">
        <h3>Resume Score</h3>
        <p>Score will appear here</p>
      </div>

      <div className="card">
        <h3>Suggestions</h3>
        <p>AI suggestions will appear here</p>
      </div>
    </div>
  );
}

export default Dashboard;