import React, { useState } from 'react';
import Auth from './Auth';
import Navbar from './Navbar';
import Dashboard from './Dashboard';

function App() {
  const [user, setUser] = useState(null);
  const [activePage, setActivePage] = useState('dashboard');

  if (!user) {
    return <Auth onLoginSuccess={(userName) => setUser(userName)} />;
  }

  return (
    <div style={{ backgroundColor: '#f8f9fa', minHeight: '100vh' }}>
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      
      <main>
        {activePage === 'dashboard' && <Dashboard user={user} />}
        {activePage === 'equipment' && <h1 style={{padding: '40px'}}>Equipment Page (Coming Next)</h1>}
      </main>
    </div>
  );
}

export default App;