import { useState } from 'react';

export const Login = ({ onLoginSuccess }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isLogging, setIsLogging] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLogging(true);
        setError("");

        // SIMULACIÓN DE LLAMADA A API
        setTimeout(() => {
            if (username === "admin" && password === "123") {
                const mockToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...fakeToken";
                const userData = { 
                    user_name: "Juan Saldaña", 
                    role: "Jefe",
                    token: mockToken 
                };
                
                // Guardamos en el navegador
                localStorage.setItem("token", mockToken);
                localStorage.setItem("user", JSON.stringify(userData));
                
                onLoginSuccess(userData);
            } else {
                setError("Usuario o contraseña incorrectos");
                setIsLogging(false);
            }
        }, 1500);
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleLogin}>
                <h2>Asistente RAG IFP</h2>
                <input 
                    type="text" 
                    placeholder="Usuario" 
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    disabled={isLogging}
                    required
                />
                <input 
                    type="password" 
                    placeholder="Contraseña" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLogging}
                    required
                />
                {error && <p className="login-error">{error}</p>}
                <button type="submit" className="btn-new-chat" disabled={isLogging}>
                    {isLogging ? "Validando..." : "Iniciar Sesión"}
                </button>
            </form>
        </div>
    );
};