import { useState } from 'react'

const Header = ({ onToggleSidebar, onToggleTheme, isDarkMode }) => {
  const [user] = useState({ name: 'Credit Analyst', avatar: '👤' })

  return (
    <header className="modern-header">
      <div className="header-left">
        <button 
          className="sidebar-toggle"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        >
          <span className="hamburger"></span>
          <span className="hamburger"></span>
          <span className="hamburger"></span>
        </button>
        
        <div className="logo-section">
          <div className="logo">🏦</div>
          <div className="brand-text">
            <h1>CreditRisk AI</h1>
            <span>Smart Risk Assessment</span>
          </div>
        </div>
      </div>

      <div className="header-center">
        <div className="search-container">
          <input 
            type="text" 
            placeholder="Search applications, customers..." 
            className="search-input"
          />
          <button className="search-btn">🔍</button>
        </div>
      </div>

      <div className="header-right">
        <div className="header-actions">
          <button 
            className="action-btn notification-btn"
            title="Notifications"
          >
            🔔
            <span className="notification-badge">3</span>
          </button>
          
          <button 
            className="action-btn theme-toggle"
            onClick={onToggleTheme}
            title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
          
          <div className="user-profile">
            <div className="user-avatar">{user.avatar}</div>
            <div className="user-info">
              <span className="user-name">{user.name}</span>
              <span className="user-role">Risk Analyst</span>
            </div>
            <div className="user-dropdown">▼</div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
