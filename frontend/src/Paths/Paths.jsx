import { Routes, Route, Navigate } from "react-router-dom";
import App from "../App";
import Login from "../Auth/Login/Login";
import Register from "../Auth/Register/Register";
import { useAuthStore } from "../store/authStore";

import { API, Chat, Resources, History, DChat } from "../Pages/Pages";

const Paths = () => {
  const { currentUser } = useAuthStore();

  return (
    <Routes>
      {currentUser ? (
        <>
          <Route path="/" element={<App><Chat /></App>} />
          <Route path="/chat/:chatId" element={<App><DChat /></App>} />
          <Route path="/api" element={<App><API /></App>} />
          <Route path="/history" element={<App><History /></App>} />
          <Route path="/resources" element={<App><Resources /></App>} />
          <Route path="*" element={<Navigate to="/" />} />
        </>
      ) : (
        <>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </>
      )}
    </Routes>
  );
};

export default Paths;