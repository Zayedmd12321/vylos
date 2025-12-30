"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/api";
import { 
  LogOut, 
  Plus, 
  Layout, 
  Activity, 
  Clock,
  Terminal,
  ExternalLink,
  Loader2,
  Github
} from "lucide-react";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";

// --- Types ---
interface Project {
  id: number;
  name: string;
  description?: string;
  framework?: string;
  status: string;
  repo_url: string;
  domain?: string;
  created_at: string;
  last_deployed_at?: string;
}

// --- Sub-components ---
const StatCard = ({ label, value, icon: Icon, trend }: any) => (
  <div className="p-6 rounded-xl border border-white/[0.08] bg-zinc-900/50 backdrop-blur-sm hover:bg-zinc-900/80 transition-all duration-300 group">
    <div className="flex justify-between items-start mb-4">
      <div className="p-2 rounded-lg bg-zinc-800/50 text-zinc-400 group-hover:text-white transition-colors">
        <Icon size={20} />
      </div>
      {trend && <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">{trend}</span>}
    </div>
    <div className="space-y-1">
      <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
      <p className="text-sm text-zinc-500 font-medium">{label}</p>
    </div>
  </div>
);

const ProjectCard = ({ project, onClick }: { project: Project; onClick?: () => void }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Live': return 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]';
      case 'Building': return 'bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]';
      case 'Failed': return 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]';
      default: return 'bg-zinc-500';
    }
  };

  return (
    <div 
      onClick={onClick}
      className="p-5 rounded-xl border border-white/[0.08] bg-black/40 hover:border-white/20 hover:bg-zinc-900/60 transition-all cursor-pointer group"
    >
      <div className="flex justify-between items-start mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
            {project.name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <h4 className="font-semibold text-white group-hover:text-indigo-400 transition-colors">{project.name}</h4>
            <p className="text-xs text-zinc-500">{project.framework || 'Unknown'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor(project.status)}`} />
          <span className="text-xs text-zinc-500">{project.status}</span>
        </div>
      </div>
      <div className="flex justify-between items-center text-xs text-zinc-500 border-t border-white/[0.05] pt-4">
        <span className="flex items-center gap-1">
          <Github size={12} /> 
          {new URL(project.repo_url).pathname.split('/').pop()}
        </span>
        <span className="flex items-center gap-1">
          <Clock size={12} /> 
          {project.last_deployed_at ? new Date(project.last_deployed_at).toLocaleDateString() : 'Not deployed'}
        </span>
      </div>
      {project.domain && (
        <div className="mt-3 pt-3 border-t border-white/[0.05]">
          <a 
            href={`http://${project.domain}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink size={12} />
            {project.domain}
          </a>
        </div>
      )}
    </div>
  );
};

// --- Main Component ---
export default function DashboardPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);

  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
      setIsLoading(false);
      fetchProjects();
    }
  }, [router]);

  const fetchProjects = async () => {
    setLoadingProjects(true);
    try {
      const { data } = await api.get("/projects");
      setProjects(data);
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleLogout = () => {
    Cookies.remove("token");
    router.push("/");
  };

  if (isLoading) return <div className="min-h-screen bg-black text-white flex items-center justify-center">Loading...</div>;
  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-black text-white selection:bg-indigo-500/30">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.15)" glowColor="rgba(100, 100, 255, 0.4)" />
      
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/[0.08] bg-black/60 backdrop-blur-xl supports-[backdrop-filter]:bg-black/30">
         <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
             <div className="flex items-center gap-8">
                <span className="font-bold text-xl tracking-tighter flex items-center gap-2">
                  <div className="w-3 h-3 bg-indigo-500 rounded-sm rotate-45" />
                  Vylos
                </span>
                <div className="hidden md:flex items-center gap-6 text-sm font-medium text-zinc-400">
                  <button className="text-white">Overview</button>
                  <button className="hover:text-white transition-colors">Integrations</button>
                  <button className="hover:text-white transition-colors">Settings</button>
                </div>
             </div>
             <div className="flex items-center gap-4">
               <button onClick={handleLogout} className="flex items-center gap-2 text-xs font-medium text-zinc-400 hover:text-red-400 transition-colors px-3 py-1.5 rounded-full border border-transparent hover:border-red-400/20 hover:bg-red-400/10">
                 <LogOut size={14} />
                 Sign Out
               </button>
               <div className="w-8 h-8 rounded-full bg-zinc-800 border border-white/10 flex items-center justify-center text-xs font-medium">
                 U
               </div>
             </div>
         </div>
      </nav>

      <main className="relative z-10 pt-28 px-6 max-w-7xl mx-auto pb-20">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-end mb-10 gap-4">
          <div>
             <h1 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400 mb-2">
               Overview
             </h1>
             <p className="text-zinc-500">Manage your projects and deployments.</p>
          </div>
          <button 
            onClick={() => router.push('/deploy')}
            className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-semibold text-sm hover:bg-zinc-200 transition-colors shadow-[0_0_20px_rgba(255,255,255,0.15)]"
          >
            <Plus size={16} />
            New Project
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
          <StatCard 
            label="Active Projects" 
            value={projects.length.toString().padStart(2, '0')} 
            icon={Layout} 
          />
          <StatCard 
            label="Live Projects" 
            value={projects.filter(p => p.status === 'Live').length.toString().padStart(2, '0')} 
            icon={Activity} 
            trend={`${projects.filter(p => p.status === 'Live').length} live`} 
          />
          <StatCard 
            label="Building" 
            value={projects.filter(p => p.status === 'Building').length.toString().padStart(2, '0')} 
            icon={Terminal} 
          />
        </div>
        
        {/* Projects Grid */}
        <div className="mb-6 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Your Projects</h2>
            <button 
              onClick={fetchProjects} 
              className="text-sm text-zinc-500 hover:text-white transition-colors flex items-center gap-1"
            >
              {loadingProjects ? <Loader2 size={14} className="animate-spin" /> : null}
              Refresh
            </button>
        </div>

        {loadingProjects && projects.length === 0 ? (
          <div className="flex items-center justify-center py-20 text-zinc-500">
            <Loader2 size={24} className="animate-spin mr-2" />
            Loading projects...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Create New - Special Card */}
            <button 
              onClick={() => router.push('/deploy')}
              className="group relative flex flex-col items-center justify-center p-6 rounded-xl border border-dashed border-zinc-700 bg-zinc-900/20 hover:bg-zinc-900/40 hover:border-indigo-500/50 transition-all h-[200px]"
            >
                <div className="p-3 rounded-full bg-zinc-800 group-hover:bg-indigo-500/20 group-hover:text-indigo-400 text-zinc-400 mb-3 transition-colors">
                  <Plus size={24} />
                </div>
                <h3 className="font-semibold text-zinc-300 group-hover:text-white">Create New Project</h3>
                <p className="text-sm text-zinc-500 mt-1">Import from GitHub</p>
            </button>

            {/* Real Projects */}
            {projects.map((project) => (
              <ProjectCard 
                key={project.id} 
                project={project}
                onClick={() => router.push(`/projects/${project.id}`)}
              />
            ))}
            
            {projects.length === 0 && (
              <div className="col-span-2 text-center py-12 text-zinc-500">
                <Terminal size={48} className="mx-auto mb-4 opacity-50" />
                <p>No projects yet. Create your first one!</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}