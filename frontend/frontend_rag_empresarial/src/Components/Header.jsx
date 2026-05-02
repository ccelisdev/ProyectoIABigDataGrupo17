import logoutIcon from "../assets/cerrar-sesion.png";

export const Header = ({ title, userName, userRole, onLogout }) => {
    return (
        <header className="main-header">
            <h1>{title}</h1>
            
            <section className="user-area">
                <div className="user-details">
                    <strong className="user-details__name">{userName}</strong>
                    <span className="user-details__role">{userRole}</span>
                </div>
                
                <button 
                    className="action-logout" 
                    onClick={onLogout} 
                    title="Cerrar sesión"
                >
                    <img src={logoutIcon} alt="Logout" className="logout-img" />
                </button>
            </section>
        </header>
    );
};