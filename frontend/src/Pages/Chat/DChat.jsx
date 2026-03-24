import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import styles from "./Chat.module.css";
import ReactMarkdown from "react-markdown";
import { useAuthStore } from "../../store/authStore";

const DChat = () => {
  const { chatId } = useParams();
  const chatEndRef = useRef(null);
  const { currentUser } = useAuthStore();

  const userId = currentUser?.id;

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    if (!chatId) return;

    const fetchMessages = async () => {
      try {
        const res = await axios.get(
          `http://localhost:5000/chat/${chatId}/${userId}`
        );

        const formatted = res.data.map((msg, index) => ({
          id: index,
          text: msg.content,
          sender: msg.sender === "user" ? 0 : 1,
        }));

        setMessages(formatted);
      } catch (err) {
        console.error(err);
      }
    };

    fetchMessages();
  }, [chatId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ Send message
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
      const res = await axios.post(
        `http://localhost:5000/chat/${chatId}`,
        {
          query: input,
          user_id: userId,
        }
      );

      const botMessage = {
        id: Date.now() + 1,
        text: res.data.response || "No response",
        sender: 1,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "Error getting response",
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
          placeholder="Continue chat..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default DChat;