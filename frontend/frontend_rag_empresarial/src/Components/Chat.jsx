export const Chat = ({messages, input, setInput, onSend, onKeyDown}) => {
    return(
        <main className="chat-container">
            <article className="chat">
                {messages.map((msg, index) => (
                    <section key={index} className={`message-${msg.role}`}>
                        <p>{msg.text}</p>
                    </section>
                ))}
            </article>
            <footer className="chat-input">
                <form className="chat-form" onSubmit={onSend}>
                    <textarea
                        value={input}
                        placeholder="Escribe tu consulta"
                        onChange={(e)=> setInput(e.target.value)} // Añade al input lo que se escribe
                        onKeyDown= {onKeyDown}
                        required
                        autoFocus //Hace que al cargar pagina ya este activo para escribir
                    />
                </form>
            </footer>
        </main>
    );
}