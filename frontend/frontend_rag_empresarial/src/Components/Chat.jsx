import { ChatMessage } from './ChatMessage';

export const Chat = ({messages, input, setInput, onSend, onKeyDown, onFeedback}) => {
    return(
        <main className="chat-container">
            <article className="chat">
                {messages.map((msg, index) => (
                    <ChatMessage 
                        key={index} 
                        msg={msg} 
                        index={index} 
                        onFeedback={onFeedback} 
                    />
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