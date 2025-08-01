const Footer = () => {
  return (
    <footer className="modern-footer">
      <div className="footer-content">
        <div className="footer-section company-info">
          <h4>CreditRisk AI</h4>
          <p>Advanced ML-powered credit risk assessment platform with comprehensive data integration and real-time analytics.</p>
          <div className="social-links">
            <a href="#" aria-label="LinkedIn">💼</a>
            <a href="#" aria-label="Twitter">🐦</a>
            <a href="#" aria-label="GitHub">🔗</a>
          </div>
        </div>

        <div className="footer-section">
          <h4>Product</h4>
          <ul>
            <li><a href="#risk-assessment">Risk Assessment</a></li>
            <li><a href="#data-integration">Data Integration</a></li>
            <li><a href="#ml-models">ML Models</a></li>
            <li><a href="#analytics">Analytics</a></li>
            <li><a href="#api">API Access</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Data Sources</h4>
          <ul>
            <li><a href="#account-aggregator">Account Aggregator</a></li>
            <li><a href="#device-analytics">Device Analytics</a></li>
            <li><a href="#location-intel">Location Intelligence</a></li>
            <li><a href="#utility-data">Utility Data</a></li>
            <li><a href="#digital-footprint">Digital Footprint</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li><a href="#documentation">Documentation</a></li>
            <li><a href="#api-reference">API Reference</a></li>
            <li><a href="#tutorials">Tutorials</a></li>
            <li><a href="#support">Support</a></li>
            <li><a href="#status">System Status</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Security & Compliance</h4>
          <ul>
            <li><a href="#privacy">Privacy Policy</a></li>
            <li><a href="#terms">Terms of Service</a></li>
            <li><a href="#gdpr">GDPR Compliance</a></li>
            <li><a href="#security">Security</a></li>
            <li><a href="#certifications">Certifications</a></li>
          </ul>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-bottom-content">
          <div className="copyright">
            <p>&copy; 2024 CreditRisk AI. All rights reserved.</p>
            <p>Built with React, FastAPI, XGBoost & LightGBM</p>
          </div>
          
          <div className="footer-badges">
            <span className="badge">🔒 SOC 2 Compliant</span>
            <span className="badge">🛡️ ISO 27001</span>
            <span className="badge">✅ GDPR Ready</span>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
