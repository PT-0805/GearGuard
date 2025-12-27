import React from 'react';

const Navbar = ({ activePage, setActivePage }) => {
  
  const handleLogout = async () => {
    try {
      await fetch('/logout', { method: 'POST', credentials: 'include' });
      window.location.href = '/'; // Go back to login
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'kanban', label: 'KanBan' },
    { id: 'calendar', label: 'Calendar' },
    { id: 'equipment', label: 'Equipment' },
    { id: 'teams', label: 'Teams' },
    { id: 'work_centers', label: 'Work Centers' },
  ];

  return (
    <nav style={styles.nav}>
      <div style={styles.brand}>GearGuard</div>
      <div style={styles.links}>
        {navItems.map((item) => (
          <span
            key={item.id}
            onClick={() => setActivePage(item.id)}
            style={{
              ...styles.link,
              ...(activePage === item.id ? styles.activeLink : {}),
            }}
          >
            {item.label}
          </span>
        ))}
      </div>
      <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
    </nav>
  );
};

const styles = {
  nav: {
    backgroundColor: '#111',
    color: '#fff',
    padding: '0 30px',
    height: '60px',
    display: 'flex',
    alignItems: 'center',
    boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
    fontFamily: 'Inter, sans-serif',
  },
  brand: {
    fontSize: '20px',
    fontWeight: '800',
    letterSpacing: '1px',
    marginRight: '50px',
    color: '#4ecca3',
  },
  links: {
    display: 'flex',
    gap: '25px',
  },
  link: {
    fontSize: '14px',
    color: '#999',
    cursor: 'pointer',
    transition: '0.2s',
    fontWeight: '500',
    paddingBottom: '5px',
  },
  activeLink: {
    color: '#fff',
    borderBottom: '2px solid #4ecca3',
  },
  logoutBtn: {
    marginLeft: 'auto',
    background: 'none',
    border: '1px solid #ff6b6b',
    color: '#ff6b6b',
    padding: '6px 15px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: '600',
  }
};

export default Navbar;