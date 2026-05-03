import { useState } from 'react';

export const Login = ({ onLoginSuccess, onGuestAccess }) => {
    const [email, setEmail] = useState(""); 
    const [password, setPassword] = useState("");
    const [isLogging, setIsLogging] = useState(false);

    // Función acceso como trabajador (llamada API)
    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLogging(true);

        try {
            const response = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                const data = await response.json();
                onLoginSuccess(data);
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Credenciales incorrectas");
            }
        } catch (error) {
            alert("Error de conexión con el servidor");
        } finally {
            setIsLogging(false);
        }
    };

    // Función botón acceso invitado
    const handleGuestClick = () => {
        onGuestAccess();
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleLogin}>
                <h2>Acceso Asistente RAG</h2>
                <input 
                    type="email" 
                    placeholder="Email corporativo" 
                    value={email}
                    onChange={e => setEmail(e.target.value)} 
                    required 
                />
                <input 
                    type="password" 
                    placeholder="Contraseña" 
                    value={password}
                    onChange={e => setPassword(e.target.value)} 
                    required 
                />
                <button type="submit" className="btn-new-chat" disabled={isLogging}>
                    {isLogging ? "Verificando..." : "Iniciar Sesión"}
                </button>
                
                <button type="button" onClick={handleGuestClick} className="btn-new-chat">
                    Acceder como Invitado
                </button>
            </form>
        </div>
    );
};