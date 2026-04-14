import React from "react";

export const Sidebar = ({ onNewChat, conversations = [], onSelectChat, currentConvId }) => {
    return (
        <nav className="sidebar">
            <button 
                type="button" 
                className="btn-new-chat" 
                onClick={onNewChat}
            >
                + Nuevo Chat
            </button>

            <section className="history">
                <h2>Últimas conversaciones</h2>
                <ul>
                    {conversations.length > 0 ? (
                        conversations.map((conv) => (
                            <li 
                                key={conv.id} 
                                className={currentConvId === conv.id ? "active-chat" : ""}
                                onClick={() => onSelectChat(conv.id)}
                            >
                                {conv.title}
                            </li>
                        ))
                    ) : (
                        <span className="no-history">Sin chats previos</span>
                    )}
                </ul>
            </section>
        </nav>
    );
};