import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import jsPDF from "jspdf";
import "./Dashboard.css";

function Dashboard() {

  const [email, setEmail] = useState("");
  const [file, setFile] = useState(null);
  const [data, setData] = useState({});

  // JOB MATCH
  const [job, setJob] = useState("");
  const [match, setMatch] = useState({});

  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/");
      return;
    }

    fetch("http://localhost:5000/profile", {
      headers: { Authorization: token },
    })
      .then(res => res.json())
      .then(d => {
        if (d.email) setEmail(d.email);
        else navigate("/");
      });
  }, [navigate]);

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("resume", file);

    const res = await fetch("http://localhost:5000/analyze", {
      method: "POST",
      body: formData,
    });

    const result = await res.json();
    setData(result);
  };

  // AI REWRITE
  const rewriteSummary = async () => {
    const res = await fetch("http://localhost:5000/rewrite", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();

    setData({
      ...data,
      summary: result.summary
    });
  };

  // JOB MATCH ANALYZER
  const analyzeJob = async () => {
    const res = await fetch("http://localhost:5000/job-match", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        skills: data.skills,
        job: job
      })
    });

    const result = await res.json();
    setMatch(result);
  };

  // DOWNLOAD PDF
  const downloadPDF = () => {
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text("AI Resume Analysis Report", 20, 20);

    doc.setFontSize(12);

    doc.text(`Name: ${data.name || ""}`, 20, 40);
    doc.text(`ATS Score: ${data.score || ""}`, 20, 50);
    doc.text(`Experience: ${data.experience || ""}`, 20, 60);
    doc.text(`Education: ${data.education || ""}`, 20, 70);

    doc.text("Skills:", 20, 90);
    doc.text((data.skills || []).join(", "), 20, 100);

    doc.text("AI Summary:", 20, 120);
    doc.text(data.summary || "", 20, 130, { maxWidth: 170 });

    doc.save("AI_Resume_Report.pdf");
  };

  return (
    <div className="dashboard">

      {/* HEADER */}
      <div className="header">
        <div>
          <h1>AI Resume Analyzer</h1>
          <p>ATS Intelligence Dashboard</p>
        </div>

        <div className="user">
          <span>{email}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </div>

      {/* UPLOAD */}
      <div className="upload">
        <input
          type="file"
          onChange={(e)=>setFile(e.target.files[0])}
        />

        <button onClick={handleUpload}>
          Analyze Resume
        </button>

        <button className="download" onClick={downloadPDF}>
          Download Report PDF
        </button>
      </div>

      <div className="grid">

        {/* ATS SCORE */}
        <div className="card ats">
          <h3>ATS Score</h3>

          <div className="circle">
            <svg width="150" height="150">

              <circle
                cx="75"
                cy="75"
                r="60"
                className="bg"
              />

              <circle
                cx="75"
                cy="75"
                r="60"
                className="progress"
                style={{
                  strokeDashoffset:
                    377 - (377 * parseInt(data.score || 0)) / 100
                }}
              />

            </svg>

            <div className="number">
              {data.score || "0%"}
            </div>
          </div>

          <p>{data.experience}</p>
        </div>

        {/* SKILLS */}
        <div className="card">
          <h3>Skills</h3>
          {data.skills?.map((s,i)=>(
            <div key={i}>{s}</div>
          ))}
        </div>

        {/* STRENGTHS */}
        <div className="card">
          <h3>Strengths</h3>
          <ul>
            {data.strengths?.map((s,i)=>(
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>

        {/* RECOMMENDATIONS */}
        <div className="card">
          <h3>Recommendations</h3>
          <ul>
            {data.recommendations?.map((s,i)=>(
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>

        {/* TIPS */}
        <div className="card">
          <h3>Tips</h3>
          <ul>
            {data.tips?.map((s,i)=>(
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>

        {/* AI SUMMARY */}
        <div className="card summary">
          <h3>AI Resume Summary</h3>
          <p>{data.summary}</p>

          <button
            className="rewrite"
            onClick={rewriteSummary}
          >
            ✨ AI Improve Resume
          </button>
        </div>

        {/* JOB MATCH ANALYZER */}
        <div className="card summary">
          <h3>Job Description Match</h3>

          <textarea
            placeholder="Paste Job Description here..."
            value={job}
            onChange={(e)=>setJob(e.target.value)}
          />

          <button
            className="rewrite"
            onClick={analyzeJob}
          >
            Analyze Job Match
          </button>

          {match.match && (
            <>
              <h4>Match Score: {match.match}</h4>

              <p><b>Matched Skills:</b></p>
              <ul>
                {match.matched?.map((s,i)=>(
                  <li key={i}>{s}</li>
                ))}
              </ul>

              <p><b>Missing Skills:</b></p>
              <ul>
                {match.missing?.map((s,i)=>(
                  <li key={i}>{s}</li>
                ))}
              </ul>

              <p><b>Suggestions:</b></p>
              <ul>
                {match.suggestions?.map((s,i)=>(
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </>
          )}

        </div>

      </div>

    </div>
  );
}

export default Dashboard;