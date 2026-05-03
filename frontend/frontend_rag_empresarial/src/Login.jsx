
import { useState } from "react";

/**
 * Componente de Login
 * - Login real contra el backend (/login)
 * - Acceso como invitado
 */
function Login({ onLoginSuccess, onGuestAccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  /**
   * Envío de credenciales al backend
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        throw new Error("Credenciales incorrectas. Por favor, inténtalo de nuevo.");
      }

      const data = await response.json();

      // Guardamos usuario en localStorage
      localStorage.setItem("user", JSON.stringify(data));

      // Informamos a App.jsx
      onLoginSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Acceso al sistema</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p className="error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Verificando..." : "Iniciar sesión"}
        </button>
      </form>

      <hr />

      <button onClick={onGuestAccess}>
        Acceder como invitado
      </button>
    </div>
  );
}

export default Login;
