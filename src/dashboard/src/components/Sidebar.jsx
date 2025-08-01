import { useState } from 'react'
import { useLocation, Link } from 'react-router-dom'

const Sidebar = ({ isOpen }) => {
  const location = useLocation()
  const [expandedMenu, setExpandedMenu] = useState(null)

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      path: '/dashboard',
      active: location.pathname === '/dashboard' || location.pathname === '/'
    },
    {
      id: 'assessment',
      label: 'Risk Assessment',
      icon: '🎯',
      submenu: [
        { label: 'New Application', path: '/assessment/new', icon: '📝' },
        { label: 'Batch Processing', path: '/assessment/batch', icon: '📋' },
        { label: 'Quick Score', path: '/assessment/quick', icon: '⚡' }
      ]
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: '📈',
      submenu: [
        { label: 'Risk Trends', path: '/analytics/trends', icon: '📊' },
        { label: 'Model Performance', path: '/analytics/models', icon: '🤖' },
        { label: 'Portfolio Analysis', path: '/analytics/portfolio', icon: '💼' }
      ]
    },
    {
      id: 'data',
      label: 'Data Sources',
      icon: '🔗',
      submenu: [
        { label: 'Account Aggregator', path: '/data/aa', icon: '🏦' },
        { label: 'Device Analytics', path: '/data/device', icon: '📱' },
        { label: 'Location Intelligence', path: '/data/location', icon: '🌍' },
        { label: 'Utility Data', path: '/data/utility', icon: '⚡' }
      ]
    },
    {
      id: 'models',
      label: 'ML Models',
      icon: '🧠',
      submenu: [
        { label: 'Model Registry', path: '/models/registry', icon: '📚' },
        { label: 'Training', path: '/models/training', icon: '🎓' },
        { label: 'Monitoring', path: '/models/monitoring', icon: '👁️' }
      ]
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      path: '/settings'
    }
  ]

  const toggleSubmenu = (menuId) => {
    setExpandedMenu(expandedMenu === menuId ? null : menuId)
  }

  return (
    <aside className={`modern-sidebar ${isOpen ? 'open' : 'closed'}`}>
      <div className="sidebar-content">
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <div key={item.id} className="nav-item">
              {item.submenu ? (
                <>
                  <button
                    className={`nav-link has-submenu ${expandedMenu === item.id ? 'expanded' : ''}`}
                    onClick={() => toggleSubmenu(item.id)}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                    <span className="submenu-arrow">›</span>
                  </button>
                  
                  <div className={`submenu ${expandedMenu === item.id ? 'expanded' : ''}`}>
                    {item.submenu.map((subItem) => (
                      <Link
                        key={subItem.path}
                        to={subItem.path}
                        className="submenu-link"
                      >
                        <span className="submenu-icon">{subItem.icon}</span>
                        <span className="submenu-label">{subItem.label}</span>
                      </Link>
                    ))}
                  </div>
                </>
              ) : (
                <Link
                  to={item.path}
                  className={`nav-link ${item.active ? 'active' : ''}`}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                </Link>
              )}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="quick-stats">
            <div className="stat-item">
              <div className="stat-value">98.2%</div>
              <div className="stat-label">Model Accuracy</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">1,247</div>
              <div className="stat-label">Assessments Today</div>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
