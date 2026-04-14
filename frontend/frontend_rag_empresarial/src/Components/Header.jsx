export const Header = ({title, userName, userRole}) => {
    return (
        <header className="main-header">
            <h1>{title}</h1>
            <section className="user-info">
                <strong>{userName}</strong>
                <span>{userRole}</span>
            </section>
        </header>
    );
};