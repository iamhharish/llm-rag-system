import { useEffect, useState } from "react";
import axios from "axios";
import styles from "./History.module.css";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";
import { GlobeSVG, BooksSVG } from "../../assets/SVGs/SVGs";

const History = () => {
  const [chats, setChats] = useState([]);
  const { currentUser } = useAuthStore();
  const navigate = useNavigate();

  const userId = currentUser?.id;

  useEffect(() => {
    if (!userId) return;

    const fetchChats = async () => {
      try {
        const res = await axios.get(
          `http://localhost:5000/chat/history/${userId}`,
        );
        setChats(res.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchChats();
  }, [userId]);

  const handleOpenChat = (chatId) => {
    navigate(`/chat/${chatId}`);
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Chat History</h2>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>

          <tbody>
            {chats.length > 0 ? (
              chats.map((chat, index) => (
                <tr
                  key={chat.chat_id}
                  onClick={() => handleOpenChat(chat.chat_id)}
                  className={styles.row}
                >
                  {/* <td>{index + 1}</td> */}
                  <td className={styles.titleCell}>{chat.title}</td>

                  <td>{chat.mode ? <BooksSVG />: <GlobeSVG />}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" className={styles.empty}>
                  No chats found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default History;
