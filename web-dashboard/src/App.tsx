import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import DashboardPage from "@/pages/DashboardPage";
import WorkflowPage from "@/pages/WorkflowPage";
import RecordsPage from "@/pages/RecordsPage";
import DocsPage from "@/pages/DocsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/workflow" element={<WorkflowPage />} />
          <Route path="/records" element={<RecordsPage />} />
          <Route path="/docs" element={<DocsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
