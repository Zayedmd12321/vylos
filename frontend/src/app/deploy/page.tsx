"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/api";
import { 
  ArrowLeft,
  Github,
  GitBranch,
  Loader2,
  CheckCircle2,
  XCircle,
  Terminal,
  Globe,
  ExternalLink,
  Rocket,
  Clock,
  Activity
} from "lucide-react";
import { DottedGlowBackground } from "@/components/ui/DottedGlowBackground";
import  { Navbar } from "@/components/layout/Navbar";

interface DeploymentLog {
  timestamp: string;
  message: string;
  type: "info" | "success" | "error";
}

interface Project {
  id: number;
  name: string;
  status: string;
  domain?: string;
  repo_url: string;
  last_deployed_at?: string;
  build_logs?: string;
}

export default function DeployPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Form state
  const [gitUrl, setGitUrl] = useState("");
  const [projectId, setProjectId] = useState("");
  const [branch, setBranch] = useState("main");
  
  // Deployment state
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState<"idle" | "deploying" | "success" | "failed">("idle");
  const [logs, setLogs] = useState<DeploymentLog[]>([]);
  const [deployedUrl, setDeployedUrl] = useState<string>("");
  
  // Polling state
  const [projectData, setProjectData] = useState<Project | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const token = Cookies.get("token");
    if (!token) {
      router.push("/login");
    } else {
      setIsAuthenticated(true);
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const addLog = (message: string, type: DeploymentLog["type"] = "info") => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      message,
      type
    }]);
  };

  const pollProjectStatus = async (projectName: string) => {
    try {
      const { data } = await api.get("/projects");
      const project = data.find((p: Project) => p.name === projectName);
      
      if (project) {
        setProjectData(project);
        
        // Fetch real build logs if available
        if (project.id) {
          try {
            const logsResponse = await api.get(`/projects/${project.id}/logs`);
            const realLogs = logsResponse.data.logs;
            
            if (realLogs && realLogs !== "No logs available yet.") {
              // Parse logs and update state
              const logLines = realLogs.split('\n').filter((line: string) => line.trim());
              const newLogs = logLines.map((line: string) => {
                let type: "info" | "success" | "error" = "info";
                if (line.includes('✅') || line.includes('SUCCESS') || line.includes('completed')) {
                  type = "success";
                } else if (line.includes('❌') || line.includes('ERROR') || line.includes('failed') || line.includes('error')) {
                  type = "error";
                }
                
                return {
                  timestamp: new Date().toLocaleTimeString(),
                  message: line,
                  type
                };
              });
              
              setLogs(newLogs);
            }
          } catch (logError) {
            console.error("Error fetching logs:", logError);
          }
        }
        
        if (project.status === "Live") {
          addLog("✅ Deployment completed successfully!", "success");
          addLog(`🌐 Your app is live at: ${project.domain}`, "success");
          setDeployedUrl(`http://${project.domain}`);
          setDeploymentStatus("success");
          setIsDeploying(false);
          
          if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
          }
        } else if (project.status === "Failed") {
          addLog("❌ Deployment failed. Please check the logs.", "error");
          setDeploymentStatus("failed");
          setIsDeploying(false);
          
          if (pollingInterval) {
            clearInterval(pollingInterval);
            setPollingInterval(null);
          }
        } else if (project.status === "Building") {
          addLog(`⚙️ Building... Status: ${project.status}`, "info");
        }
      }
    } catch (error) {
      console.error("Error polling project status:", error);
    }
  };

  const handleDeploy = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!gitUrl || !projectId) {
      addLog("❌ Please fill in all required fields", "error");
      return;
    }

    setIsDeploying(true);
    setDeploymentStatus("deploying");
    setLogs([]);
    setDeployedUrl("");
    setProjectData(null);

    try {
      // Initial deployment request
      addLog("🚀 Initiating deployment...", "info");
      
      const { data } = await api.post("/deploy", {
        git_url: gitUrl,
        project_id: projectId
      });

      addLog(`✓ ${data.message}`, "success");
      
      // Connect to SSE for real-time logs
      const token = Cookies.get("token");
      const sseUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/logs/stream/${projectId}?token=${token}`;
      
      addLog("📡 Connecting to build stream...", "info");
      
      const eventSource = new EventSource(sseUrl);
      
      eventSource.onopen = () => {
        console.log("SSE connection opened");
        addLog("✓ Connected to build stream", "success");
      };
      
      eventSource.onmessage = (event) => {
        try {
          const eventData = JSON.parse(event.data);
          console.log("SSE event:", eventData);
          
          if (eventData.type === 'connected') {
            addLog(eventData.message, "success");
          } else if (eventData.type === 'log') {
            addLog(eventData.message, "info");
          } else if (eventData.type === 'status') {
            setProjectData({
              id: 0,
              name: projectId,
              status: eventData.status,
              domain: eventData.domain,
              repo_url: gitUrl,
              last_deployed_at: new Date().toISOString()
            });
          } else if (eventData.type === 'complete') {
            if (eventData.status === 'Live') {
              addLog("✅ Deployment completed successfully!", "success");
              addLog(`🌐 Your app is live at: ${eventData.domain}`, "success");
              setDeployedUrl(eventData.url);
              setDeploymentStatus("success");
            } else {
              addLog("❌ Deployment failed", "error");
              setDeploymentStatus("failed");
            }
            setIsDeploying(false);
            eventSource.close();
          } else if (eventData.type === 'timeout') {
            addLog("⏱️ Deployment is taking longer than expected (15 min limit)", "error");
            addLog("💡 Tip: Check your dashboard - the deployment might still complete", "info");
            setDeploymentStatus("failed");
            setIsDeploying(false);
            eventSource.close();
          } else if (eventData.type === 'error') {
            addLog(`❌ ${eventData.message}`, "error");
            setDeploymentStatus("failed");
            setIsDeploying(false);
            eventSource.close();
          }
        } catch (err) {
          console.error("Error parsing SSE:", err, event.data);
        }
      };
      
      eventSource.onerror = (error) => {
        console.error("SSE error:", error);
        
        // Don't immediately fail - the build might still be running
        setTimeout(() => {
          if (deploymentStatus === "deploying") {
            addLog("⚠️ Connection interrupted, but deployment may still be running", "error");
            addLog("💡 Check your dashboard in a moment to see the final status", "info");
            setIsDeploying(false);
            setDeploymentStatus("failed");
            eventSource.close();
          }
        }, 3000);
      };
      
    } catch (error: any) {
      addLog(`❌ Deployment failed: ${error.response?.data?.detail || error.message}`, "error");
      setDeploymentStatus("failed");
      setIsDeploying(false);
    }
  };

  const handleReset = () => {
    setDeploymentStatus("idle");
    setLogs([]);
    setDeployedUrl("");
    setProjectData(null);
    setGitUrl("");
    setProjectId("");
    setBranch("main");
    
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <Loader2 className="animate-spin" size={32} />
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-black text-white">
      <DottedGlowBackground dotColor="rgba(100, 100, 100, 0.15)" glowColor="rgba(100, 100, 255, 0.4)" />
      
      <Navbar />

      <main className="relative z-10 pt-28 px-6 max-w-6xl mx-auto pb-20">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-zinc-400 mb-3">
            Deploy New Project
          </h1>
          <p className="text-zinc-500">Import your project from GitHub and deploy it instantly.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Form */}
          <div className="space-y-6">
            {/* Configuration Card */}
            <div className="p-6 rounded-xl border border-white/8 bg-zinc-900/50 backdrop-blur-sm">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Rocket size={20} className="text-indigo-400" />
                Configuration
              </h2>
              
              <form onSubmit={handleDeploy} className="space-y-5">
                {/* Git URL */}
                <div>
                  <label className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                    <Github size={16} />
                    Git Repository URL
                  </label>
                  <input
                    type="url"
                    value={gitUrl}
                    onChange={(e) => setGitUrl(e.target.value)}
                    placeholder="https://github.com/username/repo.git"
                    disabled={isDeploying}
                    className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    required
                  />
                </div>

                {/* Project ID */}
                <div>
                  <label className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                    <Terminal size={16} />
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                    placeholder="my-awesome-project"
                    disabled={isDeploying}
                    className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    required
                  />
                  <p className="text-xs text-zinc-500 mt-1.5">Lowercase letters, numbers, and hyphens only</p>
                </div>

                {/* Branch */}
                <div>
                  <label className="text-sm font-medium text-zinc-300 mb-2 flex items-center gap-2">
                    <GitBranch size={16} />
                    Branch
                  </label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    placeholder="main"
                    disabled={isDeploying}
                    className="w-full px-4 py-3 rounded-lg bg-black/50 border border-white/10 text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Deploy Button */}
                <button
                  type="submit"
                  disabled={isDeploying || deploymentStatus === "success"}
                  className="w-full py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold flex items-center justify-center gap-2 hover:from-indigo-600 hover:to-purple-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                >
                  {isDeploying ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Deploying...
                    </>
                  ) : deploymentStatus === "success" ? (
                    <>
                      <CheckCircle2 size={18} />
                      Deployed Successfully
                    </>
                  ) : (
                    <>
                      <Rocket size={18} />
                      Deploy Project
                    </>
                  )}
                </button>

                {/* Reset Button */}
                {(deploymentStatus === "success" || deploymentStatus === "failed") && (
                  <button
                    type="button"
                    onClick={handleReset}
                    className="w-full py-2.5 rounded-lg bg-zinc-800 text-zinc-300 font-medium hover:bg-zinc-700 transition-colors"
                  >
                    Deploy Another Project
                  </button>
                )}
              </form>
            </div>

            {/* Status Card */}
            {projectData && (
              <div className="p-6 rounded-xl border border-white/8 bg-zinc-900/50 backdrop-blur-sm">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Activity size={18} className="text-indigo-400" />
                  Project Status
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-zinc-400">Status</span>
                    <span className={`text-sm font-medium px-3 py-1 rounded-full ${
                      projectData.status === "Live" 
                        ? "bg-emerald-500/20 text-emerald-400" 
                        : projectData.status === "Building"
                        ? "bg-amber-500/20 text-amber-400"
                        : "bg-red-500/20 text-red-400"
                    }`}>
                      {projectData.status}
                    </span>
                  </div>
                  {projectData.domain && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-zinc-400">Domain</span>
                      <a 
                        href={`http://${projectData.domain}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                      >
                        {projectData.domain}
                        <ExternalLink size={12} />
                      </a>
                    </div>
                  )}
                  {projectData.last_deployed_at && (
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-zinc-400">Last Deployed</span>
                      <span className="text-sm text-zinc-300 flex items-center gap-1">
                        <Clock size={12} />
                        {new Date(projectData.last_deployed_at).toLocaleString()}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Logs */}
          <div className="space-y-6">
            {/* Logs Card */}
            <div className="p-6 rounded-xl border border-white/8 bg-zinc-900/50 backdrop-blur-sm">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Terminal size={20} className="text-indigo-400" />
                Deployment Logs
              </h2>
              
              <div className="bg-black/70 rounded-lg p-4 font-mono text-sm h-[500px] overflow-y-auto border border-white/5">
                {logs.length === 0 ? (
                  <div className="text-zinc-600 text-center py-8">
                    <Terminal size={32} className="mx-auto mb-2 opacity-50" />
                    <p>No logs yet. Start a deployment to see logs here.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {logs.map((log, index) => (
                      <div 
                        key={index}
                        className={`flex gap-3 ${
                          log.type === "success" 
                            ? "text-emerald-400" 
                            : log.type === "error"
                            ? "text-red-400"
                            : "text-zinc-400"
                        }`}
                      >
                        <span className="text-zinc-600 min-w-[80px]">[{log.timestamp}]</span>
                        <span>{log.message}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Success Card with URL */}
            {deployedUrl && (
              <div className="p-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 backdrop-blur-sm">
                <div className="flex items-start gap-3 mb-4">
                  <CheckCircle2 size={24} className="text-emerald-400 mt-0.5" />
                  <div>
                    <h3 className="text-lg font-semibold text-emerald-400 mb-1">Deployment Successful! 🎉</h3>
                    <p className="text-sm text-zinc-400">Your project is now live and accessible.</p>
                  </div>
                </div>
                
                <div className="bg-black/30 rounded-lg p-4 border border-emerald-500/20">
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2 text-emerald-400 min-w-0">
                      <Globe size={18} className="shrink-0" />
                      <span className="font-mono text-sm truncate">{deployedUrl}</span>
                    </div>
                    <a
                      href={deployedUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition-colors shrink-0"
                    >
                      Visit Site
                      <ExternalLink size={16} />
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Error Card */}
            {deploymentStatus === "failed" && (
              <div className="p-6 rounded-xl border border-red-500/30 bg-red-500/10 backdrop-blur-sm">
                <div className="flex items-start gap-3">
                  <XCircle size={24} className="text-red-400 mt-0.5" />
                  <div>
                    <h3 className="text-lg font-semibold text-red-400 mb-1">Deployment Failed</h3>
                    <p className="text-sm text-zinc-400">Please check the logs above for more details. Common issues:</p>
                    <ul className="text-sm text-zinc-400 mt-2 space-y-1 list-disc list-inside">
                      <li>Invalid repository URL</li>
                      <li>Build script errors</li>
                      <li>Missing dependencies</li>
                      <li>Project name already taken</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
