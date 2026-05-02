// Components/Login.jsx
import { useState } from 'react';

export const Login = ({ onLoginSuccess }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLogging, setIsLogging] = useState(false);

    // Login como empleado
    const handleLogin = (e) => {
        e.preventDefault();
        setIsLogging(true);
        // Simulación de Login Real
        setTimeout(() => {
            if (username === "admin" && password === "123") {
                onLoginSuccess({ user_name: "Admin", role: "Jefe", token: "mock-token" });
            } else {
                alert("Credenciales incorrectas");
                setIsLogging(false);
            }
        }, 1000);
    };

    // Login inmediato como invitado
    const handleGuest = () => {
        onLoginSuccess({ user_name: "Invitado", role: "Visitante", token: "guest-token" });
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleLogin}>
                <h2>Acceso Asistente</h2>
                <input type="text" placeholder="Usuario" onChange={e => setUsername(e.target.value)} />
                <input type="password" placeholder="Contraseña" onChange={e => setPassword(e.target.value)} />
                <button type="submit" className="btn-new-chat">Iniciar Sesión</button>
                <button type="button" onClick={handleGuest} className="btn-new-chat">
                    Acceder como Invitado
                </button>
            </form>
        </div>
    );
};