export const Chat = ({messages, input, setInput, onSend, onKeyDown, onFeedback}) => {
    return(
        <main className="chat-container">
            <article className="chat">
                {messages.map((msg, index) => (
                    <section key={index} className={`message-${msg.role}`} style={{ marginBottom: '20px' }}>
                        {/* 1. TEXTO DEL MENSAJE */}
                        <p>{msg.text}</p>

                        {/* 2. SECCIÓN DE FUENTES (Solo si es el bot y hay fuentes) */}
                        {msg.role === "bot" && msg.fuentes && msg.fuentes.length > 0 && (
                            <div className="sources-wrapper" style={{
                                marginTop: '12px',
                                paddingTop: '8px',
                                borderTop: '1px solid rgba(0,0,0,0.1)',
                                fontSize: '0.8rem'
                            }}>
                                <details>
                                    <summary style={{
                                        cursor: 'pointer',
                                        color: '#2563eb',
                                        fontWeight: '600',
                                        listStyle: 'none',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '4px'
                                    }}>
                                        <span>🔍</span> Ver fuentes citadas ({msg.fuentes.length})
                                    </summary>
                                    
                                    <div style={{
                                        marginTop: '8px',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        gap: '8px'
                                    }}>
                                        {msg.fuentes.map((f, idx) => (
                                            <div key={idx} style={{
                                                backgroundColor: 'rgba(0,0,0,0.03)',
                                                padding: '10px',
                                                borderRadius: '8px',
                                                borderLeft: '4px solid #2563eb'
                                            }}>
                                                <div style={{ fontWeight: '700', marginBottom: '4px', color: '#1e3a8a' }}>
                                                    📄 {f.archivo}
                                                </div>
                                                <div style={{ color: '#374151', fontStyle: 'italic', lineHeight: '1.4' }}>
                                                    "{f.texto}"
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </details>
                            </div>
                        )}

                        {/* 3. SECCIÓN DE FEEDBACK (Pulgares) - IMPLEMENTADO POR MARIO */}
                        {msg.role === "bot" && index !== 0 && (
                            <div className="feedback-section" style={{
                                display: 'flex',
                                gap: '12px',
                                marginTop: '10px',
                                opacity: '0.7'
                            }}>
                                <button 
                                    onClick={() => onFeedback && onFeedback(index, 'like')}
                                    style={{ 
                                        border: 'none', 
                                        background: 'none', 
                                        cursor: 'pointer', 
                                        fontSize: '1.1rem',
                                        transition: 'transform 0.2s'
                                    }}
                                    title="Respuesta útil"
                                    onMouseOver={(e) => e.target.style.transform = 'scale(1.2)'}
                                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                                >
                                    👍
                                </button>
                                <button 
                                    onClick={() => onFeedback && onFeedback(index, 'dislike')}
                                    style={{ 
                                        border: 'none', 
                                        background: 'none', 
                                        cursor: 'pointer', 
                                        fontSize: '1.1rem',
                                        transition: 'transform 0.2s'
                                    }}
                                    title="Respuesta no útil"
                                    onMouseOver={(e) => e.target.style.transform = 'scale(1.2)'}
                                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                                >
                                    👎
                                </button>
                                {msg.feedback && (
                                    <span style={{ fontSize: '0.7rem', color: '#059669', alignSelf: 'center' }}>
                                        ¡Gracias por tu feedback!
                                    </span>
                                )}
                            </div>
                        )}
                    </section>
                ))}
            </article>
            
            <footer className="chat-input">
                <form className="chat-form" onSubmit={onSend}>
                    <textarea
                        value={input}
                        placeholder="Escribe tu consulta"
                        onChange={(e)=> setInput(e.target.value)}
                        onKeyDown= {onKeyDown}
                        required
                        autoFocus
                    />
                </form>
            </footer>
        </main>
    );
}