import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard({ account, balance }) {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      {account ? (
        <div>
          <p>Connected Account: {account}</p>
          <p>Current Balance: {balance} ETH</p>
        </div>
      ) : (
        <p>Please connect your wallet to view account details.</p>
      )}
      <div className="dashboard-buttons">
        <Link to="/blockchain" className="button">View Blockchain</Link>
        <Link to="/transaction" className="button">New Transaction</Link>
        <Link to="/mine" className="button">Mine</Link>
      </div>
    </div>
  );
}

export default Dashboard;