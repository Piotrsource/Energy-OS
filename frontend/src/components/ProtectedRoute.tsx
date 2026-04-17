import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";

/**
 * Route guard that redirects unauthenticated users to /login.
 *
 * Wrap protected <Route> elements with this component:
 *
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/" element={<DashboardPage />} />
 *   </Route>
 *
 * It checks `isAuthenticated` from AuthContext (which also handles
 * token expiry detection). If the user is not authenticated, they
 * are redirected to the login page.
 */
export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
