export const Footer: React.FC = () => {
  const handleLicenseClick = () => {
    window.open('/LICENSE', '_blank');
  };

  return (
    <footer style={{
      padding: '12px 24px',
      background: '#ffffff',
      borderTop: '1px solid #e2e8f0',
      textAlign: 'center',
      fontSize: '13px',
      color: '#64748b',
      marginLeft: window.innerWidth <= 768 ? 0 : '260px',
    }}>
      <span>@2026 All rights reserved - Ashish Kumar Sankhua - </span>
      <a 
        href="/LICENSE"
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => {
          e.preventDefault();
          handleLicenseClick();
        }}
        style={{
          color: '#3b82f6',
          textDecoration: 'none',
          fontWeight: 500,
          cursor: 'pointer',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.textDecoration = 'underline';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.textDecoration = 'none';
        }}
      >
        Licence
      </a>
    </footer>
  );
};
