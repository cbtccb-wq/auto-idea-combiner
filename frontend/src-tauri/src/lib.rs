use std::net::TcpStream;
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::{Duration, Instant};
use tauri::{Manager, State};

const BACKEND_PORT: u16 = 8765;
const STARTUP_TIMEOUT_SECS: u64 = 30;

pub struct BackendProcess(Mutex<Option<Child>>);

/// uvicorn が既に動いているか TCP で確認
fn is_backend_alive() -> bool {
    TcpStream::connect(("127.0.0.1", BACKEND_PORT)).is_ok()
}

/// backend ディレクトリのパスを解決する
/// - 開発時: <project_root>/backend
/// - 本番時: 実行ファイルの隣に backend/ を配置している想定
fn resolve_backend_dir(app: &tauri::AppHandle) -> std::path::PathBuf {
    // 本番バンドル内のリソースパスを試みる
    if let Ok(resource) = app.path().resource_dir() {
        let candidate = resource.join("backend");
        if candidate.exists() {
            return candidate;
        }
    }
    // 開発時: src-tauri の 2階層上 → プロジェクトルート/backend
    let manifest = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    manifest
        .parent() // frontend/
        .and_then(|p| p.parent()) // project root
        .map(|p| p.join("backend"))
        .unwrap_or_else(|| manifest.join("../../backend"))
}

/// バックエンドプロセスを起動し、起動完了まで待つ
fn start_backend(app: &tauri::AppHandle) -> Option<Child> {
    if is_backend_alive() {
        println!("[AIC] Backend already running on port {BACKEND_PORT}");
        return None; // 管理不要（外部起動済み）
    }

    let backend_dir = resolve_backend_dir(app);
    println!("[AIC] Starting backend in: {}", backend_dir.display());

    let child = Command::new("uv")
        .args(["run", "uvicorn", "main:app", "--port", &BACKEND_PORT.to_string()])
        .current_dir(&backend_dir)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();

    match child {
        Ok(child) => {
            // 起動完了まで待機
            let deadline = Instant::now() + Duration::from_secs(STARTUP_TIMEOUT_SECS);
            while Instant::now() < deadline {
                if is_backend_alive() {
                    println!("[AIC] Backend ready on port {BACKEND_PORT}");
                    return Some(child);
                }
                std::thread::sleep(Duration::from_millis(500));
            }
            println!("[AIC] Backend startup timed out");
            Some(child) // タイムアウトしても参照は保持（後でkill）
        }
        Err(e) => {
            println!("[AIC] Failed to start backend: {e}");
            None
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(BackendProcess(Mutex::new(None)))
        .setup(|app| {
            // メインウィンドウを初期状態で非表示にして、バックエンド起動後に表示
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.hide();
            }

            let handle = app.handle().clone();
            let state: State<BackendProcess> = app.state();

            // バックエンド起動（同期: setup内で完結させる）
            let child = start_backend(&handle);
            *state.0.lock().unwrap() = child;

            // ウィンドウを表示
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                // 最後のウィンドウが閉じたらバックエンドを終了
                let state: State<BackendProcess> = window.state();
                if let Ok(mut guard) = state.0.lock() {
                    if let Some(mut child) = guard.take() {
                        let _ = child.kill();
                        println!("[AIC] Backend process terminated");
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
