import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "motion/react"
import { subscribeToListeners } from "./ToastBus";
import './Toast.css';



type Toast = {
  id: number;
  message: string;
};

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const subscription = subscribeToListeners(({ message, duration, id, type }) => {
      if (type === "show" && message) {
        setToasts(prevToasts => [...prevToasts, { id, message }]);
        setTimeout(() => {
          setToasts(prevToasts => prevToasts.filter(t => t.id !== id))
        }, duration);
      }
      else if (type === "remove") {
        setToasts(prevToasts => prevToasts.filter(t => t.id !== id));
      }
    });
    return () => {
      subscription();
    }
  }, []);
  return (

    <div className="toast-container">
      <AnimatePresence>
        {toasts.map(toast => (
          <motion.div
            layout="position"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, x: 100 }}
            transition={{ layout: { duration: 0.2, ease: "easeInOut" } }}
            key={toast.id}
            className={"toast"}>
            {toast.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

export { showToast } from "./ToastBus";