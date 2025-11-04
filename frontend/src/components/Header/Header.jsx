import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
    return (
        <header className="header">
            <div className="logo">
                <Link to="/" className="logo-link">
                    Cosafe System
                </Link>
            </div>
        </header>
    );
};

export default Header;
