export const ChatMessage = ({ msg, index, onFeedback }) => {
    return (
        <section className={`chat-message message-${msg.role}`}>
            {/* 1. TEXTO DEL MENSAJE */}
            <p>{msg.text}</p>

            {/* 2. SECCIÓN DE FUENTES (RAG) */}
            {msg.role === "bot" && msg.fuentes && msg.fuentes.length > 0 && (
                <div className="sources-wrapper">
                    <details>
                        <summary className="sources-summary">
                            <span>🔍</span> Ver fuentes citadas ({msg.fuentes.length})
                        </summary>
                        <div className="sources-content">
                            {msg.fuentes.map((f, idx) => (
                                <div key={idx} className="source-card">
                                    <div className="source-filename">📄 {f.archivo}</div>
                                    <div className="source-quote">"{f.texto}"</div>
                                </div>
                            ))}
                        </div>
                    </details>
                </div>
            )}

        {/* 3. SECCIÓN DE FEEDBACK */}
        {msg.role === "bot" && index !== 0 && (
            <div className="feedback-section">
                <button 
                    className={`feedback-btn ${msg.feedback === 'like' ? 'active-like' : ''}`}
                    onClick={() => onFeedback && onFeedback(index, 'like')}
                    title="Respuesta útil"
                >
                    👍
                </button>
                <button 
                    className={`feedback-btn ${msg.feedback === 'dislike' ? 'active-dislike' : ''}`}
                    onClick={() => onFeedback && onFeedback(index, 'dislike')}
                    title="Respuesta no útil"
                >
                    👎
                </button>
                
                {msg.feedback && (
                    <span className="feedback-thanks">
                        ¡Gracias por tu feedback!
                    </span>
                )}
            </div>
        )}
        </section>
    );
};