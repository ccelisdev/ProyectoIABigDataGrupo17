import { useState, useEffect, useCallback } from "react";
import { Header } from "./Components/Header";
import { Sidebar } from "./Components/Sidebar";
import { Chat } from "./Components/Chat";
import { Login } from "./Components/Login";

const API_BASE_URL = "http://localhost:8000";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [conversations, setConversations] = useState([]); 
    const [currentConvId, setCurrentConvId] = useState(null); 
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Función de logout reutilizablle
    const handleLogout = useCallback(() => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setUser(null);
        setMessages([]);
        setCurrentConvId(null);
        setConversations([]);
    }, []);

    // 1. Recuperar sesión (User + Token) al arrancar
    useEffect(() => {
        const savedUser = localStorage.getItem("user");
        const savedToken = localStorage.getItem("token");

        if (savedUser && savedToken) {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            setMessages([{ 
                role: "bot", 
                text: `Sesión recuperada. Hola ${parsedUser.user_name}, ¿en qué puedo ayudarte hoy?`,
                fuentes: [] 
            }]);
        }
        setLoading(false);
    }, []);

    // 2. Cargar historial (Requiere Token)
    useEffect(() => {
        if (user && user.user_name !== "invitado") {
            fetchConversations();
        }
    }, [user]);

    // Lógica carga chat
    const fetchConversations = async () => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`${API_BASE_URL}/conversations/${user.user_name}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.status === 401) return handleLogout(); // Token expirado
            const data = await res.json();
            setConversations(data); 
        } catch (err) {
            console.error("Error de red al cargar historial:", err);
        }
    };

    // Lógica Autenticación como trabajador
    const handleLoginSuccess = (userData) => {
        // userData debe traer { user_name, role, token }
        localStorage.setItem("user", JSON.stringify({ 
            user_name: userData.user_name, 
            role: userData.role 
        }));
        localStorage.setItem("token", userData.token); // Guardamos el token JWT
        
        setUser(userData);
        setCurrentConvId(null);
    };

    // Lógica Autenticación como invitado
    const handleGuestAccess = () => {
        const guestUser = { user_name: "invitado", role: "empleado" };
        localStorage.setItem("user", JSON.stringify(guestUser));
        localStorage.setItem("token", "invitado"); // Token simbólico para invitados
        setUser(guestUser);
        setCurrentConvId(null);
    };

    // Logica del chat
    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim()) return;

        const token = localStorage.getItem("token");
        const userMessage = { role: "user", text: input };
        setMessages(prev => [...prev, userMessage]);
        const tempInput = input;
        setInput(""); 

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` // Autenticación en cada pregunta
                },
                body: JSON.stringify({
                    user_name: user.user_name,
                    role: user.role,
                    pregunta: tempInput,
                    conversation_id: currentConvId 
                })
            });

            if (response.status === 401) return handleLogout();

            const data = await response.json();
            const botMessage = { 
                role: "bot", 
                text: data.respuesta,
                fuentes: data.fuentes || [] 
            };
            setMessages(prev => [...prev, botMessage]);

            if (!currentConvId && user.user_name !== "invitado") {
                setCurrentConvId(data.conversation_id);
                fetchConversations();
            }
        } catch (error) {
            console.error("Error en RAG:", error);
            setMessages(prev => [...prev, { 
                role: "bot", 
                text: "Error de conexión. Inténtalo de nuevo.",
                fuentes: [] 
            }]);
        }
    };

    // Lógica del feedback
    const handleFeedback = async (index, valor) => {
        if (!currentConvId) return;
        const token = localStorage.getItem("token");
        try {
            await fetch(`${API_BASE_URL}/chat/feedback`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    conversation_id: currentConvId,
                    message_index: index,
                    valor: valor
                })
            });
            setMessages(prev => {
                const newMessages = [...prev];
                newMessages[index] = { ...newMessages[index], feedback: valor };
                return newMessages;
            });
        } catch (err) { console.error(err); }
    };

    // Logica salto de linea chat con Shift + Enter
    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Lógica botón Nuevo Chat
    const handleNewChat = () => {
        setMessages([{ 
            role: "bot", 
            text: `¿En qué puedo ayudarte con esta nueva consulta, ${user?.user_name}?`,
            fuentes: [] 
        }]);
        setCurrentConvId(null);
        setInput("");
    };

    // Logica cargar conversación historial
    const loadConversation = async (id) => {
        const token = localStorage.getItem("token");
        try {
            const res = await fetch(`${API_BASE_URL}/chat/${id}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.status === 401) return handleLogout();
            const data = await res.json();
            setMessages(data); 
            setCurrentConvId(id);
        } catch (err) { console.error(err); }
    };

    if (loading) return <div className="loading-screen">Validando sesión...</div>;

    if (!user) {
        return (
            <Login 
                onLoginSuccess={handleLoginSuccess} 
                onGuestAccess={handleGuestAccess} 
            />
        );
    }

    return (
        <div className="app-wrapper">
            <Header
                title="Asistente Corporativo IFP"
                userName={user.user_name}
                userRole={user.role}
                onLogout={handleLogout}
            />
            <div className="layout-container">
                <Sidebar
                    onNewChat={handleNewChat}
                    conversations={conversations}
                    onSelectChat={loadConversation}
                />
                <Chat
                    messages={messages}
                    input={input}
                    setInput={setInput}
                    onSend={handleSend}
                    onKeyDown={handleKeyDown}
                    onFeedback={handleFeedback} 
                />
            </div>
        </div>
    );
}

export default App;