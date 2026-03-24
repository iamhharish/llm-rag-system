import styles from "./Sidebar.module.css";
import {
  SidebarSVG,
  HistorySVG,
  DatabaseSVG,
  APISVG,
  PencilSVG,
  LogoSVG,
  LogOutSVG,
} from "../../assets/SVGs/SVGs";
import { useState, useLayoutEffect, useRef } from "react";
import { gsap } from "gsap";
import { useAuthStore} from './../../store/authStore'

const Sidebar = () => {

  const { logout } = useAuthStore();
  const [isOpen, setIsOpen] = useState(true);
  const pRefs = useRef([]);

  useLayoutEffect(() => {
    pRefs.current.forEach((p, index) => {
      if (isOpen) {
        gsap.to(p, {
          duration: 0.5,
          width: "auto",
          opacity: 1,
          paddingRight: "1rem",
        });
      } else {
        gsap.to(p, {
          duration: 0.5,
          width: 0,
          opacity: 0,
          paddingRight: 0,
        });
      }
    });
  }, [isOpen]);

  return (
    <div className={styles.container}>
      <div className={styles.links}>
        <button onClick={() => setIsOpen(!isOpen)}>
          <p ref={(el) => pRefs.current.push(el)}>
            <LogoSVG />
          </p>{" "}
          <SidebarSVG isOpen={isOpen} />
        </button>
        <button>
          <a href="/" ref={(el) => pRefs.current.push(el)}>
            New Chat
          </a>{" "}
          <PencilSVG />
        </button>
        <button>
          <a href="/history" ref={(el) => pRefs.current.push(el)}>
            History
          </a>{" "}
          <HistorySVG />
        </button>
        <button>
          <a href="/resources" ref={(el) => pRefs.current.push(el)}>
            Resources
          </a>{" "}
          <DatabaseSVG />
        </button>
        <button>
          <a href="/api" ref={(el) => pRefs.current.push(el)}>
            API
          </a>{" "}
          <APISVG />
        </button>
      </div>

      <div className={styles.links}>
        <button onClick={logout}>
          <a href="/api" ref={(el) => pRefs.current.push(el)}>
            Log Out
          </a>{" "}
          <LogOutSVG />
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
