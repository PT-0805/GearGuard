import React, { useState } from 'react';

const Auth = () => {
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

    // Client-side check before sending
    if (!isLogin && formData.password !== formData.retype_password) {
      alert("Passwords do not match!");
      return;
    }

    // IMPORTANT: No http://localhost:5000 here! 
    // Vite proxy will handle /login and /signup automatically.
    const endpoint = isLogin ? '/login' : '/signup';
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formData),
        // credentials: 'include' is still needed to keep the Flask session cookie
        credentials: 'include', 
      });

      const result = await response.json();

      if (response.ok) {
        alert(isLogin ? "Welcome Back!" : "Account Created Successfully!");
        // Change this to wherever your dashboard route is
        window.location.href = '/equipment'; 
      } else {
        alert(result.error || result.message || "Authentication failed");
      }
    } catch (err) {
      console.error("Auth Error:", err);
      alert("Could not connect to the server. Check if Flask is running.");
    }
  };

  const styles = {
    container: {
      height: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    },
    card: {
      background: 'rgba(255, 255, 255, 0.05)',
      backdropFilter: 'blur(10px)',
      padding: '40px',
      borderRadius: '15px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      width: '100%',
      maxWidth: '380px',
      color: 'white'
    },
    input: {
      width: '100%',
      padding: '12px',
      margin: '10px 0',
      borderRadius: '5px',
      border: 'none',
      background: 'rgba(255, 255, 255, 0.1)',
      color: 'white',
      outline: 'none',
      boxSizing: 'border-box'
    },
    button: {
      width: '100%',
      padding: '12px',
      background: '#4ecca3',
      color: '#1a1a2e',
      border: 'none',
      borderRadius: '5px',
      fontSize: '16px',
      fontWeight: 'bold',
      cursor: 'pointer',
      marginTop: '20px'
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={{ textAlign: 'center', marginBottom: '10px' }}>{isLogin ? 'Login' : 'Sign Up'}</h2>
        <p style={{ textAlign: 'center', fontSize: '14px', color: '#bbb', marginBottom: '20px' }}>
          Inventory Management System
        </p>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input type="text" name="name" placeholder="Full Name" value={formData.name} onChange={handleChange} style={styles.input} required />
          )}
          <input type="email" name="email" placeholder="Email Address" value={formData.email} onChange={handleChange} style={styles.input} required />
          <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} style={styles.input} required />
          {!isLogin && (
            <input type="password" name="retype_password" placeholder="Confirm Password" value={formData.retype_password} onChange={handleChange} style={styles.input} required />
          )}
          <button type="submit" style={styles.button}>
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px' }}>
          {isLogin ? "Need an account?" : "Already have an account?"}{' '}
          <span style={{ color: '#4ecca3', cursor: 'pointer' }} onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? 'Register' : 'Login'}
          </span>
        </p>
      </div>
    </div>
  );
};

export default Auth;