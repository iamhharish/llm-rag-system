import { useState } from "react";
import styles from "./Register.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Register = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    phone: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setError("");
    setSuccess("");

    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/api/auth/register",
        form
      );

      console.log("Register success:", response.data);

      setSuccess(response.data.message || "Registration successful");

      // Redirect after 1.5 sec
      setTimeout(() => {
        navigate("/login");
      }, 1500);
    } catch (err) {
      console.error("Register failed:", err);

      if (err.response) {
        // Backend error (400, etc.)
        const message =
          err.response.data?.error ||
          err.response.data?.message ||
          "Registration failed";

        setError(message);
      } else if (err.request) {
        setError("Server not responding. Try again later.");
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Register</h2>

        {error && <p className={styles.error}>{error}</p>}
        {success && <p className={styles.success}>{success}</p>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <input
            type="text"
            name="username"
            placeholder="Enter username"
            value={form.username}
            onChange={handleChange}
            className={styles.input}
          />

          <input
            type="email"
            name="email"
            placeholder="Enter email"
            value={form.email}
            onChange={handleChange}
            className={styles.input}
          />

          <input
            type="password"
            name="password"
            placeholder="Create password"
            value={form.password}
            onChange={handleChange}
            className={styles.input}
          />

          <input
            type="text"
            name="phone"
            placeholder="Enter phone number"
            value={form.phone}
            onChange={handleChange}
            className={styles.input}
          />

          <button type="submit" className={styles.button} disabled={loading}>
            {loading ? "Registering..." : "Register"}
          </button>
        </form>

        <a href="/login" className={styles.footer}>
          Already have an account? <span>Login</span>
        </a>
      </div>
    </div>
  );
};

export default Register;