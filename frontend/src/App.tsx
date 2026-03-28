import { useEffect, useState } from "react";
import { getConceptMap } from "./api/client";
import { History } from "./pages/History";
import { Home } from "./pages/Home";
import { SettingsPage } from "./pages/SettingsPage";
import type { ConceptMap } from "./types";

type TabId = "home" | "history" | "map" | "settings";

const tabs: Array<{ id: TabId; label: string; subtitle: string }> = [
  { id: "home", label: "ホーム", subtitle: "今日の 3 アイデア" },
  { id: "history", label: "履歴", subtitle: "過去の候補" },
  { id: "map", label: "マップ", subtitle: "概念のつながり" },
  { id: "settings", label: "設定", subtitle: "重みとプロバイダ" },
];

const emptyMap: ConceptMap = { nodes: [], edges: [] };

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>("home");
  const [visitedTabs, setVisitedTabs] = useState<TabId[]>(["home"]);
  const [conceptMap, setConceptMap] = useState<ConceptMap>(emptyMap);
  const [mapStatus, setMapStatus] = useState("概念マップはまだ読み込まれていません。");

  useEffect(() => {
    if (activeTab !== "map") {
      return;
    }

    void loadConceptMap();
  }, [activeTab]);

  const activeTabMeta = tabs.find((tab) => tab.id === activeTab) ?? tabs[0];

  const handleTabChange = (tab: TabId) => {
    setActiveTab(tab);
    setVisitedTabs((current) => (current.includes(tab) ? current : [...current, tab]));
  };

  const loadConceptMap = async () => {
    try {
      setMapStatus("概念マップを読み込んでいます...");
      const nextMap = await getConceptMap();
      setConceptMap(nextMap);
      setMapStatus(
        nextMap.nodes.length > 0
          ? `${nextMap.nodes.length} ノード / ${nextMap.edges.length} エッジを取得しました。`
          : "概念マップはまだ空です。",
      );
    } catch (error) {
      setMapStatus(error instanceof Error ? error.message : "概念マップの取得に失敗しました。");
    }
  };

  return (
    <div className="min-h-screen px-4 py-6 text-slate-100 sm:px-6 lg:px-10">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-7xl flex-col rounded-[2rem] border border-white/10 bg-slate-950/70 shadow-glow backdrop-blur">
        <header className="border-b border-white/10 px-6 py-6 sm:px-8">
          <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
            <div>
              <p className="mb-3 text-xs uppercase tracking-[0.34em] text-cyan-300/70">
                Auto Idea Combiner
              </p>
              <h1 className="text-3xl font-semibold text-white">
                発想の距離を調整するアイデアワークベンチ
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
                遠すぎず近すぎない組み合わせを毎日 3 件提示し、フィードバックから次の生成を磨きます。
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-sm text-cyan-50">
              <div className="font-medium">{activeTabMeta.label}</div>
              <div className="text-cyan-100/70">{activeTabMeta.subtitle}</div>
            </div>
          </div>

          <nav className="mt-6 flex flex-wrap gap-2">
            {tabs.map((tab) => {
              const isActive = tab.id === activeTab;

              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => handleTabChange(tab.id)}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                    isActive
                      ? "bg-cyan-400 text-slate-950"
                      : "border border-slate-700 bg-slate-900/70 text-slate-300 hover:border-cyan-400/40 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </header>

        <main className="flex-1 px-6 py-6 sm:px-8">
          {visitedTabs.includes("home") ? (
            <section className={activeTab === "home" ? "block" : "hidden"}>
              <Home />
            </section>
          ) : null}

          {visitedTabs.includes("history") ? (
            <section className={activeTab === "history" ? "block" : "hidden"}>
              <History />
            </section>
          ) : null}

          {visitedTabs.includes("map") ? (
            <section className={activeTab === "map" ? "block space-y-5" : "hidden"}>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-semibold text-white">概念マップ</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    可視化本体は後続工程向けのプレースホルダです。API のノード数だけ先に確認できます。
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => void loadConceptMap()}
                  className="rounded-full border border-slate-700 bg-slate-900/80 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-cyan-400/40 hover:text-white"
                >
                  再取得
                </button>
              </div>

              <div className="grid gap-5 lg:grid-cols-[1.4fr_0.8fr]">
                <div className="flex min-h-[360px] items-center justify-center rounded-[2rem] border border-dashed border-cyan-400/20 bg-slate-900/60 p-6">
                  <div className="max-w-md text-center">
                    <p className="mb-3 text-xs uppercase tracking-[0.3em] text-cyan-300/70">
                      Placeholder
                    </p>
                    <h3 className="text-xl font-semibold text-white">概念グラフ表示エリア</h3>
                    <p className="mt-3 text-sm leading-6 text-slate-400">
                      今後ここにネットワーク図を載せます。現状はバックエンドから取得した件数だけ表示します。
                    </p>
                  </div>
                </div>

                <div className="space-y-4 rounded-[2rem] border border-white/10 bg-slate-900/70 p-5">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                    <p className="text-sm text-slate-400">状態</p>
                    <p className="mt-2 text-sm leading-6 text-slate-200">{mapStatus}</p>
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
                    <StatCard label="ノード数" value={String(conceptMap.nodes.length)} />
                    <StatCard label="エッジ数" value={String(conceptMap.edges.length)} />
                  </div>
                </div>
              </div>
            </section>
          ) : null}

          {visitedTabs.includes("settings") ? (
            <section className={activeTab === "settings" ? "block" : "hidden"}>
              <SettingsPage />
            </section>
          ) : null}
        </main>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-white">{value}</p>
    </div>
  );
}
