import React, { useState, useEffect } from 'react';

export default function Anomalies({ anomalyType }) {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`http://ec2-18-232-133-253.compute-1.amazonaws.com:8120/anomalies?anomaly_type=${encodeURIComponent(anomalyType)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      setAnomalies(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, [anomalyType]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h2>Anomalies - {anomalyType}</h2>
      <table border="1" style={{ width: "100%", textAlign: "left" }}>
        <thead>
          <tr>
            <th>Event ID</th>
            <th>Trace ID</th>
            <th>Type</th>
            <th>Anomaly Type</th>
            <th>Description</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.map((anomaly, index) => (
            <tr key={index}>
              <td>{anomaly.event_id}</td>
              <td>{anomaly.trace_id}</td>
              <td>{anomaly.event_type}</td>
              <td>{anomaly.anomaly_type}</td>
              <td>{anomaly.description}</td>
              <td>{new Date(anomaly.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
