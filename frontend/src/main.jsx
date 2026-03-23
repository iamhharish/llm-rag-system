import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import Paths from "./Paths/Paths";
import { BrowserRouter } from "react-router-dom";


createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Paths />
    </BrowserRouter>
  </StrictMode>,
);
