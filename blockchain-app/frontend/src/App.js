import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { ethers } from 'ethers';
import './App.css';
import Blockchain from './components/Blockchain';
import NewTransaction from './components/NewTransaction';
import Mine from './components/Mine';

function App() {
  const [account, setAccount] = useState(null);

  useEffect(() => {
    connectWallet();
  }, []);

  const connectWallet = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        await window.ethereum.request({ method: 'eth_requestAccounts' });
        const provider = new ethers.providers.Web3Provider(window.ethereum);
        const signer = provider.getSigner();
        const address = await signer.getAddress();
        setAccount(address);
      } catch (error) {
        console.error("Failed to connect to MetaMask", error);
      }
    } else {
      console.log('Please install MetaMask!');
    }
  };

  return (
    <Router>
      <div className="container">
        <header className="header">
          <h1>Blockchain App</h1>
        </header>
        <nav className="nav">
          <ul>
            <li><Link to="/">Blockchain</Link></li>
            <li><Link to="/transaction">New Transaction</Link></li>
            <li><Link to="/mine">Mine</Link></li>
          </ul>
        </nav>
        
        {account ? (
          <p className="account-info">Connected Account: {account}</p>
        ) : (
          <button className="button connect-button" onClick={connectWallet}>Connect MetaMask</button>
        )}

        <main>
          <Routes>
            <Route path="/" element={<Blockchain />} />
            <Route path="/transaction" element={<NewTransaction account={account} />} />
            <Route path="/mine" element={<Mine account={account} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;