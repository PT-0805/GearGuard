import React, { useState } from 'react';

const Auth = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    retype_password: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Client-side validation for signup
    if (!isLogin && formData.password !== formData.retype_password) {
      alert("Passwords do not match!");
      return;
    }

    const endpoint = isLogin ? '/login' : '/signup';
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formData),
        credentials: 'include', // Handshake for Flask Sessions
      });

      const result = await response.json();

      if (response.ok) {
        if (isLogin) {
          // Tell App.jsx we are logged in and pass the username
          onLoginSuccess(result.user || "User");
        } else {
          alert("Account created! Please log in.");
          setIsLogin(true);
        }
      } else {
        alert(result.error || "Authentication failed");
      }
    } catch (err) {
      console.error("Auth Error:", err);
      alert("Connection failed. Make sure Flask is running on port 5000.");
    }
  };

  const styles = {
    container: {
      height: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)',
      fontFamily: "'Inter', sans-serif"
    },
    card: {
      background: 'rgba(255, 255, 255, 0.08)',
      backdropFilter: 'blur(12px)',
      padding: '40px',
      borderRadius: '20px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
      width: '100%',
      maxWidth: '400px',
      color: '#fff'
    },
    title: {
      textAlign: 'center',
      fontSize: '28px',
      fontWeight: '800',
      marginBottom: '10px',
      letterSpacing: '-0.5px'
    },
    subtitle: {
      textAlign: 'center',
      color: '#aaa',
      fontSize: '14px',
      marginBottom: '30px'
    },
    input: {
      width: '100%',
      padding: '14px',
      margin: '10px 0',
      borderRadius: '8px',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.1)',
      color: '#fff',
      fontSize: '15px',
      outline: 'none',
      boxSizing: 'border-box',
      transition: '0.3s'
    },
    button: {
      width: '100%',
      padding: '14px',
      background: '#4ecca3',
      color: '#1a1a2e',
      border: 'none',
      borderRadius: '8px',
      fontSize: '16px',
      fontWeight: '700',
      cursor: 'pointer',
      marginTop: '20px',
      transition: 'transform 0.2s, background 0.2s'
    },
    toggle: {
      marginTop: '25px',
      textAlign: 'center',
      fontSize: '14px',
      color: '#ccc'
    },
    link: {
      color: '#4ecca3',
      fontWeight: 'bold',
      cursor: 'pointer',
      textDecoration: 'none'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.title}>{isLogin ? 'Welcome Back' : 'Get Started'}</div>
        <div style={styles.subtitle}>
          {isLogin ? 'Enter your credentials to access GearGuard' : 'Create an account to manage your equipment'}
        </div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              style={styles.input}
              required
            />
          )}
          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={formData.email}
            onChange={handleChange}
            style={styles.input}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            style={styles.input}
            required
          />
          {!isLogin && (
            <input
              type="password"
              name="retype_password"
              placeholder="Confirm Password"
              value={formData.retype_password}
              onChange={handleChange}
              style={styles.input}
              required
            />
          )}

          <button 
            type="submit" 
            style={styles.button}
            onMouseOver={(e) => e.target.style.background = '#45b393'}
            onMouseOut={(e) => e.target.style.background = '#4ecca3'}
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div style={styles.toggle}>
          {isLogin ? "New here? " : "Already have an account? "}
          <span 
            style={styles.link} 
            onClick={() => {
              setIsLogin(!isLogin);
              setFormData({name: '', email: '', password: '', retype_password: ''});
            }}
          >
            {isLogin ? 'Create Account' : 'Log In'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Auth;