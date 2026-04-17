import { useEffect, useState } from "react";
import { api } from "@/api/client";
import type { PaginatedResponse, Notification } from "@/types";
import { Bell, X } from "lucide-react";

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [count, setCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    const poll = () => {
      api.get<{ unread_count: number }>("/notifications/unread-count")
        .then((r) => setCount(r.unread_count))
        .catch(() => {});
    };
    poll();
    const interval = setInterval(poll, 15000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = () => {
    api.get<PaginatedResponse<Notification>>("/notifications/?limit=20")
      .then((r) => setNotifications(r.items));
  };

  const toggle = () => {
    if (!open) loadNotifications();
    setOpen(!open);
  };

  const markRead = async (id: string) => {
    await api.post(`/notifications/${id}/read`, {});
    setCount((c) => Math.max(0, c - 1));
    setNotifications((ns) =>
      ns.map((n) => (n.id === id ? { ...n, read_at: new Date().toISOString() } : n))
    );
  };

  return (
    <div className="relative">
      <button onClick={toggle} className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
        <Bell className="w-5 h-5 text-gray-600" />
        {count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
            {count > 9 ? "9+" : count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-lg border z-50 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between px-4 py-3 border-b">
            <span className="text-sm font-semibold text-gray-800">Notifications</span>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600">
              <X className="w-4 h-4" />
            </button>
          </div>
          {notifications.length === 0 ? (
            <p className="p-4 text-sm text-gray-400 text-center">No notifications</p>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`px-4 py-3 border-b last:border-b-0 cursor-pointer hover:bg-gray-50 ${
                  !n.read_at ? "bg-blue-50" : ""
                }`}
                onClick={() => !n.read_at && markRead(n.id)}
              >
                <p className="text-sm font-medium text-gray-800">{n.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{n.body}</p>
                <p className="text-[10px] text-gray-400 mt-1">{new Date(n.sent_at).toLocaleString()}</p>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
