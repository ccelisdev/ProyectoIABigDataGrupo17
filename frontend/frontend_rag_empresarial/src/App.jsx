import { useState, useEffect } from "react";
import { Header } from "./Components/Header";
import { Sidebar } from "./Components/Sidebar";
import { Chat } from "./Components/Chat";

const USER_NAME = "Juan Saldaña";
const API_BASE_URL = "http://localhost:8000";
const INITIAL_MESSAGE = { role: "bot", text: `Hola ${USER_NAME}, soy tu asistente. ¿En qué te puedo ayudar?` };

function App() {
    const [messages, setMessages] = useState([INITIAL_MESSAGE]);
    const [input, setInput] = useState("");
    const [conversations, setConversations] = useState([]); // Para el Sidebar
    const [currentConvId, setCurrentConvId] = useState(null); // Trackea el chat activo

    // 1. Cargar historial del Sidebar al iniciar (maneja usuario nuevo o existente)
    useEffect(() => {
        fetchConversations();
    }, []);

    const fetchConversations = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/conversations/${USER_NAME}`);
            const data = await res.json();
            setConversations(data); // Si no hay chats, vendrá un []
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
                    user_name: USER_NAME,
                    pregunta: tempInput,
                    conversation_id: currentConvId // Si es null, el backend crea uno nuevo
                })
            });

            const data = await response.json();

            // Actualizamos con la respuesta del RAG
            const botMessage = { role: "bot", text: data.respuesta };
            setMessages(prev => [...prev, botMessage]);

            // Si era un chat nuevo, guardamos el ID y refrescamos el sidebar
            if (!currentConvId) {
                setCurrentConvId(data.conversation_id);
                fetchConversations();
            }
        } catch (error) {
            console.error("Error conectando con el backend:", error);
            setMessages(prev => [...prev, { role: "bot", text: "Error de conexión con el servidor." }]);
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
        setMessages([INITIAL_MESSAGE]);
        setCurrentConvId(null);
        setInput("");
    };

    // Cargar un chat antiguo al hacer clic en el Sidebar
    const loadConversation = async (id) => {
        try {
            const res = await fetch(`${API_BASE_URL}/chat/${id}`);
            const data = await res.json();
            setMessages(data); // Reemplaza los mensajes actuales con el historial de esa ficha
            setCurrentConvId(id);
        } catch (err) {
            console.error("Error al cargar la conversación:", err);
        }
    };

    return (
        <div className="app-wrapper">
            <Header
                title="Asistente de Empresa Ficticia"
                userName={USER_NAME}
                userRole="Jefe"
            />
            <div className="layout-container">
                <Sidebar
                    onNewChat={handleNewChat}
                    conversations={conversations}
                    onSelectChat={loadConversation} // Pasa esta función al Sidebar
                />
                <Chat
                    messages={messages}
                    input={input}
                    setInput={setInput}
                    onSend={handleSend}
                    onKeyDown={handleKeyDown}
                />
            </div>
        </div>
    );
}

export default App;