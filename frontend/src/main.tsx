import React, { Suspense, lazy, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  BrowserRouter,
  Navigate,
  NavLink,
  Route,
  Routes,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig, motion } from "motion/react";
import { Toaster } from "sonner";
import {
  ChartNoAxesCombined,
  Droplets,
  FileText,
  Info,
  Layers,
  LayoutDashboard,
  Menu,
  X,
} from "lucide-react";
import { LabArt, Logo, Waves } from "./components/Brand";
import { Loading } from "./components/ui";
import "./styles.css";
const Analyzer = lazy(() => import("./pages/Analyzer"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Models = lazy(() => import("./pages/Models"));
const Batch = lazy(() => import("./pages/Batch"));
const Reports = lazy(() => import("./pages/Reports"));
const About = lazy(() => import("./pages/About"));
const client = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});
const nav = [
  { to: "/dashboard", title: "Dashboard", Icon: LayoutDashboard },
  { to: "/analyze", title: "Analyze Sample", Icon: Droplets },
  { to: "/models", title: "Model Comparison", Icon: ChartNoAxesCombined },
  { to: "/batch", title: "Batch Analysis", Icon: Layers },
  { to: "/reports", title: "Reports", Icon: FileText },
  { to: "/about", title: "About", Icon: Info },
];
export function App() {
  const [open, setOpen] = useState(false);
  return (
    <MotionConfig reducedMotion="user">
      <BrowserRouter>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <button
          className="mobile-toggle icon-button"
          aria-label={open ? "Close navigation" : "Open navigation"}
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
        {open && (
          <button
            className="nav-scrim"
            aria-label="Close navigation"
            onClick={() => setOpen(false)}
          />
        )}
        <aside className={`sidebar ${open ? "is-open" : ""}`}>
          <Logo />
          <nav aria-label="Main navigation">
            {nav.map(({ to, title, Icon }) => (
              <NavLink to={to} key={to} onClick={() => setOpen(false)}>
                <Icon size={21} />
                <span>{title}</span>
              </NavLink>
            ))}
          </nav>
          <LabArt />
          <div className="sidebar-foot">UNIT 5 · ML RESEARCH PROJECT</div>
        </aside>
        <main id="main">
          <Waves />
          <motion.div
            className="page-content"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Suspense fallback={<Loading />}>
              <Routes>
                <Route path="/" element={<Navigate to="/analyze" replace />} />
                <Route path="/analyze" element={<Analyzer />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/models" element={<Models />} />
                <Route path="/batch" element={<Batch />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/about" element={<About />} />
                <Route path="*" element={<Navigate to="/analyze" replace />} />
              </Routes>
            </Suspense>
            <footer className="page-footer">
              <span>JalSathi · Intelligent Water Quality Analysis</span>
              <span>
                Educational screening only · Laboratory testing remains
                essential
              </span>
            </footer>
          </motion.div>
        </main>
        <Toaster richColors position="bottom-right" />
      </BrowserRouter>
    </MotionConfig>
  );
}
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={client}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
