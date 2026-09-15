import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid,
  BarChart, Bar, Legend
} from "recharts";
import { AlertTriangle, CheckCircle, ShieldAlert, Cpu, Activity, Database } from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [summary, setSummary] = useState(null);
  const [mspc, setMspc] = useState(null);
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/summary`).then(r => r.json()),
      fetch(`${API_URL}/api/analytics/mspc?limit=100`).then(r => r.json()),
      fetch(`${API_URL}/api/analytics/models`).then(r => r.json())
    ])
      .then(([sumData, mspcData, modelData]) => {
        setSummary(sumData);
        setMspc(mspcData);
        setModels(modelData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error conectando a la API:", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-200">
        <Activity className="h-8 w-8 animate-spin text-cyan-400 mr-3" />
        <span className="text-lg font-medium">Cargando analitica farmaceutica multivariante...</span>
      </div>
    );
  }

  const modelMetricsData = models ? [
    { metric: "Recall (Desvio)", RF: (models.RandomForest.recall * 100).toFixed(1), LR: (models.LogisticRegression.recall * 100).toFixed(1) },
    { metric: "F1-Score", RF: (models.RandomForest.f1 * 100).toFixed(1), LR: (models.LogisticRegression.f1 * 100).toFixed(1) },
    { metric: "Precision", RF: (models.RandomForest.precision * 100).toFixed(1), LR: (models.LogisticRegression.precision * 100).toFixed(1) },
    { metric: "AUC-ROC", RF: (models.RandomForest.auc * 100).toFixed(1), LR: (models.LogisticRegression.auc * 100).toFixed(1) }
  ] : [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="border-b border-slate-800 pb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Cpu className="text-cyan-400" />
            Sistema de Analitica y Calidad en Fabricacion de Tabletas
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Control Estadistico Multivariante (MSPC) y Modelos Predictivos Lote a Lote
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-700 text-xs text-slate-300">
          <Database className="h-4 w-4 text-emerald-400" />
          <span>Base de datos: <strong>SQLite (1.005 lotes)</strong></span>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="text-sm text-slate-400">Lotes Analizados</div>
          <div className="text-3xl font-semibold mt-2 text-white">{summary?.total_batches || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Historico 2018-2021</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="text-sm text-slate-400">Lotes Conformes</div>
          <div className="text-3xl font-semibold mt-2 text-emerald-400 flex items-center justify-between">
            {summary?.compliant || 0}
            <CheckCircle className="h-6 w-6 text-emerald-500/80" />
          </div>
          <div className="text-xs text-slate-500 mt-1">Cumplen CPPs y CQAs</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="text-sm text-slate-400">Lotes con Desviacion</div>
          <div className="text-3xl font-semibold mt-2 text-amber-400 flex items-center justify-between">
            {summary?.deviations || 0}
            <AlertTriangle className="h-6 w-6 text-amber-500/80" />
          </div>
          <div className="text-xs text-slate-500 mt-1">Fuera de especificacion</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="text-sm text-slate-400">Tasa de Desviacion</div>
          <div className="text-3xl font-semibold mt-2 text-rose-400 flex items-center justify-between">
            {summary?.deviation_rate || 0}%
            <ShieldAlert className="h-6 w-6 text-rose-500/80" />
          </div>
          <div className="text-xs text-slate-500 mt-1">Impacto en OEE y calidad</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Carta de Control Hotelling T2</h2>
              <p className="text-xs text-slate-400">Distancia multivariante en espacio de componentes principales</p>
            </div>
            <span className="text-xs px-2.5 py-1 bg-cyan-950 text-cyan-300 rounded border border-cyan-800">
              UCL: {mspc?.t2_ucl}
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mspc?.chart_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="batch_code" hide />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155" }} />
                <ReferenceLine y={mspc?.t2_ucl} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: "UCL", fill: "#f43f5e", fontSize: 10 }} />
                <Line type="monotone" dataKey="t2" stroke="#38bdf8" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Carta de Residuos SPE (Q-Residuals)</h2>
              <p className="text-xs text-slate-400">Varianza residual no explicada por el modelo multivariante</p>
            </div>
            <span className="text-xs px-2.5 py-1 bg-amber-950 text-amber-300 rounded border border-amber-800">
              UCL: {mspc?.spe_ucl}
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mspc?.chart_data || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="batch_code" hide />
                <YAxis stroke="#64748b" />
                <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155" }} />
                <ReferenceLine y={mspc?.spe_ucl} stroke="#fbbf24" strokeDasharray="4 4" label={{ value: "UCL", fill: "#fbbf24", fontSize: 10 }} />
                <Line type="monotone" dataKey="spe" stroke="#e2e8f0" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5">
        <h2 className="text-lg font-semibold text-slate-100">
          Comparativa de Modelos de Clasificacion Supervisada
        </h2>
        <p className="text-xs text-slate-400 mb-4">
          Validacion cruzada estratificada (5-Fold CV) priorizando Recall y F1 en la clase critica (Desviacion).
        </p>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={modelMetricsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="metric" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} unit="%" />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155" }} />
              <Legend />
              <Bar dataKey="RF" name="Random Forest (Balanced)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="LR" name="Regresion Logistica" fill="#818cf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
