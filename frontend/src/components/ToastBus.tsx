
type ToastProps = {
  message: string;
  duration?: number;
};

type ToastListener = (event: ToastProps) => void;

const globalKey = "__toast_listeners__";
const listeners: ToastListener[] =
  (globalThis as any)[globalKey] || ((globalThis as any)[globalKey] = []);

export function subscribeToListeners(listener: ToastListener) {
  listeners.push(listener);
  return () => {
    const idx = listeners.indexOf(listener);
    if (idx > -1) listeners.splice(idx, 1);
  };
}
export function showToast(message: string, duration: number = 3000) {
  listeners.forEach(listener => listener({ message, duration }));
}