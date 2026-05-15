import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        🌾 Rice Leaf Classifier
      </Link>
      <div className="navbar-links">
        <Link to="/admin">Admin</Link>
      </div>
    </nav>
  );
}
