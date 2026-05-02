import { useState, useEffect } from "react";
import { Header } from "./Components/Header";
import { Sidebar } from "./Components/Sidebar";
import { Chat } from "./Components/Chat";
import { Login } from "./Components/Login";

const API_BASE_URL = "http://localhost:8000";

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [conversations, setConversations] = useState([]); // Para el Sidebar
    const [currentConvId, setCurrentConvId] = useState(null); // Trackea el chat activo
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Al arrancar, comprobamos si hay un token válido guardado
        const savedToken = localStorage.getItem("token");
        const savedUser = localStorage.getItem("user");

        if (savedToken && savedUser) {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            // Definimos el mensaje inicial aquí con el nombre real
            setMessages([{ 
                role: "bot", 
                text: `Hola ${parsedUser.user_name}, soy tu asistente. ¿En qué te puedo ayudar?`,
                fuentes: [] 
            }]);
        }
        setLoading(false);
    }, []);

    // 2. Efecto para cargar conversaciones (SOLO si hay usuario)
    useEffect(() => {
        if (user) {
            fetchConversations();
        }
    }, [user]); // Se dispara cuando el usuario hace login

    const fetchConversations = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/conversations/${user.user_name}`);
            const data = await res.json();
            setConversations(data); 
        } catch (err) {
            console.error("Error al cargar historial:", err);
        }
    };

    const handleSend = async (e) => {
        if (e) e.preventDefault();
        if (!input.trim()) return;

        // Añadimos mensaje del usuario localmente para feedback inmediato
        const userMessage = { role: "user", text: input };
        setMessages(prev => [...prev, userMessage]);
        const tempInput = input;
        setInput(""); 

        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_name: user.user_name,
                    pregunta: tempInput,
                    conversation_id: currentConvId 
                })
            });

            const data = await response.json();

            // Guardamos la respuesta y la lista de fuentes (archivo y texto)
            const botMessage = { 
                role: "bot", 
                text: data.respuesta,
                fuentes: data.fuentes || [] // Captura las fuentes reales del backend
            };
            setMessages(prev => [...prev, botMessage]);

            // Si era un chat nuevo, guardamos el ID y refrescamos el sidebar
            if (!currentConvId) {
                setCurrentConvId(data.conversation_id);
                fetchConversations();
            }
        } catch (error) {
            console.error("Error conectando con el backend:", error);
            setMessages(prev => [...prev, { 
                role: "bot", 
                text: "Error de conexión con el servidor.",
                fuentes: [] 
            }]);
        }
    };

    // --- FUNCIÓN DE FEEDBACK ---
    const handleFeedback = async (index, valor) => {
        if (!currentConvId) return;

        try {
            await fetch(`${API_BASE_URL}/chat/feedback`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    conversation_id: currentConvId,
                    message_index: index,
                    valor: valor
                })
            });

            // Actualizamos el estado local para que el componente Chat sepa que ya hay feedback
            setMessages(prev => {
                const newMessages = [...prev];
                newMessages[index] = { ...newMessages[index], feedback: valor };
                return newMessages;
            });
            
            console.log(`Feedback ${valor} guardado para el mensaje ${index}`);
        } catch (error) {
            console.error("Error al enviar el feedback:", error);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Al pulsar "Nueva Conversación" reseteamos el estado local
    const handleNewChat = () => {
        setMessages([{ 
            role: "bot", 
            text: `Hola ${user?.user_name}, ¿en qué puedo ayudarte ahora?`,
            fuentes: [] 
        }]);
        setCurrentConvId(null);
        setInput("");
    };

    // Cargar un chat antiguo al hacer clic en el Sidebar
    const loadConversation = async (id) => {
        try {
            const res = await fetch(`${API_BASE_URL}/chat/${id}`);
            const data = await res.json();
            // data ya contiene los mensajes con sus respectivas fuentes de la DB
            setMessages(data); 
            setCurrentConvId(id);
        } catch (err) {
            console.error("Error al cargar la conversación:", err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setUser(null);
    };

    if (loading) return <div className="loading-screen">Cargando sistema...</div>;

    // Renderizado Condicional
    if (!user) {
        return <Login onLoginSuccess={(data) => setUser(data)} />;
    }

    return (
        <div className="app-wrapper">
            <Header
                title="Asistente de IFP"
                userName={user.user_name}
                userRole="Jefe"
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