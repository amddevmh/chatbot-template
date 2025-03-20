import { Outlet } from "react-router-dom";
import { AuthProvider } from "./components/auth-provider";

export default function App() {  
  return (
    <AuthProvider>
       <Outlet />
    </AuthProvider>
  );
}
