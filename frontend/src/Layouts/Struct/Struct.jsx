import { useState } from "react";
import Sidebar from "../Sidebar/Sidebar";
import styles from "./Struct.module.css";
import { BooksSVG, GlobeSVG } from "./../../assets/SVGs/SVGs";
import { useLocation } from "react-router-dom";

const Struct = ({ children }) => {
  const [mode, setMode] = useState(0);
  const location = useLocation();

  return (
    <div className={styles.container}>
      <div>
        <Sidebar />
      </div>
      <div className={styles.body}>
        <header className={styles.headers}>
          {location.pathname === "/" ||
          location.pathname.startsWith("/chat/") ? (
            <h1 />
          ) : (
            <></>
          )}
          <h1>RAG - H2D</h1>

          {location.pathname === "/" ||
          location.pathname.startsWith("/chat/") ? (
            <button onClick={() => setMode(!mode)}>
              {mode ? (
                <>
                  <BooksSVG /> <p>Resources Mode</p>
                </>
              ) : (
                <>
                  <GlobeSVG />
                  <p>Internet Mode</p>
                </>
              )}
            </button>
          ) : (
            <></>
          )}
        </header>
        <div className={styles.databody}>{children}</div>
      </div>
    </div>
  );
};

export default Struct;
