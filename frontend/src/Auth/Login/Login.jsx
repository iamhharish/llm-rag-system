import { useState } from "react";
import styles from "./Login.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [form, setForm] = useState({
    username_or_email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError(""); // reset previous error

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/api/auth/login",
        form,
      );

      console.log("Login successful:", response.data);

      login(response.data);
      navigate("/");
    } catch (err) {
      console.error("Login failed:", err);

      if (err.response) {
        const message =
          err.response.data?.message ||
          err.response.data?.error ||
          "Invalid username/email or password";

        setError(message);
      }

      else if (err.request) {
        setError("Server not responding. Please try again later.");
      }

      else {
        setError("Something went wrong. Please try again.");
      }
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Login</h2>

        {error && <p className={styles.error}>{error}</p>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="text"
            name="username_or_email"
            placeholder="Enter your username or email"
            value={form.username_or_email}
            onChange={handleChange}
            className={styles.input}
          />

          <input
            type="password"
            name="password"
            placeholder="Enter your password"
            value={form.password}
            onChange={handleChange}
            className={styles.input}
          />

          <button type="submit" className={styles.button}>
            Login
          </button>
        </form>

        <a href="/register" className={styles.footer}>
          Don't have an account? <span>Sign up</span>
        </a>
      </div>
    </div>
  );
};

export default Login;
