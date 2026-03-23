import { useState, useEffect, useRef } from "react";
import axios from "axios";
import styles from "./Chat.module.css";
import ReactMarkdown from "react-markdown";
import { useAuthStore } from "../../store/authStore";
import { useNavigate } from "react-router-dom";

const Chat = () => {
  const chatEndRef = useRef(null);
  const { currentUser } = useAuthStore();
  const navigate = useNavigate();

  const userId = currentUser?.id;

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !userId) return;

    const userMessage = {
      id: Date.now(),
      text: input,
      sender: 0,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const res = await axios.post("http://localhost:5000/chat", {
        query: input,
        user_id: userId,
      });

      const chatId = res.data.chat_id;

      // redirect to dynamic chat
      navigate(`/chat/${chatId}`);

    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Error creating chat",
          sender: 1,
        },
      ]);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.chats}>
        {messages.map((message) => (
          <div
            key={message.id}
            className={`${styles.message} ${
              message.sender === 0 ? styles.user : styles.bot
            }`}
          >
            <ReactMarkdown>{message.text}</ReactMarkdown>
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      <div className={styles.input}>
        <input
          type="text"
          placeholder="Start a new chat..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default Chat;